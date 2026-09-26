# frontend_ws_api.md — Live2D 数字人前端（mate-human）WebSocket 接口文档

> 本文档基于 `CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src` 源码分析得出，
> 描述前端（浏览器端 Live2D 渲染）对后端 Fay 服务的能力要求。

---

## WebSocket 连接信息（端口、握手方式、心跳机制）

| 项 | 值 |
|---|---|
| 连接地址 | `ws://127.0.0.1:10002`（[lappmodel.ts:1538](file:///d:/codes/fay/mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src/lappmodel.ts#L1538)） |
| 协议 | WebSocket，消息体为 JSON 文本帧 |
| 默认用户名 | `User`（Fay 默认用户名） |

### 握手方式

连接建立（`onopen`）后，前端立即发送一条**注册消息**（[fayclient.ts:78-81](file:///d:/codes/fay/mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src/fayclient.ts#L78-L81)）：

```json
{
  "Username": "User",
  "Output": true
}
```

- `Username`：当前用户身份标识。
- `Output`：`true` 表示开启（文本/音频）输出推送。
- 后端收到后即开始向该连接推送消息；前端不等待握手响应即可接收数据。

### 心跳机制

- **无 WebSocket 应用层心跳**：代码中没有向服务端发送 ping/pong 或定时保活消息。
- 前端存在一个本地每秒一次的 `heartbeat` 定时器（[lappmodel.ts:1687-1691](file:///d:/codes/fay/mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src/lappmodel.ts#L1687-L1691)），仅用于在浏览器拦截自动播放后恢复音频队列，**与 WebSocket 保活无关**。
- **断线重连**：连接关闭或创建失败后自动重连，指数退避 `min(1000 * 2^n, 30000)` ms，最多 5 次（[fayclient.ts:123-143](file:///d:/codes/fay/mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src/fayclient.ts#L123-L143)）。

---

## 音频数据格式（采样率、编码方式、帧大小）

### 网页端播放入口（Fay 语音）

- 前端**不解析音频字节**，而是通过浏览器 `<audio>` 元素播放：`new Audio(HttpValue)`（[lappmodel.ts:1326](file:///d:/codes/fay/mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src/lappmodel.ts#L1326)）。
- 因此后端只要求：
  - `Data.HttpValue` 返回一个**浏览器可直接播放的音频 URL**（HTTP/HTTPS，可跨域），格式不限（MP3/WAV 等浏览器支持即可）。
  - URL 需支持前端直接 GET 拉取并播放（`preload='auto'`，`volume=1.0`）。
- **采样率 / 编码 / 帧大小：前端无硬性要求**，由浏览器解码器决定。文档备注：若沿用 Fay 惯例，后端一般输出 16kHz 单声道 WAV，但代码层面未校验。

### 模型自带动作配音（本地 WAV，与 Fay 语音无关）

`lappwavfilehandler.ts` 解析模型动作附带的配音 WAV，要求 **RIFF WAVE 线性 PCM**：

| 项 | 要求 |
|---|---|
| 格式 | 线性 PCM（format id = 1） |
| 采样位宽 | 8 / 16 / 24 bit |
| 声道数 | 任意（解析为多通道 Float32Array） |
| 采样率 | 任意（解析后用于按时间推进 RMS 计算） |

---

## 表情控制指令（表情列表、参数名、指令格式）

表情通过消息的 `Data.Action.affect` 语义字段映射，或通过 `Data.Sentiment` 情感值兜底映射。

### 指令格式（优先）

```json
"Data": {
  "Action": { "code": "...", "behavior": "nod", "affect": "smile", "intensity": 0.5 }
}
```

- `Action.affect` → 表情 ID（`live2d-action-map.ts` `affectExpressions`）：

| affect 值 | 表情 ID | 含义 |
|---|---|---|
| `smile` / `warm` / `neutral` | `F01` | 微笑 / 温暖 / 中性 |
| `serious` | `F02` | 严肃 |
| `sorry` / `sad` | `F03` | 抱歉 / 悲伤 |
| `curious` / `surprised` / `excited` | `F04` | 好奇 / 惊讶 / 兴奋 |

### 兜底：情感值 → 表情（`setExpressionBySentiment`，[lappmodel.ts:1701-1727](file:///d:/codes/fay/mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src/lappmodel.ts#L1701-L1727)）

| Sentiment 范围 | 表情 ID |
|---|---|
| `>= 1` | `F04`（惊喜） |
| `> 0.3` | `F01`（微笑） |
| `< -0.7` | `F03`（悲伤） |
| `< -0.3` | `F02`（生气） |
| 其余 | `F01`（默认微笑） |

### 对话结束复位

`Data.IsEnd === 1` 时前端恢复 `F01` 表情（[lappmodel.ts:1651-1660](file:///d:/codes/fay/mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src/lappmodel.ts#L1651-L1660)）。

---

## 口型同步参数（参数名、取值范围）

### 驱动方式

后端在播放音频的**同时**发送 `Data.Lips` 口型序列，前端按时间戳驱动 Live2D 模型参数 **`ParamMouthOpenY`**（绝对赋值，范围 0~1，[lappmodel.ts:1524-1535](file:///d:/codes/fay/mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src/lappmodel.ts#L1524-L1535)）。

### 数据结构

`Data.Lips` 为 viseme 数组，每项 `{ Lip: string; Time: number }`：

| 字段 | 类型 | 含义 |
|---|---|---|
| `Lip` | string | OVR LipSync 15 种 viseme 音素名（见下表） |
| `Time` | number | 该音素持续时长，**单位毫秒** |

- 总时长 = 所有 `Time` 之和，前端据此推算播放进度。
- 无口型数据时嘴部平滑回归闭合（0）。

### viseme → 嘴巴开合度映射表（`lipsync.ts` `visemeMap`）

| viseme | 开合度 | 发音特征 |
|---|---|---|
| `sil` | 0.0 | 静音 |
| `PP` | 0.2 | 双唇闭合 |
| `FF` | 0.3 | 下唇咬上齿 |
| `TH` | 0.4 | 舌尖抵上下齿 |
| `DD` | 0.5 | 舌尖抵上齿 |
| `kk` | 0.6 | 舌根抵软腭 |
| `CH` | 0.5 | 硬腭 |
| `SS` | 0.4 | 舌尖接近上齿 |
| `nn` | 0.3 | 舌尖抵上齿龈 |
| `RR` | 0.4 | 舌尖卷曲 |
| `aa` | 0.9 | 张嘴，低元音 |
| `E` | 0.6 | 微张，前元音 |
| `ih` | 0.5 | 半张，前高元音 |
| `oh` | 0.7 | 圆唇，后元音 |
| `ou` | 0.8 | 圆唇突出，后高元音 |

- 取值区间：`0.0`（闭合）~ `0.9`（最大张开）。
- 前端平滑因子 0.3（越小越平滑），未知 viseme 按 `sil`（0.0）处理。

---

## 文字内容（是否需要、显示格式）

- **必须提供**：`Data.Text` 在接口定义中为必填字符串（[fayclient.ts:26](file:///d:/codes/fay/mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src/fayclient.ts#L26)），每段音频消息都带当前语句文本。
- **显示方式**：前端**不渲染文字**（无字幕/对话气泡 UI）。`Text` 仅用于：
  1. 日志输出（每段音频入队/出队时打印）。
  2. 音频分片与内容的关联标识。
- 建议后端仍按句子/分片附带文本，便于前端调试与后续扩展显示。

---

## 完整的消息格式示例（一条完整的 WebSocket 消息长什么样）

`FayMessage` 完整字段定义见 [fayclient.ts:21-41](file:///d:/codes/fay/mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src/fayclient.ts#L21-L41)。

### 字段总表

| 字段 | 类型 | 必填 | 含义 |
|---|---|---|---|
| `Topic` | string | 是 | 消息主题/分类 |
| `Data.Key` | string | 是 | 数据类型标识，**音频消息必须为 `"audio"`** |
| `Data.Value` | string | 否 | 附加值 |
| `Data.HttpValue` | string | 否 | 音频 URL（浏览器直接播放；无 URL 则仅做口型同步） |
| `Data.Text` | string | 是 | 当前语句文本（仅日志/关联用） |
| `Data.Time` | number | 否 | 时间信息 |
| `Data.Type` | string | 否 | 类型 |
| `Data.IsFirst` | number | 是 | 是否为一段语音流的首帧（`1` 是 / `0` 否） |
| `Data.IsEnd` | number | 是 | 是否为一段语音流的末帧（`1` 是 / `0` 否） |
| `Data.Lips` | array | 否 | 口型序列 `[{Lip, Time}]`，见"口型同步参数" |
| `Data.Sentiment` | number | 否 | 情感值，范围 `-2 ~ +2`（负=消极，正=积极） |
| `Data.MotionNo` | number | 否 | 旧式动作编号（1 起始，按组内下标 `no-1` 播放） |
| `Data.MotionGroup` | string | 否 | 动作组名，默认 `TapBody` |
| `Data.Action` | object | 否 | 语义动作 `{code, behavior?, affect?, intensity?, priority?, matchedKeywords?, sentimentHint?}` |
| `Username` | string | 是 | 用户名（默认 `User`） |
| `robot` | string | 否 | 机器人标识 |

### 动作编号映射（behavior → TapBody 组 motion 下标）

`live2d-action-map.ts`（Lisette 模型）：

| behavior | motion 下标 | 动作名 |
|---|---|---|
| `celebrate` | 0 | jump_ani |
| `wave` | 1 | hello_ani |
| `sad` | 2 | sad_idle |
| `warn` / `reject` | 3 | angry_idle |
| `surprise` | 4 | frenzy_idle |
| `think` | 5 | hand_fiddle_idle |
| `nod` | 6 | happy_transition |

- 多候选时用 `intensity`（0~1，默认 0.5）取 `round(intensity * (n-1))`。
- 语义动作优先级：`Action.behavior/affect` > 旧式 `MotionNo/MotionGroup` > `Sentiment` 兜底。

### 示例 1：一段带音频+口型+语义动作的语音流首帧

```json
{
  "Topic": "chat",
  "Username": "User",
  "robot": "fay",
  "Data": {
    "Key": "audio",
    "Text": "你好呀，今天有什么可以帮你？",
    "HttpValue": "http://127.0.0.1:5001/tmp/audio/20260810_123456_1.wav",
    "IsFirst": 1,
    "IsEnd": 0,
    "Sentiment": 0.8,
    "Action": {
      "code": "greeting",
      "behavior": "wave",
      "affect": "smile",
      "intensity": 0.5,
      "priority": 2
    },
    "Lips": [
      { "Lip": "sil", "Time": 200 },
      { "Lip": "PP", "Time": 120 },
      { "Lip": "aa", "Time": 180 },
      { "Lip": "ih", "Time": 150 },
      { "Lip": "ou", "Time": 200 },
      { "Lip": "sil", "Time": 150 }
    ]
  }
}
```

### 示例 2：仅带口型（无音频 URL）的中间帧

```json
{
  "Topic": "chat",
  "Username": "User",
  "Data": {
    "Key": "audio",
    "Text": "中间分句",
    "IsFirst": 0,
    "IsEnd": 0,
    "Lips": [
      { "Lip": "E", "Time": 300 },
      { "Lip": "sil", "Time": 100 }
    ]
  }
}
```

### 示例 3：语音流结束帧

```json
{
  "Topic": "chat",
  "Username": "User",
  "Data": {
    "Key": "audio",
    "Text": "说完啦",
    "HttpValue": "http://127.0.0.1:5001/tmp/audio/20260810_123456_9.wav",
    "IsFirst": 0,
    "IsEnd": 1,
    "Sentiment": 0.2,
    "Lips": []
  }
}
```

### 前端播放行为要点

1. `Data.Key !== 'audio'` 的消息直接忽略（不排队播放）。
2. 有 `HttpValue` 才播放音频；只有 `Lips` 时仅驱动口型（[lappmodel.ts:1247-1257](file:///d:/codes/fay/mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo/src/lappmodel.ts#L1247-L1257)）。
3. `IsFirst=1` 开启新语音流：`streamId+1` 并清空播放队列；`IsEnd=1` 表示该流结束。
4. 音频播放成功后才启动口型同步，进度按 `audio.currentTime / audio.duration` 折算到 Lips 总时长。
5. 播放兜底超时 = `max(3000, Lips总时长 + 2500)` ms；被浏览器拦截自动播放时会显示 "Enable Audio" 按钮，等待用户手势后继续。
6. 音频流按 `streamId` 过滤过期分片（新流启动后旧分片丢弃）。

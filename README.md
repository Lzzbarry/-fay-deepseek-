<div align="center">
  <br>
  <img src="fay/readme/icon.png" alt="Fay" width="140">
  <h1>Fay 数字人框架</h1>
  <p>面向终端的开源数字人应用框架 —— 向上适配各种数字人模型，向下接入各式大语言模型</p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4B8BBE" alt="Platform">
    <img src="https://img.shields.io/badge/License-GPL--3.0-blue" alt="License">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs welcome">
  </p>
</div>

## 项目简介

Fay 致力于思考面向终端的数字人落地应用，并通过完整代码把思考结果呈现给大家。

- **向上**：自由匹配 Live2D 数字人模型、大语言模型（OpenAI 兼容接口）、ASR、TTS 模型；
- **向下**：为单片机、App、网站、大屏、三方业务系统提供统一的数字人应用接口。

Fay 只负责“对话、语音、工具调用与记忆”，数字人渲染交给独立的前端工程（见 [mate-human](mate-human)）。上下解耦，便于替换任意一环。

> 更新日志与完整文档见飞书：
> [更新日志](https://qqk9ntwbcit.feishu.cn/wiki/UlbZwfAXgiKSquk52AkcibhHngg) ·
> [中文文档](https://qqk9ntwbcit.feishu.cn/wiki/JzMJw7AghiO8eHktMwlcxznenIg)

## 功能特点

- 完全开源，商用免责
- 支持全离线使用，全时流式
- 自由匹配数字人模型、大语言模型（OpenAI 兼容接口）、ASR、TTS 模型
- 支持数字人自动播报模式（虚拟教师、虚拟主播、新闻播报）
- 支持任意终端接入：单片机、App、网站、大屏、三方业务系统
- 支持多用户、多路并发
- 提供文字交互、语音交互、数字人驱动、管理控制、自动播报、意图等接口
- 支持语音指令灵活配置执行（`qa.csv`）
- 支持自定义知识库、自定义问答对、自定义人设信息
- 支持唤醒及打断对话
- 支持服务器（web）及单机（common）两种启动模式
- 支持机器人表情输出
- 支持 Agent 自主决策与工具调用
- 基于日程式的数字人主动对话
- 支持后台静默启动
- 支持 deepseek 等 thinking LLM（大小模型协同）
- 自我认知提高
- 仿生记忆（记忆流 + 每日反思 + 用户画像）
- 支持 MCP 工具管理（stdio / SSE / studio）
- 提供配置管理中心
- 全链路交互互通

## 效果展示

| 对话界面 | 控制中心 |
| --- | --- |
| ![chat](fay/readme/chat.png) | ![controller](fay/readme/controller.png) |

| 数字人驱动 | MCP 工具管理 |
| --- | --- |
| ![interface](fay/readme/interface.png) | ![mcp](fay/readme/mcp.png) |

## 仓库结构

```
.
├── fay/            # Fay 数字人框架主程序（Python）
│   ├── core/       # 对话流、交互、记忆、录音、WebSocket 服务
│   ├── llm/        # 认知流与记忆调度
│   ├── asr/        # 语音识别（FunASR / 阿里云 NLS / SenseVoice）
│   ├── tts/        # 语音合成（Azure / 阿里云 / GPT-SoVITS / 火山 / edge-tts）
│   ├── gui/        # Web 管理页 + 桌面窗口（Flask / PyQt5）
│   ├── faymcp/     # MCP 客户端、服务端与工具管理
│   ├── genagents/  # 生成式智能体（记忆流、反思）
│   ├── mcp_servers/# 示例 MCP 服务（日程 / logseq / 窗口捕获 / 知识库 / RAG）
│   ├── docs/       # 设计与协议文档
│   └── memory/     # 记忆与知识库数据（运行期生成）
├── human/          # Live2D 数字人模型资源（Lisette）
└── mate-human/     # 基于 Live2D Cubism 5 的 Web 数字人前端
```

## 快速开始

### 环境要求

- Python 3.12
- Windows / macOS / Ubuntu
- Ubuntu 需先安装 gcc 与 portaudio：

```bash
sudo apt update
sudo apt install build-essential
sudo apt install portaudio19-dev
```

### 安装依赖

```bash
cd fay
pip install -r requirements.txt
```

### 配置

编辑 `fay/system.conf`，至少填写以下内容：

- LLM：`gpt_api_key` / `gpt_base_url` / `gpt_model_engine`（OpenAI 兼容接口均可）
- ASR：`asr_mode`（`funasr` / `ali` / `sensevoice`）及对应密钥
- TTS：`tts_module`（`azure` / `ali` / `gptsovits` / `volcano` / `gptsovits_v3`）及对应密钥
- 启动模式：`start_mode`（服务器 / Docker 请用 `web`，桌面模式用 `common`）

### 启动

```bash
# 使用公共资源（速度较慢，建议替换为自己的 key）
python main.py start -config_center d19f7b0a-2b8a-4503-8c0d-1a587b90eb69
```

启动后浏览器访问管理页：**http://127.0.0.1:5000**

> 镜像部署：https://www.compshare.cn/images/compshareImage-1cft3sk9gvta?ytag=GPU_fay

## 接口与端口

| 端口 | 协议 | 用途 |
| --- | --- | --- |
| 5000 | HTTP | Web 管理页、接口服务、TTS 音频下载 |
| 10001 | TCP | 远程音频设备接入（麦克风 / 扬声器） |
| 10002 | WebSocket | 数字人驱动接口（音频、口型、动作、表情） |
| 10003 | WebSocket | Web UI 数据接口 |
| 9001 | WebSocket | socket bridge 服务（桥接远程音频设备） |
| 5010 | HTTP | MCP 管理服务（工具调用、预启用工具调用） |
| 8765 | HTTP / SSE | 内置 MCP Server（记忆工具等） |

- 数字人驱动协议与消息结构：见 [后端对接规范](mate-human/后端对接规范.md)
- MCP 外部调用接口：见 [MCP外部调用接口](fay/docs/MCP外部调用接口.md)

## 数字人前端

数字人渲染由独立前端工程 [mate-human](mate-human) 承担，基于 Live2D Cubism 5，通过 WebSocket 连接 Fay 的 `10002` 端口，实现语音播放、口型同步、表情切换与动作驱动：

```bash
cd mate-human/CubismSdkForWeb-5-r.4/Samples/TypeScript/Demo
npm install
npm start
```

浏览器打开 http://localhost:5173 即可看到 Live2D 角色。模型制作要求见 [Live2D模型制作要求](fay/docs/Live2D模型制作要求.md)。

## 记忆机制

Fay 采用“记忆流 + 每日反思 + 用户画像”的仿生记忆：

- **memory_stream**：以节点形式记录观察、对话与反思，按用户隔离存储于 `memory/`；
- **每日反思**：每晚自动抽取主题，生成 `reflection` 节点并继承业务标签；
- **用户画像**：定时分析对话，更新每个用户的画像；
- **对外接口**：通过内置 MCP Server 暴露 `memory_*` 工具，供外部 Agent 读写同一套记忆。

详见 [记忆机制总览](fay/docs/memory_mechanism.md)。

## 文档

| 文档 | 说明 |
| --- | --- |
| [记忆机制总览](fay/docs/memory_mechanism.md) | 三层存储、写入/检索路径与定时任务 |
| [MCP 外部调用接口](fay/docs/MCP外部调用接口.md) | MCP 工具与预启用工具的 HTTP 接口 |
| [MCP 知识库配置指南](fay/docs/Fay数字人MCP知识库配置指南.md) | 知识库类 MCP 服务接入 |
| [后端对接规范](mate-human/后端对接规范.md) | 数字人驱动协议（音频 / 口型 / 动作 / 表情） |
| [Prompt 设计文档](fay/docs/Prompt设计文档.md) | 提示词与大小模型协同设计 |
| [Live2D 模型制作要求](fay/docs/Live2D模型制作要求.md) | 自定义 Live2D 模型的制作规范 |

## 致谢

感谢以下开源项目为 Fay 提供的技术支持：

- [FunASR](https://github.com/modelscope/FunASR) —— 语音识别（ASR）能力
- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) —— 语音合成（TTS）能力
- [OpenAI Codex](https://github.com/openai/codex) —— 稳定工具调用能力的参考
- [Live2D Cubism SDK](https://www.live2d.com/) —— 数字人渲染引擎
- [openclaw](https://github.com/openclaw/openclaw) —— 记忆机制与 skills 设计的参考

## 开源协议

本项目基于 [GPL-3.0](fay/LICENSE) 开源。

`mate-human` 内的 Live2D Cubism SDK 遵循 [Live2D Open Software License](mate-human/CubismSdkForWeb-5-r.4/LICENSE.md)，`human/` 内的 Live2D 模型仅供学习交流，请勿商用。


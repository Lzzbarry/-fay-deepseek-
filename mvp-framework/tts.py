"""
职坐标数字人框架 - 语音合成与口型生成
使用 edge-tts（微软免费语音）合成音频，并基于词时间戳生成口型数据。
"""
import os
import uuid
import edge_tts

# 音素池：轮转分配，让嘴型有开合变化，看起来在说话
_VISEME_POOL = ["aa", "ou", "oh", "E", "ih", "nn", "kk", "SS"]


def _pick_viseme(index):
    """根据序号轮转选择音素"""
    return _VISEME_POOL[index % len(_VISEME_POOL)]


async def synthesize(text, voice, audio_dir):
    """
    合成语音并生成口型数据。
    :param text: 要合成的文本
    :param voice: edge-tts 语音名
    :param audio_dir: 音频文件存放目录
    :return: (音频文件名, lips列表, 总时长ms)
    """
    os.makedirs(audio_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(audio_dir, filename)

    communicate = edge_tts.Communicate(text, voice)
    lips = []
    audio_data = bytearray()
    word_index = 0
    last_end_ms = 0

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            # edge-tts 的 offset/duration 单位是百纳秒，转毫秒
            offset_ms = int(chunk.get("offset", 0)) / 10000
            duration_ms = int(chunk.get("duration", 0)) / 10000
            word_text = chunk.get("text", "").strip()
            if not word_text or duration_ms <= 0:
                continue
            # 每个词对应一个音素 + 持续时间
            lips.append({
                "Lip": _pick_viseme(word_index),
                "Time": int(duration_ms),
            })
            word_index += 1
            last_end_ms = offset_ms + duration_ms

    # 写入音频文件
    with open(filepath, "wb") as f:
        f.write(audio_data)

    # 若未拿到 WordBoundary，按文本长度估算口型
    if not lips:
        lips = _estimate_lips(text)
        last_end_ms = sum(l["Time"] for l in lips)

    total_ms = int(last_end_ms) if last_end_ms > 0 else max(1000, len(text) * 200)
    return filename, lips, total_ms


def _estimate_lips(text):
    """回退方案：按字符估算口型（每字约 200ms）"""
    lips = []
    for i, ch in enumerate(text):
        if ch.strip():
            lips.append({"Lip": _pick_viseme(i), "Time": 200})
    # 句末静音
    lips.append({"Lip": "sil", "Time": 100})
    return lips


if __name__ == "__main__":
    import asyncio

    async def test():
        fn, lips, dur = await synthesize(
            "你好，欢迎来到职坐标数字人课堂。",
            "zh-CN-XiaoxiaoNeural",
            os.path.join(os.path.dirname(__file__), "audio"),
        )
        print(f"音频: {fn}")
        print(f"口型: {len(lips)} 个, 总时长 {dur}ms")
        print(lips[:5])

    asyncio.run(test())

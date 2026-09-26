"""
职坐标数字人框架 - LLM 对话
支持 OpenAI 兼容接口（本地 LM Studio / Ollama / 在线 API）。
未配置 API Key 时使用预设回复，保证开箱即用。
"""
import config

# 对话历史（简易记忆，保留最近 6 轮）
_history = []
MAX_HISTORY = 6

SYSTEM_PROMPT = (
    "你是职坐标数字人，一位热情专业的课程助手。"
    "请用简洁口语化的中文回答，每句不超过30字，适合语音播报。"
    "避免使用 markdown 格式和特殊符号。"
)

# 预设回复（未配置 LLM 时使用）
_PRESET = [
    ("你好|您好|hi|hello", "你好，欢迎来到职坐标数字人课堂！"),
    ("你是谁|介绍", "我是职坐标数字人，很高兴见到你。"),
    ("课程|课|讲什么", "我们的课程涵盖AI数字人、智能体开发等实战内容。"),
    ("谢谢|感谢", "不客气，很高兴能帮到你！"),
    ("再见|拜拜", "再见，期待下次见面！"),
    ("怎么|如何|怎么做", "这个问题很好，让我为你详细说明一下。"),
    (" Live2D|数字人", "数字人通过Live2D技术实现，可以说话和做动作。"),
]


def _preset_reply(text):
    """关键词匹配的预设回复"""
    for keywords, reply in _PRESET:
        for kw in keywords.split("|"):
            if kw in text:
                return reply
    return "我收到了你的消息，让我想想怎么回答。你可以试试问我课程相关的问题。"


def chat(user_text):
    """
    生成回复。
    :param user_text: 用户输入
    :return: 回复文本
    """
    if not config.ENABLE_LLM:
        return _preset_reply(user_text)

    try:
        from openai import OpenAI

        client = OpenAI(base_url=config.LLM_API_BASE, api_key=config.LLM_API_KEY)
        _history.append({"role": "user", "content": user_text})

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(_history[-MAX_HISTORY:])

        resp = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=200,
        )
        reply = resp.choices[0].message.content.strip()
        _history.append({"role": "assistant", "content": reply})

        # 控制历史长度
        if len(_history) > MAX_HISTORY * 2:
            del _history[:2]
        return reply
    except Exception as e:
        print(f"[LLM] 调用失败，回退到预设回复: {e}")
        return _preset_reply(user_text)


def clear_history():
    """清空对话历史"""
    _history.clear()


if __name__ == "__main__":
    import config
    config.ENABLE_LLM = False
    for t in ["你好", "这门课讲什么", "你是谁"]:
        print(t, "->", chat(t))

"""
职坐标数字人框架 - 配置文件
所有参数均可通过环境变量覆盖，方便部署和课堂演示。
"""
import os

# ============ 服务端口 ============
# WebSocket 服务端口（Live2D 前端连接此端口接收音频与动作指令）
WS_PORT = int(os.getenv("WS_PORT", "10002"))

# HTTP 服务端口（提供音频文件下载 + Web 控制台）
HTTP_PORT = int(os.getenv("HTTP_PORT", "5000"))

# ============ 音频 ============
# 音频文件存放目录
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

# TTS 语音（edge-tts 免费微软语音）
# 常用：zh-CN-XiaoxiaoNeural(女-晓晓) / zh-CN-YunxiNeural(男-云希)
TTS_VOICE = os.getenv("TTS_VOICE", "zh-CN-XiaoxiaoNeural")

# ============ LLM 大语言模型 ============
# 使用 OpenAI 兼容接口，可接本地 LM Studio / Ollama / 在线 API
# 本地 LM Studio 默认地址：http://127.0.0.1:1234/v1
# 不配置 LLM_API_KEY 时自动使用预设回复（保证开箱即用）
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.deepseek.com")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-v4-flash")

# 是否启用真实 LLM 对话
ENABLE_LLM = bool(LLM_API_KEY)

# ============ 其他 ============
# 数字人名称
ROBOT_NAME = os.getenv("ROBOT_NAME", "职坐标数字人")

# 默认用户名（与前端握手一致）
DEFAULT_USERNAME = "User"

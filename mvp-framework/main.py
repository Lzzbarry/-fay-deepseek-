"""
职坐标数字人框架 - 主服务
同时启动 WebSocket 服务（10002，对接 Live2D 前端）和 HTTP 服务（5000，音频下载 + 控制台）。
"""
import asyncio
import json
import os
import re

from aiohttp import web, WSMsgType

import config
from tts import synthesize
from sentiment import analyze_sentiment
from action_rules import match_action
from llm import chat

# 连接的输出端（Live2D 前端）
_clients = set()


def split_sentences(text):
    """按标点切分句子，便于流式语音合成"""
    text = text.strip()
    if not text:
        return []
    parts = re.split(r"[。！？!?\n；;]+", text)
    sentences = []
    for p in parts:
        p = p.strip()
        if p:
            sentences.append(p)
    return sentences or [text]


async def handle_conversation(ws, user_text, username):
    """处理一轮对话：LLM 回复 -> 切句 -> TTS 合成 -> 流式推送"""
    try:
        # reply = chat(user_text)
        from mcp_platform.agent import agent
        result = await agent.invoke({"question": user_text, "context": [], "iterations": 0})
        reply = result["answer"]
        print(f"[对话] 用户: {user_text}")
        print(f"[对话] 回复: {reply}")

        sentences = split_sentences(reply)
        total = len(sentences)

        for i, sent in enumerate(sentences):
            filename, lips, duration = await synthesize(
                sent, config.TTS_VOICE, config.AUDIO_DIR
            )
            message = {
                "Topic": "human",
                "Data": {
                    "Key": "audio",
                    "Text": sent,
                    "HttpValue": f"http://127.0.0.1:{config.HTTP_PORT}/audio/{filename}",
                    "IsFirst": 1 if i == 0 else 0,
                    "IsEnd": 1 if i == total - 1 else 0,
                    "Lips": lips,
                    "Sentiment": analyze_sentiment(sent),
                    "Action": match_action(sent),
                },
                "Username": username,
                "robot": config.ROBOT_NAME,
            }
            await ws.send_str(json.dumps(message, ensure_ascii=False))
            print(f"[推送] ({i + 1}/{total}) {sent} | 口型{len(lips)}个 | {duration}ms")
            # 等待该句音频播放完成
            await asyncio.sleep(duration / 1000 + 0.4)
    except Exception as e:
        print(f"[对话] 处理失败: {e}")


# ============ WebSocket 服务（10002 端口）============

async def ws_handler(request):
    ws = web.WebSocketResponse(heartbeat=30)
    await ws.prepare(request)
    _clients.add(ws)
    print(f"[WebSocket] 新连接，当前输出端数: {len(_clients)}")
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except json.JSONDecodeError:
                    continue
                # 握手消息：{Username, Output:true}
                if data.get("Output"):
                    print(f"[WebSocket] 输出端已注册: {data.get('Username', config.DEFAULT_USERNAME)}")
                    continue
                # 用户输入消息：{Username, Text}
                if "Text" in data:
                    asyncio.create_task(handle_conversation(
                        ws, data.get("Text", ""), data.get("Username", config.DEFAULT_USERNAME)
                    ))
            elif msg.type == WSMsgType.ERROR:
                print(f"[WebSocket] 错误: {ws.exception()}")
                break
    finally:
        _clients.discard(ws)
        print(f"[WebSocket] 连接关闭，当前输出端数: {len(_clients)}")
    return ws


# ============ HTTP 服务（5000 端口）============

async def audio_handler(request):
    filename = request.match_info["filename"]
    if "/" in filename or "\\" in filename or ".." in filename:
        return web.Response(status=400, text="非法文件名")
    filepath = os.path.join(config.AUDIO_DIR, filename)
    if not os.path.exists(filepath):
        return web.Response(status=404, text="音频不存在")
    return web.FileResponse(filepath, headers={
        "Cache-Control": "no-cache",
        "Access-Control-Allow-Origin": "*",
    })


async def send_handler(request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    user_text = data.get("text", "").strip()
    username = data.get("username", config.DEFAULT_USERNAME)
    if not user_text:
        return web.json_response({"status": "error", "msg": "文本为空"}, status=400)
    if not _clients:
        return web.json_response({"status": "error", "msg": "没有前端连接，请先打开 Live2D 页面"}, status=400)
    for ws in list(_clients):
        asyncio.create_task(handle_conversation(ws, user_text, username))
    return web.json_response({"status": "ok", "reply_to": user_text})


async def status_handler(request):
    return web.json_response({
        "robot": config.ROBOT_NAME,
        "clients": len(_clients),
        "llm_enabled": config.ENABLE_LLM,
        "voice": config.TTS_VOICE,
    })


async def index_handler(request):
    return web.Response(text=CONSOLE_HTML, content_type="text/html", charset="utf-8")


CONSOLE_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>职坐标数字人控制台</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, "Microsoft YaHei", sans-serif; background: #f0f2f5; color: #333; min-height: 100vh; display: flex; justify-content: center; padding: 40px 20px; }
  .container { width: 100%; max-width: 560px; }
  .card { background: #fff; border-radius: 16px; padding: 28px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); margin-bottom: 20px; }
  h1 { font-size: 22px; margin-bottom: 6px; }
  .sub { color: #888; font-size: 13px; margin-bottom: 20px; }
  .status { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 18px; }
  .badge { padding: 5px 12px; border-radius: 20px; font-size: 12px; background: #f0f2f5; }
  .badge.on { background: #e6f7ed; color: #27ae60; }
  .badge.off { background: #fef0f0; color: #e74c3c; }
  .quick { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
  .quick button { padding: 6px 14px; border: 1px solid #d9d9d9; border-radius: 18px; background: #fff; cursor: pointer; font-size: 13px; color: #555; transition: all .2s; }
  .quick button:hover { border-color: #4a90d9; color: #4a90d9; }
  .input-row { display: flex; gap: 10px; }
  input { flex: 1; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 12px; font-size: 15px; outline: none; transition: border-color .2s; }
  input:focus { border-color: #4a90d9; }
  .send { padding: 12px 28px; background: #4a90d9; color: #fff; border: none; border-radius: 12px; font-size: 15px; cursor: pointer; font-weight: 600; transition: background .2s; }
  .send:hover { background: #3a7bc8; }
  .send:disabled { background: #bbb; cursor: not-allowed; }
  .log { max-height: 320px; overflow-y: auto; }
  .log-item { padding: 10px 14px; border-radius: 10px; margin-bottom: 8px; font-size: 14px; line-height: 1.6; }
  .log-user { background: #e8f1fc; text-align: right; }
  .log-bot { background: #f5f5f5; }
  .log-bot .meta { font-size: 11px; color: #999; margin-top: 4px; }
  .empty { text-align: center; color: #bbb; padding: 30px 0; font-size: 14px; }
  .tip { font-size: 12px; color: #999; margin-top: 14px; line-height: 1.6; }
</style>
</head>
<body>
<div class="container">
  <div class="card">
    <h1>职坐标数字人控制台</h1>
    <p class="sub">输入文字，Live2D 数字人即可开口说话</p>
    <div class="status">
      <span class="badge" id="badge-conn">前端: 检测中</span>
      <span class="badge" id="badge-llm">LLM: 检测中</span>
      <span class="badge" id="badge-voice">语音: -</span>
    </div>
    <div class="quick">
      <button onclick="quick('你好，欢迎来到职坐标')">你好</button>
      <button onclick="quick('请介绍一下这门课程')">介绍课程</button>
      <button onclick="quick('太好了，我学会了！')">庆祝</button>
      <button onclick="quick('抱歉，这个问题我不太确定')">致歉</button>
    </div>
    <div class="input-row">
      <input id="txt" placeholder="输入要让数字人说的话..." onkeydown="if(event.key==='Enter')send()">
      <button class="send" id="btn" onclick="send()">发送</button>
    </div>
    <p class="tip">提示：先打开 Live2D 前端页面 (http://localhost:5173)，再在此输入文字。<br>未配置 LLM 时使用预设回复，配置后为真实 AI 对话。</p>
  </div>
  <div class="card">
    <div class="log" id="log">
      <div class="empty">暂无对话记录</div>
    </div>
  </div>
</div>
<script>
async function refreshStatus(){
  try{
    const r = await fetch('/status');
    const d = await r.json();
    const conn = document.getElementById('badge-conn');
    conn.textContent = '前端: ' + (d.clients>0?'已连接':'未连接');
    conn.className = 'badge ' + (d.clients>0?'on':'off');
    const llm = document.getElementById('badge-llm');
    llm.textContent = 'LLM: ' + (d.llm_enabled?'已启用':'预设模式');
    llm.className = 'badge ' + (d.llm_enabled?'on':'off');
    document.getElementById('badge-voice').textContent = '语音: ' + d.voice;
  }catch(e){}
}
function addLog(role, text, meta){
  const log = document.getElementById('log');
  if(log.querySelector('.empty')) log.innerHTML='';
  const div = document.createElement('div');
  div.className = 'log-item log-' + role;
  div.innerHTML = text + (meta?`<div class="meta">${meta}</div>`:'');
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}
async function send(){
  const txt = document.getElementById('txt').value.trim();
  if(!txt) return;
  document.getElementById('txt').value='';
  addLog('user', txt);
  const btn = document.getElementById('btn');
  btn.disabled = true;
  try{
    const r = await fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:txt})});
    const d = await r.json();
    if(d.status!=='ok'){ addLog('bot','⚠ '+(d.msg||'发送失败')); }
    else{ addLog('bot','已推送给数字人','回复内容将逐句在 Live2D 页面播放'); }
  }catch(e){ addLog('bot','⚠ 网络错误'); }
  btn.disabled = false;
}
function quick(t){ document.getElementById('txt').value=t; send(); }
refreshStatus();
setInterval(refreshStatus, 3000);
</script>
</body>
</html>
"""


async def main():
    os.makedirs(config.AUDIO_DIR, exist_ok=True)

    # WebSocket 应用（10002）
    ws_app = web.Application()
    ws_app.router.add_get("/", ws_handler)

    # HTTP 应用（5000）
    http_app = web.Application()
    http_app.router.add_get("/", index_handler)
    http_app.router.add_get("/audio/{filename}", audio_handler)
    http_app.router.add_post("/send", send_handler)
    http_app.router.add_get("/status", status_handler)

    ws_runner = web.AppRunner(ws_app)
    await ws_runner.setup()
    await web.TCPSite(ws_runner, "0.0.0.0", config.WS_PORT).start()

    http_runner = web.AppRunner(http_app)
    await http_runner.setup()
    await web.TCPSite(http_runner, "0.0.0.0", config.HTTP_PORT).start()

    print("=" * 52)
    print(f"  {config.ROBOT_NAME} 框架已启动")
    print("=" * 52)
    print(f"  WebSocket 服务: ws://127.0.0.1:{config.WS_PORT}")
    print(f"  音频服务:       http://127.0.0.1:{config.HTTP_PORT}/audio/<文件>")
    print(f"  Web 控制台:     http://127.0.0.1:{config.HTTP_PORT}")
    print(f"  LLM 对话:       {'已启用' if config.ENABLE_LLM else '未启用(用预设回复)'}")
    print(f"  TTS 语音:       {config.TTS_VOICE}")
    print("=" * 52)
    print("  在浏览器打开控制台，输入文字即可让数字人说话")
    print("  按 Ctrl+C 停止服务")
    print("=" * 52)

    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[系统] 服务已停止")

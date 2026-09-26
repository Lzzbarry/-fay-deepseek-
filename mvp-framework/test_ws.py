"""
全链路测试脚本：模拟 Live2D 前端连接后端，验证消息推送。
运行: python test_ws.py
"""
import asyncio
import json
import aiohttp


async def test():
    print("[测试] 连接 ws://127.0.0.1:10002 ...")
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect("ws://127.0.0.1:10002/") as ws:
            print("[测试] 已连接")

            # 1. 发送握手消息（模拟前端注册为输出端）
            await ws.send_str(json.dumps({"Username": "User", "Output": True}))
            print("[测试] 已发送握手消息")

            # 2. 发送用户输入（触发对话）
            await ws.send_str(json.dumps({"Username": "User", "Text": "你好"}))
            print('[测试] 已发送用户输入: "你好"')
            print("[测试] 等待后端推送音频消息...\n")

            # 3. 接收并验证后端推送的消息
            msg_count = 0
            while True:
                try:
                    msg = await asyncio.wait_for(ws.receive(), timeout=30)
                except asyncio.TimeoutError:
                    print("[测试] 30秒内未收到消息，超时退出")
                    break

                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    msg_count += 1
                    d = data.get("Data", {})
                    print(f"--- 收到消息 {msg_count} ---")
                    print(f"  Topic:     {data.get('Topic')}")
                    print(f"  Key:       {d.get('Key')}")
                    print(f"  Text:      {d.get('Text')}")
                    print(f"  HttpValue: {d.get('HttpValue')}")
                    print(f"  IsFirst:   {d.get('IsFirst')}")
                    print(f"  IsEnd:     {d.get('IsEnd')}")
                    print(f"  Lips:      {len(d.get('Lips', []))} 个音素")
                    print(f"  Sentiment: {d.get('Sentiment')}")
                    action = d.get("Action")
                    if action:
                        print(f"  Action:    {action.get('code')} | behavior={action.get('behavior')} | affect={action.get('affect')}")
                    else:
                        print(f"  Action:    None")

                    # 验证关键字段
                    assert d.get("Key") == "audio", "Key 应为 audio"
                    assert d.get("HttpValue"), "应有音频地址"
                    assert d.get("Lips"), "应有口型数据"
                    print("  [验证] 字段完整 OK\n")

                    if d.get("IsEnd") == 1:
                        print(f"[测试] 收到结束标记，共 {msg_count} 条消息")
                        break
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    print("[测试] 连接关闭")
                    break

            await ws.close()
            print("[测试] 全链路验证通过!")


if __name__ == "__main__":
    asyncio.run(test())

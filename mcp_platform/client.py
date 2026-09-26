"""
MCP 中台 - Client 端
连接 MCP Server，发现工具、调用工具。
任何需要调用 MCP 中台的服务（数字人后端、Web 控制台）
都通过这个 Client 来调。

"""
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    """MCP 中台客户端 —— 数字人后端通过它调用所有工具"""

    def __init__(self):
        self.session = None
        self.tools = []

    async def connect(self, server_script="server.py"):
        """启动 MCP Server 子进程并连接"""
        params = StdioServerParameters(
            command=sys.executable,
            args=[server_script],
        )
        self._read, self._write = await stdio_client(params).__aenter__()
        self.session = await ClientSession(self._read, self._write).__aenter__()
        await self.session.initialize()

        # 动态发现 Server 有哪些工具
        result = await self.session.list_tools()
        self.tools = [t.name for t in result.tools]
        print(f"[MCP Client] 已连接，可用工具: {self.tools}")
        return self.tools

    async def call(self, tool_name: str, **kwargs) -> dict:
        """像调本地函数一样调远端 MCP 工具"""
        result = await self.session.call_tool(tool_name, kwargs)
        return result

    async def close(self):
        if self.session:
            await self.session.__aexit__(None, None, None)

# 全局单例
mcp_client = MCPClient()
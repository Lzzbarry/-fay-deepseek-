"""
MCP 中台 - Server 端
把所有工具封装成 MCP 协议暴露，
任何客户端（数字人、钉钉机器人、网页）都能调。
"""
from mcp.server.mcpserver.server import MCPServer

app = MCPServer("zhizhubiao-mcp-platform")

# ===== 4 个核心工具 =====

@app.tool()
def searchKnowledge(query: str, size: int = 5) -> dict:
    """从知识库中检索与 query 相关的文档片段。"""
    # 教学版：先用关键词匹配（生产版换向量检索）
    results = knowledge_store.search(query, size)
    return {"hits": results, "total": len(results)}

@app.tool()
def storeKnowledge(content: str, title: str = "") -> dict:
    """将一段文本存入知识库。"""
    chunk_id = knowledge_store.add(content, title)
    return {"status": "ok", "chunk_id": chunk_id}

@app.tool()
def getProductInfo(product_name: str) -> dict:
    """查询产品信息（对接 Odoo 19）。"""
    # 教学版：模拟数据（生产版换 Odoo XML-RPC 调用）
    return {"name": product_name, "price": 299, "stock": 150}

@app.tool()
def getOrderStatus(order_id: str) -> dict:
    """查询订单状态（对接 Odoo 19）。"""
    return {"order_id": order_id, "status": "shipped", "eta": "3天"}

@app.tool()
def searchOdooSales(month: str) -> dict:
    """查询 Odoo 19 中某月的销售数据"""
    # 生产版：odoo.xmlrpc.execute_kw(...)
    # 教学版：模拟数据
    return {"month": month, "revenue": 1280000, "orders": 342}

if __name__ == "__main__":
    print("MCP Server 启动中...")
    app.run(transport="stdio")
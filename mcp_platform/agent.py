"""
MCP 中台 - LangGraph Agent
用状态图编排数字人的思考流程：
理解意图 → 查知识库 → 判断够不够 → 不够就查 Odoo → 生成回复
"""
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_components import llm, search_similar, chain

# ===== 定义 State（全局数据容器，替代你 llm.py 里 _history 列表）=====
class AgentState(TypedDict):
    question: str                    # 用户问题
    context: Annotated[list, operator.add]  # 累积的检索结果
    answer: str                     # 最终答案
    iterations: int                 # 循环次数（防无限循环）

# ===== 节点 1：理解意图 =====
def understand(state: AgentState) -> AgentState:
    print(f"[Agent] 理解: {state['question']}")
    return state

# ===== 节点 2：查知识库（通过 MCP 工具）=====
def search_knowledge(state: AgentState) -> AgentState:
    print(f"[Agent] 检索知识库...")
    results = search_similar(state["question"])
    return {"context": [results]}

# ===== 节点 3：判断信息够不够 =====
def should_search_more(state: AgentState) -> str:
    if state["iterations"] >= 2:
        return "generate"
    if len(state["context"]) == 0:
        return "search_odoo"
    return "generate"

# ===== 节点 4：查 Odoo（业务数据）=====
def search_odoo(state: AgentState) -> AgentState:
    print(f"[Agent] 检索 Odoo 业务数据...")
    # 教学版：模拟（生产版调 mcp_client.call("getProductInfo", ...)）
    odoo_result = "Odoo 数据：本月销售额 128 万，同比增长 15%"
    return {"context": [odoo_result], "iterations": state["iterations"] + 1}

# ===== 节点 5：生成最终回复 =====
def generate(state: AgentState) -> AgentState:
    context_text = "\n".join(state["context"])
    answer = chain.invoke({
        "context": context_text,
        "question": state["question"],
    })
    print(f"[Agent] 生成回复: {answer[:50]}...")
    return {"answer": answer}

# ===== 组装 StateGraph =====
def build_agent() -> StateGraph:
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("understand", understand)
    graph.add_node("search_kb", search_knowledge)
    graph.add_node("search_odoo", search_odoo)
    graph.add_node("generate", generate)

    # 设置入口
    graph.set_entry_point("understand")

    # 添加边
    graph.add_edge("understand", "search_kb")
    graph.add_conditional_edges(
        "search_kb",
        should_search_more,
        {
            "generate": "generate",
            "search_odoo": "search_odoo",
        }
    )
    graph.add_edge("search_odoo", "generate")
    graph.add_edge("generate", END)

    return graph.compile()

agent = build_agent()
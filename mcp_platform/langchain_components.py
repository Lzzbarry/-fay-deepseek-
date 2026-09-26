"""
MCP 中台 - LangChain 组件层
用 LangChain 标准化零件替换手写代码。
这个文件 = 你原来 llm.py 的"升级版"。
"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
import os

# ===== LLM 封装（替代你 llm.py 里手写的 client.chat.completions.create）=====
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
    base_url=os.getenv("LLM_API_BASE", "https://api.openai.com/v1"),
    api_key=os.getenv("LLM_API_KEY", "sk-xxx"),
    temperature=0.7,
)

# ===== Prompt 模板（替代你 llm.py 里 SYSTEM_PROMPT 字符串）=====
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是职坐标数字人，一位热情专业的课程助手。
回答要简洁口语化，每句不超过30字，适合语音播报。
如果提供了"参考知识"，请基于参考知识回答。
如果没有参考知识，用自己的知识回答。"""),
    ("user", "参考知识：{context}\n\n用户问题：{question}"),
])

# ===== 文档加载 + 切分（你原来没有，MCP 中台新增）=====
splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=80)

def load_and_split(file_path: str) -> list:
    """加载文档并切分成小块"""
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    return splitter.split_documents(docs)

# ===== Embedding + 向量数据库（你原来没有，MCP 中台新增）=====
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv("LLM_API_KEY", "sk-xxx"),
)
vector_store = Chroma(
    collection_name="zhizhubiao_kb",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

def search_similar(query: str, k: int = 5) -> str:
    """语义检索：搜与 query 意思相似的文档（不是关键词匹配）"""
    docs = vector_store.similarity_search(query, k=k)
    return "\n---\n".join([d.page_content for d in docs])

# ===== 组装管道：Prompt → LLM → 解析（就是你 llm.py 里 chat() 做的事，但标准化了）=====
chain = agent_prompt | llm | StrOutputParser()
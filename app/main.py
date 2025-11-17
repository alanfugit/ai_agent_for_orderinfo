from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import asyncio

# 导入我们新的 agent 逻辑
from . import agent, config

# --- Pydantic 模型定义 (保持不变) ---
class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    question: str
    answer: str
    intermediate_steps: list | None = None # Agent 的思考过程

# --- 依赖注入 (保持不变) ---
def get_settings():
    return config.Settings()

# --- FastAPI 应用实例 (保持不变) ---
app = FastAPI()
@app.post("/ask/agent", response_model=AnswerResponse)
async def ask_agent(
    request: QuestionRequest,
    settings: config.Settings = Depends(get_settings)
):
    """
    使用 LangChain SQL Agent 回答关于订单的问题。
    Agent 会动态地决定执行步骤，并能从错误中恢复。
    """
    try:
        # 1. 获取 Agent Executor
        # 我们在这里初始化 Agent，也可以在应用启动时初始化一个全局的 Agent
        agent_executor = agent.get_agent_executor(settings)
        # 2. 运行 Agent
        # LangChain 的 agent.invoke 是一个阻塞操作，
        # 为了不阻塞 FastAPI 的事件循环，我们使用 asyncio.to_thread 来在单独的线程中运行它。
        result = await asyncio.to_thread(
            agent_executor.invoke,
            {"input": request.question}
        )

        # 3. 提取并返回结果
        answer = result.get("output", "Agent 未能提供最终答案。")
        intermediate_steps = result.get("intermediate_steps", [])
        
        return AnswerResponse(
            question = request.question,
            answer = answer,
            intermediate_steps = intermediate_steps # 返回思考过程，便于调试
        ) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 执行时发生错误: {e}")

@app.get("/")
def read_root():
    return {"message": "欢迎使用订单问答系统 API！请访问 /docs 查看 API 文档。"}

# app/agents/executor.py
from langchain_openai import ChatOpenAI  # ✅ New import

llm = ChatOpenAI(model="gpt-4", temperature=0.2)

def execute_task(task_obj: dict) -> dict:
    task = task_obj["task"]
    content = task_obj["content"]
    
    prompt_map = {
        "tone_analysis": f"Analyze the tone of this financial report: {content}",
        "ethical_risk_check": f"Check this financial text for manipulation, projection bias, or ethical concerns: {content}",
        "financial_keywords": f"Extract financial terms and concepts: {content}"
    }

    response = llm.invoke(prompt_map[task])
    return {"task": task, "result": response.content}

# app/agents/executor.py
import time
import logging
from langchain_openai import ChatOpenAI
from app.core.metrics import MetricsCollector

logger = logging.getLogger(__name__)
metrics = MetricsCollector()

llm = ChatOpenAI(model="gpt-4", temperature=0.2)

def execute_task(task_obj: dict) -> dict:
    task = task_obj["task"]
    content = task_obj["content"]
    
    logger.debug(f"Executing task: {task}", extra={"component": "executor"})
    start_time = time.time()
    
    prompt_map = {
        "tone_analysis": f"Analyze the tone of this financial report: {content}",
        "ethical_risk_check": f"Check this financial text for manipulation, projection bias, or ethical concerns: {content}",
        "financial_keywords": f"Extract financial terms and concepts: {content}"
    }

    try:
        response = llm.invoke(prompt_map[task])
        duration = time.time() - start_time
        
        # Record metrics
        metrics.record_agent_task(task, duration)
        metrics.record_openai_call("gpt-4", "success", duration)
        
        logger.info(
            f"Task completed: {task}",
            extra={
                "task": task,
                "duration_ms": int(duration * 1000),
                "component": "executor"
            }
        )
        
        return {"task": task, "result": response.content}
        
    except Exception as e:
        duration = time.time() - start_time
        error_type = type(e).__name__
        
        # Record error metrics
        metrics.record_agent_task(task, duration)
        metrics.record_openai_call("gpt-4", "error", duration)
        metrics.record_error(error_type, "executor")
        
        logger.error(
            f"Task failed: {task} - {str(e)}",
            extra={
                "task": task,
                "error_type": error_type,
                "duration_ms": int(duration * 1000),
                "component": "executor"
            },
            exc_info=True
        )
        
        raise

from app.agents.planner import plan_tasks
from app.agents.executor import execute_task
from app.agents.verifier import verify_result

def run_agent_pipeline(text: str) -> dict:
    tasks = plan_tasks(text)
    execution_results = []

    for task in tasks:
        result = execute_task(task)
        execution_results.append(result)

    flags = verify_result(execution_results)

    return {
        "steps": execution_results,
        "flags": flags
    }

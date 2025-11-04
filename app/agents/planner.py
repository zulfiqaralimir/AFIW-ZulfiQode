def plan_tasks(input_text: str) -> list:
    return [
        {"task": "tone_analysis", "content": input_text},
        {"task": "ethical_risk_check", "content": input_text},
        {"task": "financial_keywords", "content": input_text}
    ]

from app.evaluation import metrics

def verify_result(execution_results: list) -> dict:
    flags = {}
    for item in execution_results:
        task = item["task"]
        output = item["result"]

        bias_score = metrics.detect_bias_signals(output)
        hallucinated = metrics.detect_hallucination_signals(output)
        explain_score = metrics.evaluate_explanation_clarity(output)

        flags[task] = {
            "bias_score": bias_score,
            "hallucination": hallucinated,
            "explanation_ok": bool(explain_score)
        }

    return flags

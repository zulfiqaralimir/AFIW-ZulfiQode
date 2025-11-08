from app.evaluation.metrics import (
	detect_bias_signals,
	detect_hallucination_signals,
)
from app.core.metrics import HALLUCINATION_ALERTS


def verify_result(execution_results: list) -> dict:
	flags = {}
	for item in execution_results:
		task = item["task"]
		output: str = item.get("result", "")

		bias_score = detect_bias_signals(output)
		hallucination = detect_hallucination_signals(output)
		
		# Increment hallucination metric if detected
		if hallucination:
			HALLUCINATION_ALERTS.inc()
		
		status = "Red Flag" if (bias_score > 0 or hallucination) else "Clear"

		# Build a concise reason from matched words/phrases
		reason = ""
		lower = output.lower()
		bias_keywords = ["manipulate", "bias", "overconfident", "inflated", "ambiguous"]
		hallu_phrases = ["as an ai", "i do not have", "cannot verify"]
		matched_bias = next((w for w in bias_keywords if w in lower), None)
		matched_hallu = next((p for p in hallu_phrases if p in lower), None)
		if matched_bias:
			reason = f"Found bias keyword: '{matched_bias}'"
		elif matched_hallu:
			reason = f"Found hallucination phrase: '{matched_hallu}'"

		flags[task] = {
			"status": status,
			"bias_score": bias_score,
			"hallucination": hallucination,
			"reason": reason,
		}

	return flags

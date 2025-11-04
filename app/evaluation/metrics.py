import re

def detect_bias_signals(text: str) -> int:
    keywords = ["manipulate", "bias", "overconfident", "inflated", "ambiguous"]
    return sum(1 for word in keywords if word in text.lower())

def detect_hallucination_signals(text: str) -> bool:
    hallucination_flags = ["as an AI", "I do not have", "cannot verify"]
    return any(flag in text.lower() for flag in hallucination_flags)

def evaluate_explanation_clarity(text: str) -> int:
    if len(text.split()) > 50 and "." in text:
        return 1  # Good explanation
    return 0  # Needs improvement

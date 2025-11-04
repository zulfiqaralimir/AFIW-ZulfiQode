def verify_result(execution_results: list) -> dict:
    flags = {}
    for item in execution_results:
        task = item["task"]
        output = item["result"].lower()
        if "manipulate" in output or "bias" in output:
            flags[task] = "Red Flag"
        else:
            flags[task] = "Clear"
    return flags

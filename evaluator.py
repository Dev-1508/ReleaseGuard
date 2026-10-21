def evaluate_exact_match(expected_output, actual_output):
    if expected_output == actual_output:
        return 1

    return 0


def evaluate_tool_call(expected_tool, tool_calls):
    if expected_tool is None:
        return None

    if len(tool_calls) == 0:
        return 0

    actual_tool = tool_calls[0]["tool"]

    if expected_tool == actual_tool:
        return 1

    return 0
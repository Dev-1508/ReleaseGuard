import re

def evaluate_exact_match(expected_output, actual_output):
    if expected_output == actual_output:
        return 1

    return 0

def evaluate_normalized_match(expected_output, actual_output):

    expected = expected_output.lower().strip()
    actual = actual_output.lower().strip()

    expected = re.sub(r"#\d+", "", expected)
    actual = re.sub(r"#\d+", "", actual)

    expected = " ".join(expected.split())
    actual = " ".join(actual.split())

    if expected == actual:
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
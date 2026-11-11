from evaluator import (
    evaluate_normalized_match,
    evaluate_tool_call
)


def test_normalized_exact_match():
    score = evaluate_normalized_match(
        "Order cancelled successfully",
        "Order cancelled successfully"
    )

    assert score == 1


def test_normalized_ignores_order_number():
    score = evaluate_normalized_match(
        "Order #123 cancelled successfully",
        "Order #789 cancelled successfully"
    )

    assert score == 1


def test_normalized_detects_different_meaning():
    score = evaluate_normalized_match(
        "Order cancelled successfully",
        "Order is currently in transit"
    )

    assert score == 0


def test_correct_tool_call():
    tool_calls = [
        {
            "tool": "cancel_order",
            "arguments": {
                "order_id": 123
            },
            "result": "Order #123 cancelled successfully"
        }
    ]

    score = evaluate_tool_call(
        "cancel_order",
        tool_calls
    )

    assert score == 1


def test_wrong_tool_call():
    tool_calls = [
        {
            "tool": "get_order_status",
            "arguments": {
                "order_id": 123
            },
            "result": "Order #123 is currently in transit"
        }
    ]

    score = evaluate_tool_call(
        "cancel_order",
        tool_calls
    )

    assert score == 0


def test_missing_tool_call():
    score = evaluate_tool_call(
        "cancel_order",
        []
    )

    assert score == 0
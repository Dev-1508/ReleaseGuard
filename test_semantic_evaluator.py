from semantic_evaluator import evaluate_semantic_match


score_1 = evaluate_semantic_match(
    "Order cancelled successfully",
    "Your order has been successfully cancelled."
)

print("Similar meaning:", score_1)


score_2 = evaluate_semantic_match(
    "Order cancelled successfully",
    "Order #123 is currently in transit."
)

print("Different meaning:", score_2)
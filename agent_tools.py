def cancel_order(order_id: int) -> str:
    """
    Cancel a customer order.

    Args:
        order_id: The numeric ID of the order to cancel.

    Returns:
        A message confirming that the order was cancelled.
    """

    return f"Order #{order_id} cancelled successfully"


def get_order_status(order_id: int) -> str:
    """
    Get the current status of a customer order.

    Args:
        order_id: The numeric ID of the order.

    Returns:
        A message describing the current order status.
    """

    return f"Order #{order_id} is currently in transit"
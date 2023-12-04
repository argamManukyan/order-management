class NotPassedVerification(Exception):
    """Raises when user did not pass the verification process."""


class ObjectAlreadyExists(Exception):
    """Raises when any object instance exists."""


class FiredFromWorkException(Exception):
    """Raises when user worked negative salary"""


class StockQuantityIsNotEnough(Exception):
    """Raises when product stock quantity is not enough"""


class StatusDoesNotExists(Exception):
    """Raises when one of the statuses does not define"""


class OrderAlreadyHasBeenPaid(Exception):
    """Raises when is tried to update order status"""


class DiscountError(Exception):
    """Raises when discount is given incorrectly"""


class InvalidCustomerAddress(Exception):
    """Raises when customer address is invalid (not belongs to the customer)"""


class ItemsDoNotFound(Exception):
    """Raises when items don't found"""


class RateError(Exception):
    """Raises when rating is not allowed"""

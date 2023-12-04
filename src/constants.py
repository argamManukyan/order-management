import os
from enum import Enum, auto


MINIMUM_RATING = 2


class CustomerAddressActions(Enum):
    ADD = auto()
    REMOVE = auto()


class OrderDeliveryStatuses(Enum):
    WAITING = auto()
    IN_PROGRESS = auto()
    PICK_UP = auto()
    ON_THE_WAY = auto()
    DELIVERED = auto()
    RETURNED = auto()
    CANCELED = auto()

    @classmethod
    def values(cls):
        return [i.value for i in cls]


class OrderPaymentStatus(Enum):
    WAITING = auto()
    UNPAID = auto()
    PAID = auto()
    REFUNDED = auto()
    CANCELED = auto()

    @classmethod
    def values(cls):
        return [i.value for i in cls]


# Email settings

EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_SERVER = os.environ.get("EMAIL_SERVER")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")

import logging
from dataclasses import dataclass, field
from typing import Optional

from .constants import OrderPaymentStatus, OrderDeliveryStatuses
from .customer import Customer, CustomerAddress
from .employee import Employee, EmployeeRating
from .exceptions import (
    StockQuantityIsNotEnough,
    StatusDoesNotExists,
    OrderAlreadyHasBeenPaid,
    InvalidCustomerAddress,
    ItemsDoNotFound,
    RateError,
)
from .helpers import BaseModel
from .product import Product
from .management import InstanceManagement

order_instances = InstanceManagement([])
logger = logging.getLogger()


@dataclass
class OrderItem(BaseModel):
    product: Product
    qty: float
    item_price: float

    @property
    def item_total(self) -> float:
        return self.qty * self.item_price

    def validate_qty(self):
        if self.qty > self.product.stock_qty:
            raise StockQuantityIsNotEnough
        if self.qty < 0:
            raise ValueError

    def __post_init__(self):
        self.validate_qty()
        super().__post_init__()


@dataclass
class Order(BaseModel):
    customer: Customer
    customer_address: CustomerAddress
    employee: Employee
    employee_rating: Optional[EmployeeRating] = None
    items: list[OrderItem] = field(default_factory=list)
    _order_delivery_status: int = (
        OrderDeliveryStatuses.WAITING.value
    )  # OrderDeliveryStatuses
    _order_payment_status: int = OrderPaymentStatus.WAITING.value  # OrderPaymentStatus
    _ordered: bool = False
    __management_instance = order_instances

    @property
    def ordered(self):
        return self._ordered

    @property
    def delivery_status(self):
        return self._order_delivery_status

    @property
    def payment_status(self):
        return self._order_payment_status

    @staticmethod
    def validate_order_delivery_status(delivery_status: int) -> None:
        """Validates the order delivery status"""

        if delivery_status not in OrderDeliveryStatuses.values():
            raise StatusDoesNotExists

    @staticmethod
    def validate_order_pyment_status(payment_status: int) -> None:
        """Validates the order payment status"""

        if payment_status not in OrderPaymentStatus.values():
            raise StatusDoesNotExists

    @staticmethod
    def validate_customer_address(customer: Customer, address: CustomerAddress) -> None:
        """
        Validates the order delivery address validity.
        if the given does not belong the customer will be raised `InvalidAddress` exception
        """

        if not customer.is_address_valid(address):
            raise InvalidCustomerAddress

    def change_order_delivery_status(self, status: int) -> None:
        """Updates order delivery status"""
        if not self.items:
            raise ItemsDoNotFound

        self.validate_order_delivery_status(status)

        if self.ordered and status not in [
            OrderDeliveryStatuses.CANCELED.value,
            OrderDeliveryStatuses.DELIVERED.value,
            OrderDeliveryStatuses.RETURNED.value,
        ]:
            raise OrderAlreadyHasBeenPaid

        if status == OrderDeliveryStatuses.CANCELED.value:
            self._cancel_order()
        else:
            if status == self._order_delivery_status:
                logger.warning("You have updated the status repeatedly")
            self._order_delivery_status = status

    def change_order_payment_status(self, status: int) -> None:
        """Updates order payment status"""

        if not self.items:
            raise ItemsDoNotFound

        self.validate_order_pyment_status(status)

        if self.ordered and status not in [
            OrderPaymentStatus.CANCELED.value,
            OrderPaymentStatus.REFUNDED.value,
        ]:
            raise OrderAlreadyHasBeenPaid

        if status == OrderPaymentStatus.CANCELED.value:
            self._cancel_order()
        else:
            if status == self._order_payment_status:
                logger.warning("You have updated the status repeatedly")
            self._order_payment_status = status

        if self._order_payment_status == OrderPaymentStatus.PAID.value:
            self._ordered = True
        else:
            self._ordered = False

    def add_item(self, item: OrderItem) -> None:
        """Adds an item in order"""

        self.items.append(item)

    def remove_item(self, item_id: str) -> None:
        """Removes an item from the order"""

        self.items = list(filter(lambda x: x.id != item_id, self.items))

    def order_total(self) -> float:
        """Returns sum of items total amount"""

        return sum([item.item_total for item in self.items])

    def _cancel_order(self) -> None:
        """Cancels the order"""

        self._order_delivery_status = OrderDeliveryStatuses.CANCELED.value

        if self._order_payment_status == OrderPaymentStatus.PAID.value:
            self._order_payment_status = OrderPaymentStatus.REFUNDED.value
        else:
            self._order_payment_status = OrderPaymentStatus.CANCELED.value

    @staticmethod
    def get_customer_orders(customer_id: str) -> list:
        return list(
            filter(
                lambda x: x.customer.id == customer_id, order_instances.get_instances()
            )
        )

    @staticmethod
    def get_employee_orders(employee_id: str) -> list:
        return list(
            filter(
                lambda x: x.employee.id == employee_id, order_instances.get_instances()
            )
        )

    def __post_init__(self):
        self.validate_order_delivery_status(self.delivery_status)
        self.validate_order_pyment_status(self.payment_status)
        self.validate_customer_address(self.customer, self.customer_address)
        super().__post_init__()

    def rate_employee(self, rating: EmployeeRating) -> None:
        if (
            self.payment_status != OrderPaymentStatus.PAID.value
            and self.delivery_status != OrderDeliveryStatuses.DELIVERED.value
        ):
            raise RateError

        self.employee.rating = rating

        logger.info("Thank you for the review")

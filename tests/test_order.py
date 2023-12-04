from unittest import TestCase

from src.constants import OrderPaymentStatus, OrderDeliveryStatuses
from src.employee import (
    Employee,
    EmployeeDepartment,
    employee_instances,
    employee_department_instances,
    EmployeeRating,
    employee_rating_instances,
)
from src.exceptions import (
    StockQuantityIsNotEnough,
    StatusDoesNotExists,
    InvalidCustomerAddress,
    ItemsDoNotFound,
    OrderAlreadyHasBeenPaid,
    RateError,
)
from src.order import Order, OrderItem, order_instances
from src.product import Product, product_instances
from src.customer import (
    Customer,
    CustomerAddress,
    customer_instances,
    customer_address_instances,
)
from src.user import User, user_instances


class TestOrderItem(TestCase):
    def setUp(self):
        product_instances.set_empty_instances()

        self.product = Product(
            product_name="Some product",
            stock_qty=13,
            discount=10,
            price=45_000,
        )
        self.product1 = Product(
            product_name="Some product 1",
            stock_qty=15,
            discount=15,
            price=45_000,
        )

    def test_create_order_item_success(self):
        products = [self.product, self.product1]

        items = [
            OrderItem(
                product=product,
                qty=product.stock_qty - 1,
                item_price=product.final_price,
            )
            for product in products
        ]

        assert items[0].item_total == 12 * items[0].product.final_price

    def test_create_order_item_fail(self):
        try:
            OrderItem(
                product=self.product,
                qty=self.product.stock_qty + 1,
                item_price=self.product.final_price,
            )
        except Exception as e:
            assert isinstance(e, StockQuantityIsNotEnough)

    def test_create_order_item_fail_negative_qty(self):
        try:
            OrderItem(
                product=self.product,
                qty=-1,
                item_price=self.product.final_price,
            )
        except Exception as e:
            assert isinstance(e, ValueError)


class TestOrder(TestCase):
    user_fixture = {
        "first_name": "Gvido",
        "last_name": "Van Rosom",
        "email": "van.rosom@gmail.com",
        "phone_number": "+374747474",
    }

    def setUp(self):
        self.product = Product(
            product_name="Some product",
            stock_qty=13,
            discount=10,
            price=45_000,
        )
        self.product1 = Product(
            product_name="Some product 1",
            stock_qty=15,
            discount=15,
            price=45_000,
        )

        customer_user = User(**self.user_fixture)
        self.customer_address = CustomerAddress(address="Armenia, Yerevan")
        self.customer = Customer(user=customer_user, addresses=[self.customer_address])
        self.fail_customer_address = CustomerAddress(address="Fail address")
        self.customer.verify(self.customer.verification_code)

        new_fixture = self.user_fixture.copy()
        new_fixture["email"] = "test@mail.com"
        employee_user = User(**new_fixture)
        employee_department = EmployeeDepartment("Delivery")

        self.employee = Employee(
            absense_cost=1000,
            department=employee_department,
            num_absent=10,
            salary=200_000,
            user=employee_user,
        )

    def tearDown(self):
        order_instances.set_empty_instances()
        product_instances.set_empty_instances()
        customer_instances.set_empty_instances()
        customer_address_instances.set_empty_instances()
        user_instances.set_empty_instances()
        employee_instances.set_empty_instances()
        employee_department_instances.set_empty_instances()
        employee_rating_instances.set_empty_instances()

    def test_create_order_fail(self):
        try:
            Order(
                self.customer,
                customer_address=self.fail_customer_address,
                employee=self.employee,
            )
        except Exception as e:
            assert isinstance(e, InvalidCustomerAddress)

    def test_validate_order_delivery_status_invalid_status_exec(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 2,
            item_price=self.product.final_price,
        )

        order.add_item(item1)

        try:
            order.change_order_delivery_status(13)
        except Exception as e:
            assert isinstance(e, StatusDoesNotExists)

    def test_validate_order_payment_status_invalid_status_exec(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)

        try:
            order.change_order_payment_status(13)
        except Exception as e:
            print("Ok, STATUS")
            assert isinstance(e, StatusDoesNotExists)

    def test_validate_order_payment_status_no_items_exec(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        try:
            order.change_order_payment_status(OrderPaymentStatus.PAID.value)
        except Exception as e:
            assert isinstance(e, ItemsDoNotFound)

    def test_validate_order_delivery_status_no_items_exec(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        try:
            order.change_order_delivery_status(OrderDeliveryStatuses.WAITING.value)
        except Exception as e:
            assert isinstance(e, ItemsDoNotFound)

    def test_change_order_delivery_status(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)
        order.change_order_delivery_status(OrderDeliveryStatuses.IN_PROGRESS.value)
        assert order.delivery_status == OrderDeliveryStatuses.IN_PROGRESS.value

    def test_change_order_payment_status(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)
        order.change_order_payment_status(OrderPaymentStatus.WAITING.value)
        assert order.payment_status == OrderPaymentStatus.WAITING.value

    def test_add_order_item(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)

        assert len(order.items) == 1

    def test_remove_order_item(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)

        order.remove_item(item1.id)

        assert len(order.items) == 0

    def test_order_total_price(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)

        order_total = order.order_total()
        computed_total = self.product.final_price * (self.product.stock_qty - 3)

        assert order_total == computed_total

    def test_cancel_order(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)

        order.change_order_payment_status(OrderPaymentStatus.CANCELED.value)

        assert order.delivery_status == OrderDeliveryStatuses.CANCELED.value
        assert order.payment_status == OrderPaymentStatus.CANCELED.value

    def test_pay_order(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)
        order.change_order_payment_status(OrderPaymentStatus.PAID.value)

        assert order.ordered

    def test_raise_order_already_has_been_paid_payment_status(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)
        order.change_order_payment_status(OrderPaymentStatus.PAID.value)
        try:
            order.change_order_payment_status(OrderPaymentStatus.WAITING.value)
        except Exception as e:
            assert isinstance(e, OrderAlreadyHasBeenPaid)

    def test_raise_order_already_has_been_paid_delivery_status(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)
        order.change_order_payment_status(OrderPaymentStatus.PAID.value)
        try:
            order.change_order_delivery_status(OrderDeliveryStatuses.WAITING.value)
        except Exception as e:
            assert isinstance(e, OrderAlreadyHasBeenPaid)

    def test_cancel_and_refund_funds(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)
        order.change_order_payment_status(OrderPaymentStatus.PAID.value)
        order.change_order_payment_status(OrderPaymentStatus.CANCELED.value)

        assert order.payment_status == OrderPaymentStatus.REFUNDED.value

    def test_repeatedly_status_update(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)
        order.change_order_payment_status(OrderPaymentStatus.WAITING.value)
        # Will be printed this log `You have updated the status repeatedly`

        assert order.payment_status == OrderPaymentStatus.WAITING.value

    def test_cancel_order_in_delivery_status_change_fn(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)
        order.change_order_delivery_status(OrderDeliveryStatuses.CANCELED.value)

        assert order.delivery_status == OrderDeliveryStatuses.CANCELED.value

    def test_repeat_status_in_delivery_status_change_fn(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)
        order.change_order_delivery_status(OrderDeliveryStatuses.WAITING.value)
        # Will be printed log about the status

        assert order.delivery_status == OrderDeliveryStatuses.WAITING.value

    def test_rate_employee_exec(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)

        rating = EmployeeRating(value=4.7, message="Everything was ok.")

        try:
            order.rate_employee(rating)
        except Exception as e:
            assert isinstance(e, RateError)

    def test_rate_employee_success(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)
        order.change_order_payment_status(OrderPaymentStatus.PAID.value)
        order.change_order_delivery_status(OrderDeliveryStatuses.DELIVERED.value)

        rating = EmployeeRating(value=4.7, message="Everything was ok.")

        order.rate_employee(rating)

        assert order.employee.rating == 4.7

    def test_get_customer_orders_list(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)

        assert len(order.get_customer_orders(order.customer.id)) == 1

    def test_get_employee_orders_list(self):
        order = Order(
            self.customer,
            customer_address=self.customer_address,
            employee=self.employee,
        )

        item1 = OrderItem(
            product=self.product,
            qty=self.product.stock_qty - 3,
            item_price=self.product.final_price,
        )

        order.add_item(item1)

        assert len(order.get_employee_orders(order.employee.id)) == 1

from src.customer import Customer, CustomerAddress
from src.employee import EmployeeDepartment, Employee
from src.order import Order, OrderItem
from src.product import Product
from src.user import User


def main() -> None:
    user_fixture = {
        "first_name": "Gvido",
        "last_name": "Van Rosom",
        "email": "van.rosom@gmail.com",
        "phone_number": "+374747474",
    }

    product = Product(
        product_name="Some product",
        stock_qty=13,
        discount=10,
        price=45_000,
    )
    product1 = Product(
        product_name="Some product 1",
        stock_qty=15,
        discount=15,
        price=45_000,
    )

    customer_user = User(**user_fixture)
    customer_address = CustomerAddress(address="Armenia, Yerevan")
    customer = Customer(user=customer_user, addresses=[customer_address])
    customer.verify(customer.verification_code)
    new_fixture = user_fixture.copy()
    new_fixture["email"] = "test@mail.com"
    employee_user = User(**new_fixture)
    employee_department = EmployeeDepartment("Delivery")

    employee = Employee(
        absense_cost=1000,
        department=employee_department,
        num_absent=10,
        salary=200_000,
        user=employee_user,
    )
    order = Order(
        customer,
        customer_address=customer_address,
        employee=employee,
    )

    item1 = OrderItem(
        product=product,
        qty=product.stock_qty - 2,
        item_price=product.final_price,
    )
    item2 = OrderItem(
        product=product1,
        qty=product1.stock_qty - 2,
        item_price=product1.final_price,
    )

    order.add_item(item1)
    order.add_item(item2)


if __name__ == "__main__":
    main()
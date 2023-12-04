from unittest import TestCase

from src import exceptions
from src.customer import (
    CustomerAddress,
    Customer,
    customer_instances,
    customer_address_instances,
)
from src.exceptions import ObjectAlreadyExists
from src.user import User, user_instances
from src.constants import CustomerAddressActions


class TestCustomer(TestCase):
    user_fixture = {
        "first_name": "Gvido",
        "last_name": "Van Rosom",
        "email": "vanrosom2023@gmail.com",
        "phone_number": "+374747474",
    }

    def test_create_customer_success(self):
        user_instances.set_empty_instances()
        user = User(**self.user_fixture)
        customer = Customer(user=user)
        assert customer.id

    def test_create_customer_fail(self):
        try:
            user_instances.set_empty_instances()
            user = User(**self.user_fixture)
            Customer(user=user)
            Customer(user=user)
        except Exception as e:
            assert isinstance(e, ObjectAlreadyExists)

    def test_verify_customer_success(self):
        customer = customer_instances.get_instances()[-1]
        verification_code = customer.verification_code
        assert customer.is_verified is False
        customer.verify(verification_code)
        assert customer.is_verified is True
        assert customer.verification_code is None

    def test_verify_customer_fail(self):
        try:
            customer = list(
                filter(
                    lambda x: x.is_verified is False, customer_instances.get_instances()
                )
            )[0]
            verification_code = customer.verification_code
            assert customer.is_verified is False
            customer.verify(f"{verification_code}2")
        except Exception as e:
            assert isinstance(e, exceptions.NotPassedVerification)

    def test_reset_verification_code(self):
        customer = list(
            filter(lambda x: x.is_verified is False, customer_instances.get_instances())
        )[0]
        verification_code = customer.verification_code
        customer.request_verification_code()
        assert verification_code != customer.verification_code


class TestCustomerAddress(TestCase):
    def test_create_customer_address(self):
        location = "12/1 test st. Estonia, Talon"
        address = CustomerAddress(location)
        assert address.address == location

    def test_shift_customer_address(self):
        addresses = customer_address_instances.get_instances()
        customer = customer_instances.get_instances()[0]
        customer.handle_address(
            action=CustomerAddressActions.ADD.value, data=addresses[0]
        )
        assert len(customer.addresses) == 1

    def test_remove_customer_address(self):
        addresses = customer_address_instances.get_instances()
        customer = customer_instances.get_instances()[0]
        customer.handle_address(
            action=CustomerAddressActions.REMOVE.value, data=addresses[0].id
        )
        assert len(customer.addresses) == 0

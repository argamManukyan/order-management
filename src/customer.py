import asyncio
import logging
import random
from dataclasses import dataclass, field
from typing import Optional, Callable

from src.constants import CustomerAddressActions
from src.exceptions import NotPassedVerification
from src.helpers import send_email_data, BaseModel
from src.user import User
from src.management import InstanceManagement

logger = logging.getLogger()
customer_instances = InstanceManagement([])
customer_address_instances = InstanceManagement([])


@dataclass
class CustomerAddress(BaseModel):
    address: str
    __management_instance = customer_address_instances


@dataclass
class Customer(BaseModel):
    """Describes customer object"""

    user: User
    addresses: list[CustomerAddress] = field(default_factory=list)
    is_verified: bool = False
    verification_code: Optional[str] = None
    __management_instance = customer_instances

    def handle_address(self, action, data) -> list:
        """Sets new address and returns the user address list."""
        action_method = self._manage_addresses(action)
        action_method(data)
        return self.addresses

    def verify(self, code) -> bool:
        """Verifies the customer profile."""
        logger.info("Please make sure the given code is correct")
        if any([not self.verification_code, self.verification_code != code]):
            raise NotPassedVerification

        self.verification_code = None
        self.is_verified = True
        return True

    def request_verification_code(self) -> None:
        """Reset a new verification code for a user."""
        logger.info("Verification code has been generated")
        self._handle_verification_code()

    def add_address(self, address: str) -> None:
        """Appends a new address into addresses list."""
        self.addresses.append(CustomerAddress(address))

    def remove_address(self, address_id: str) -> None:
        """Removes an address with given address_id"""

        self.addresses = list(filter(lambda x: x.id != address_id, self.addresses))

    def is_address_valid(self, address: CustomerAddress) -> bool:
        return address in self.addresses

    def _manage_addresses(self, value) -> Callable[[str], None]:
        """Resolves and returns the responsible method to deal with addresses"""

        actions_facade = {
            CustomerAddressActions.ADD.value: self.add_address,
            CustomerAddressActions.REMOVE.value: self.remove_address
        }

        return actions_facade.get(value, None)

    def todo(self):
        """Here is commented upcoming integrations and features for this model"""

        # 1. Make a method to get order list or a service

    @staticmethod
    async def __mail_sender(code: str, recipients: list):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_email_data, code, recipients)

    def _handle_verification_code(self) -> None:
        """Generates and sends verification code to the user email."""

        self.verification_code = f"{random.randrange(10_000, 99_000)}"
        asyncio.run(self.__mail_sender(self.verification_code, [self.user.email]))
        logger.info("Emailing is on the process")

    def _validate_customer(self):
        """Validates customer by using the given user email address"""
        user_id = self.user.id

        _customer = len(list(filter(lambda x: x.user.id == user_id, customer_instances.get_instances()))) == 0
        if not _customer:
            raise ValueError
        return True

    def __post_init__(self):
        super().__post_init__()
        self._handle_verification_code()

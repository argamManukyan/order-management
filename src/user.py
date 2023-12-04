from dataclasses import dataclass
from src.helpers import BaseModel
from src.management import InstanceManagement

user_instances = InstanceManagement([])


@dataclass
class User(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: str
    __username: str = ''
    __management_instance = user_instances

    def _validate_user(self) -> bool:
        if len(list(filter(lambda x: x.username == self.username, user_instances.get_instances()))) > 0:
            raise ValueError

        return True

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, value):
        self.__username = value

    def __post_init__(self):
        self.username = self.email.split("@")[-1]
        super().__post_init__()

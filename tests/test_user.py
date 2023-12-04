from unittest import TestCase

from src.exceptions import ObjectAlreadyExists
from src.user import User, user_instances


class UserTest(TestCase):
    user_fixture = {
        "first_name": "Gvido",
        "last_name": "Van Rosom",
        "email": "gvido.vanrosom@python.org",
        "phone_number": "+374747474",
    }

    def test_create_user_success(self):
        user_instances.set_empty_instances()
        new_user = User(**self.user_fixture)
        username = self.user_fixture["email"].split("@")[-1]
        assert new_user.username == username

    def test_create_user_fail(self):
        try:
            User(**self.user_fixture)
            User(**self.user_fixture)
        except Exception as e:
            assert isinstance(e, ObjectAlreadyExists)

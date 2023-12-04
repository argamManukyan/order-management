import logging
from dataclasses import dataclass, field
from typing import Optional

from src.constants import MINIMUM_RATING
from src.management import InstanceManagement
from src.helpers import BaseModel
from src.user import User
from src.exceptions import FiredFromWorkException

logger = logging.getLogger()
employee_rating_instances = InstanceManagement([])
employee_department_instances = InstanceManagement([])
employee_instances = InstanceManagement([])


@dataclass
class EmployeeRating(BaseModel):
    """Employee rating model"""

    value: float
    message: Optional[str] = None
    __management_instance = employee_rating_instances


@dataclass
class EmployeeDepartment(BaseModel):
    """Employee department model"""

    name: str
    __management_instance = employee_department_instances

    def _validate_employeedepartment(self):
        """Validates and returns is there any employee department by the given name"""
        if (
            len(
                list(
                    filter(
                        lambda department: department.name == self.name,
                        self.__management_instance.get_instances(),
                    )
                )
            )
            > 0
        ):
            raise ValueError


@dataclass
class Employee(BaseModel):
    """Employee model"""

    user: User
    department: EmployeeDepartment
    salary: float
    num_absent: int
    absense_cost: float
    __blocked_for_a_week: bool = False
    __management_instance = employee_instances
    __rating: list[EmployeeRating] = field(default_factory=list)

    def block_user(self, trigger: bool) -> None:
        """Block / Unblock user"""

        self.__blocked_for_a_week = trigger

    def user_blocked(self) -> bool:
        """Returns user blocking state"""

        return self.__blocked_for_a_week

    @property
    def rating(self) -> float:
        """Returns average rating of an employee"""
        avg_rating = self._avg_rating()

        block_user = self._block_unblock_employee_trigger(avg_rating)
        self.block_user(block_user)

        if avg_rating < 2:
            logger.warning(
                "Please pay attention on your work. your rating has to be greater than `2`"
            )

        elif avg_rating > 4:
            logger.info(
                "Congrats you have worked well in this month. Please make this progress continued ..."
            )

        return self._avg_rating()

    @rating.setter
    def rating(self, data: EmployeeRating) -> None:
        """Sets new rating"""
        if not data.value > 0:
            raise ValueError("Value must be grater or equal 0")
        self.__rating.append(data)

    def _avg_rating(self) -> float:
        """Calculates avg of employee's rating"""
        return sum(i.value for i in self.__rating) / len(self.__rating)

    @staticmethod
    def _block_unblock_employee_trigger(rating: float) -> bool:
        """Returns is the employee middle rating less than minimal rating"""
        return rating < MINIMUM_RATING

    def _validate_employee(self) -> None:
        """Validates and returns is there any employee created by the given user"""

        user_email = self.user.email
        if (
            len(
                list(
                    filter(
                        lambda employee: employee.user.email == user_email,
                        employee_instances.get_instances(),
                    )
                )
            )
            > 0
        ):
            raise ValueError

    def _calculate_absense_sum(self) -> float:
        """Calculates and returns sum of absense hours expressed by dollars"""
        return self.absense_cost * self.num_absent

    def calculate_salary(self) -> Optional[float]:
        """Calculates employee hand on salary"""

        total_salary = self.salary - self._calculate_absense_sum()
        if total_salary <= 0:
            raise FiredFromWorkException

        return total_salary

import random
from unittest import TestCase

from src import exceptions
from src.employee import (
    Employee,
    EmployeeDepartment,
    employee_instances,
    employee_department_instances,
    EmployeeRating,
)
from src.user import user_instances, User


class TestEmployeeDepartment(TestCase):
    def test_create_employee_department(self):
        employee_department_instances.set_empty_instances()
        EmployeeDepartment(name="Programmer")
        assert len(employee_department_instances.get_instances()) == 1

    def test_create_employee_department_fail(self):
        try:
            EmployeeDepartment(name="Programmer")
        except Exception as e:
            assert isinstance(e, exceptions.ObjectAlreadyExists)


class TestEmployee(TestCase):
    user_fixture = {
        "first_name": "Gvido",
        "last_name": "Van Rosom",
        "email": "gvido12w.vanrosom@python.org",
        "phone_number": "+374747474",
    }

    salaries = [30_000, 40_000, 35_000, 400_000]

    def test_crate_employee_success(self):
        user_instances.set_empty_instances()
        employee_instances.set_empty_instances()

        user = User(**self.user_fixture)
        department = EmployeeDepartment(name="Programmer")
        calculated_salary = random.choice(self.salaries)
        employee = Employee(
            absense_cost=100,
            user=user,
            department=department,
            num_absent=0,
            salary=calculated_salary,
        )
        assert employee.salary == calculated_salary

    def test_create_employee_fail(self):
        user = user_instances.get_instances()[0]
        department = employee_department_instances.get_instances()[0]
        calculated_salary = random.choice(self.salaries)

        try:
            Employee(
                absense_cost=100,
                user=user,
                department=department,
                num_absent=0,
                salary=calculated_salary,
            )
        except Exception as e:
            assert isinstance(e, exceptions.ObjectAlreadyExists)

    def test_calculate_total_salary(self):
        user_instances.set_empty_instances()
        employee_instances.set_empty_instances()

        user = User(**self.user_fixture)
        department = employee_department_instances.get_instances()[0]
        calculated_salary = random.choice(self.salaries)
        employee = Employee(
            absense_cost=100,
            user=user,
            department=department,
            num_absent=2,
            salary=calculated_salary,
        )

        assert employee.calculate_salary() == calculated_salary - 200

    def test_fire_hauler_of_work(self):
        user = user_instances.get_instances()[0]
        employee_instances.set_empty_instances()
        department = employee_department_instances.get_instances()[0]
        calculated_salary = random.choice(self.salaries)

        try:
            employee = Employee(
                absense_cost=calculated_salary,
                user=user,
                department=department,
                num_absent=1,
                salary=calculated_salary,
            )
            employee.calculate_salary()
        except Exception as e:
            assert isinstance(e, exceptions.FiredFromWorkException)

    def test_rate_hauler(self):
        user = user_instances.get_instances()[0]
        employee_instances.set_empty_instances()
        department = employee_department_instances.get_instances()[0]
        calculated_salary = random.choice(self.salaries)

        employee = Employee(
            absense_cost=0.2,
            user=user,
            department=department,
            num_absent=10,
            salary=calculated_salary,
        )

        rating_value = EmployeeRating(
            value=5,
            message="The food has been delivered on time. But supplier did not have billing.",
        )

        employee.rating = rating_value
        assert employee.rating == 5
        assert employee.user_blocked() is False

    def test_rate_hauler_fail(self):
        user = user_instances.get_instances()[0]
        employee_instances.set_empty_instances()
        department = employee_department_instances.get_instances()[0]
        calculated_salary = random.choice(self.salaries)

        employee = Employee(
            absense_cost=0.2,
            user=user,
            department=department,
            num_absent=10,
            salary=calculated_salary,
        )

        rating_value = EmployeeRating(value=-1)
        try:
            employee.rating = rating_value
        except Exception as e:
            assert isinstance(e, ValueError)

    def test_block_employee_for_a_week(self):
        user = user_instances.get_instances()[0]
        employee_instances.set_empty_instances()
        department = EmployeeDepartment(name="Accountant")
        calculated_salary = random.choice(self.salaries)

        employee = Employee(
            absense_cost=0.2,
            user=user,
            department=department,
            num_absent=10,
            salary=calculated_salary,
        )
        rating = EmployeeRating(value=1)

        employee.rating = rating
        employee.rating = rating
        assert employee.rating == 1
        assert employee.user_blocked()

from django.contrib.auth import get_user_model
from django.db import models

from bases.models import BaseIdentification

User = get_user_model()


class Employee(BaseIdentification):
    class DesignationChoice(models.TextChoices):
        TRAINER = 'trainer'
        ADMINISTRATOR = 'administrator'
        MANAGER = 'manager'
        ACCOUNTANT = 'accountant'
        EMPLOYEE = 'Employee'

    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name="employee_info")
    designation = models.CharField(max_length=16, choices=DesignationChoice.choices, default=DesignationChoice.EMPLOYEE)
    total_salary = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    hourly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=1)

    def __str__(self):
        return self.user.username

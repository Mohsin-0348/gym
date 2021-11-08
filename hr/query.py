
import graphene
from graphene_django.filter import DjangoFilterConnectionField

from backend.permissions import is_admin_user
from hr.models import Employee
from hr.object_types import EmployeeType


class Query(graphene.ObjectType):
    employee = graphene.relay.Node.Field(EmployeeType)
    all_employees = DjangoFilterConnectionField(EmployeeType)

    @is_admin_user
    def resolve_all_employees(self, info, **kwargs) -> object:
        return Employee.objects.all()

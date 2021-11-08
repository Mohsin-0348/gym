
import graphene
from graphene_django import DjangoObjectType

from backend.count_connection import CountConnection
from hr.filters import EmployeeFilters
from hr.models import Employee


class EmployeeType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = Employee
        filterset_class = EmployeeFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id

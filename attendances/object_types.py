import graphene
from graphene_django import DjangoObjectType

from attendances.filters import (
    ClassAttendanceFilters,
    ClassWorkOutFilters,
    EmployeeAttendanceFilters,
    GymAttendanceFilters,
    GymWorkOutFilters,
    WorkOutFilters,
)
from attendances.models import (
    ClassAttendance,
    ClassWorkOut,
    EmployeeAttendance,
    GymAttendance,
    GymWorkOut,
    WorkOut,
)
from backend.count_connection import CountConnection


class WorkOutType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = WorkOut
        filterset_class = WorkOutFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class ClassWorkOutType(DjangoObjectType):
    object_id = graphene.ID()
    burnt_calorie = graphene.Float()

    class Meta:
        model = ClassWorkOut
        filterset_class = ClassWorkOutFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id

    @staticmethod
    def resolve_burnt_calorie(self, info, **kwargs):
        return self.burnt_calorie


class GymWorkOutType(DjangoObjectType):
    object_id = graphene.ID()
    burnt_calorie = graphene.Float()

    class Meta:
        model = GymWorkOut
        filterset_class = GymWorkOutFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id

    @staticmethod
    def resolve_burnt_calorie(self, info, **kwargs):
        return self.burnt_calorie


class GymAttendanceType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = GymAttendance
        filterset_class = GymAttendanceFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class ClassAttendanceType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = ClassAttendance
        filterset_class = ClassAttendanceFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class EmployeeAttendanceType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = EmployeeAttendance
        filterset_class = EmployeeAttendanceFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id

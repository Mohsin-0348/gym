
import graphene
from graphene_django import DjangoObjectType

from backend.count_connection import CountConnection
from classes.filters import ClassBookingFilters, ClassFilters, ScheduledClassFilters
from classes.models import BaseClass, ClassBooking, ClassSchedule, WeekDay


class WeekDayType(DjangoObjectType):

    class Meta:
        model = WeekDay
        fields = ('id', 'day')
        convert_choices_to_enum = True


class ClassType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = BaseClass
        filterset_class = ClassFilters
        interfaces = (graphene.relay.Node, )
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class ClassScheduleType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = ClassSchedule
        filterset_class = ScheduledClassFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class ClassBookingType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = ClassBooking
        filterset_class = ClassBookingFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id

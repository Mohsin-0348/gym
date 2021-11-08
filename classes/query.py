
import graphene
from graphene_django.filter import DjangoFilterConnectionField

from backend.permissions import is_admin_user, is_authenticated
from classes.models import BaseClass, ClassBooking, ClassSchedule, WeekDay
from classes.object_types import (
    ClassBookingType,
    ClassScheduleType,
    ClassType,
    WeekDayType,
)
from hr.models import Employee
from members.models import Member

# from users.models import UserProfile


class Query(graphene.ObjectType):
    weekdays = graphene.List(WeekDayType)
    base_class = graphene.relay.Node.Field(ClassType)
    all_classes = DjangoFilterConnectionField(ClassType)
    scheduled_class = graphene.relay.Node.Field(ClassScheduleType)
    all_scheduled_classes = DjangoFilterConnectionField(ClassScheduleType)
    class_booking = graphene.relay.Node.Field(ClassBookingType)
    all_class_bookings = DjangoFilterConnectionField(ClassBookingType)

    @is_admin_user
    def resolve_weekdays(self, info, **kwargs):
        return WeekDay.objects.all()

    @is_authenticated
    def resolve_all_classes(self, info, **kwargs):
        return BaseClass.objects.all()

    @is_authenticated
    def resolve_all_scheduled_classes(self, info, **kwargs):
        user = info.context.user
        if not user.is_staff:
            employee = Employee.objects.filter(user=user)
            if employee and employee.first().designation == Employee.DesignationChoice.TRAINER:
                return ClassSchedule.objects.filter(trainer=employee.first())
            return ClassSchedule.objects.filter(postponed=False)
        return ClassSchedule.objects.all()

    @is_authenticated
    def resolve_all_class_bookings(self, info, **kwargs):
        user = info.context.user
        if not user.is_staff:
            member_user, created = Member.objects.get_or_create(user=user)
            return ClassBooking.objects.filter(member=member_user)
        return ClassBooking.objects.all()

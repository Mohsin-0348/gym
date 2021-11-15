
import django_filters

from attendances.models import (
    ClassAttendance,
    ClassWorkOut,
    EmployeeAttendance,
    GymAttendance,
    GymWorkOut,
    WorkOut,
)
from bases.filters import BaseFilters


class WorkOutFilters(BaseFilters):
    """Work out Filter will define here"""
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    uom = django_filters.CharFilter(
        field_name='uom',
        lookup_expr='icontains'
    )

    class Meta:
        model = WorkOut
        fields = [
            'id',
            'name',
            'uom',
        ]


class ClassWorkOutFilters(BaseFilters):
    """Class Work out Filter will define here"""
    class_attendance = django_filters.CharFilter(
        field_name='class_attendance__base_class__name',
        lookup_expr='icontains'
    )
    base_type = django_filters.CharFilter(
        field_name='base_type__name',
        lookup_expr='icontains'
    )

    class Meta:
        model = ClassWorkOut
        fields = [
            'id',
            'class_attendance',
            'base_type',
        ]


class GymWorkOutFilters(BaseFilters):
    """
        Gym Work out Filter will define here
    """

    gym_attendance = django_filters.CharFilter(
        field_name='gym_attendance__id',
        lookup_expr='icontains'
    )
    base_type = django_filters.CharFilter(
        field_name='base_type__name',
        lookup_expr='icontains'
    )

    class Meta:
        model = GymWorkOut
        fields = [
            'id',
            'gym_attendance',
            'base_type',
        ]


class GymAttendanceFilters(BaseFilters):
    """
        Gym attendance Filter will define here
    """

    member = django_filters.CharFilter(
        field_name='member__user__username',
        lookup_expr='icontains'
    )

    class Meta:
        model = GymAttendance
        fields = [
            'id',
            'member',
        ]


class EmployeeAttendanceFilters(BaseFilters):
    """
        Employee attendance Filter will define here
    """

    member = django_filters.CharFilter(
        field_name='member__user__username',
        lookup_expr='icontains'
    )

    class Meta:
        model = EmployeeAttendance
        fields = [
            'id',
            'member',
        ]


class ClassAttendanceFilters(BaseFilters):
    """
        Gym attendance Filter will define here
    """

    class_schedule = django_filters.CharFilter(
        field_name='class_schedule__base_class',
        lookup_expr='icontains'
    )

    class Meta:
        model = ClassAttendance
        fields = [
            'id',
            'class_schedule',
        ]

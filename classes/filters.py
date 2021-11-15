
import django_filters

from bases.filters import BaseFilters
from classes.models import BaseClass, ClassBooking, ClassSchedule


class ClassFilters(BaseFilters):
    """
        Class Filter will define here.
    """
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    weekday = django_filters.CharFilter(
        field_name='weekday__day',
        lookup_expr='exact'
    )
    gender_type = django_filters.CharFilter(
        field_name='gender_type',
        lookup_expr='exact'
    )

    class Meta:
        model = BaseClass
        fields = [
            'id',
            'name',
            'weekday',
            'gender_type',
            'single_class',
        ]


class ScheduledClassFilters(BaseFilters):
    """
        Class schedule Filter will define here.
    """
    base_class = django_filters.CharFilter(
        field_name='base_class__name',
        lookup_expr='icontains'
    )
    trainer = django_filters.CharFilter(
        field_name='trainer__user__username',
        lookup_expr='icontains'
    )
    date = django_filters.CharFilter(
        field_name='date',
        lookup_expr='exact'
    )

    class Meta:
        model = ClassSchedule
        fields = [
            'id',
            'base_class',
            'trainer',
            'date',
            'postponed',
        ]


class ClassBookingFilters(BaseFilters):
    """
        Class booking Filter will define here.
    """
    member = django_filters.CharFilter(
        field_name='member__user__username',
        lookup_expr='icontains'
    )
    scheduled_class = django_filters.CharFilter(
        field_name='scheduled_class__base_class__name',
        lookup_expr='exact'
    )

    class Meta:
        model = ClassBooking
        fields = [
            'id',
            'member',
            'scheduled_class',
        ]

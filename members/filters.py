
import django_filters

from bases.filters import BaseFilters
from members.models import (
    Food,
    FoodsConsumed,
    FoodToEat,
    Member,
    NutritionPlan,
    TrackBodyMeasurement,
    TrackNutritionPlan,
)


class MemberFilters(BaseFilters):
    """UserFilter will define here"""
    height = django_filters.CharFilter(
        field_name='height',
        lookup_expr='exact'
    )
    chest = django_filters.CharFilter(
        field_name='chest',
        lookup_expr='exact'
    )
    weight = django_filters.CharFilter(
        field_name='weight',
        lookup_expr='exact'
    )

    class Meta:
        model = Member
        fields = [
            'id',
            'height',
            'chest',
            'weight',
        ]


class FoodFilters(BaseFilters):
    """UserFilter will define here"""
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    uom = django_filters.CharFilter(
        field_name='uom',
        lookup_expr='icontains'
    )
    base_amount = django_filters.CharFilter(
        field_name='base_amount',
        lookup_expr='exact'
    )

    class Meta:
        model = Food
        fields = [
            'id',
            'name',
            'uom',
            'base_amount',
        ]


class NutritionPlanFilters(BaseFilters):
    """UserFilter will define here"""
    member = django_filters.CharFilter(
        field_name='member__user__username',
        lookup_expr='icontains'
    )
    meal_type = django_filters.CharFilter(
        field_name='meal_type',
        lookup_expr='icontains'
    )

    class Meta:
        model = NutritionPlan
        fields = [
            'id',
            'member',
            'meal_type',
        ]


class FoodToEatFilters(BaseFilters):
    """UserFilter will define here"""
    plan = django_filters.CharFilter(
        field_name='plan__meal_type',
        lookup_expr='icontains'
    )
    food = django_filters.CharFilter(
        field_name='food__name',
        lookup_expr='icontains'
    )
    amount = django_filters.CharFilter(
        field_name='amount',
        lookup_expr='exact'
    )

    class Meta:
        model = FoodToEat
        fields = [
            'id',
            'plan',
            'food',
            'amount',
        ]


class FoodConsumedFilters(BaseFilters):
    """UserFilter will define here"""
    plan = django_filters.CharFilter(
        field_name='plan__meal_type',
        lookup_expr='icontains'
    )
    food = django_filters.CharFilter(
        field_name='food__name',
        lookup_expr='icontains'
    )
    amount = django_filters.CharFilter(
        field_name='amount',
        lookup_expr='exact'
    )

    class Meta:
        model = FoodsConsumed
        fields = [
            'id',
            'plan',
            'food',
            'amount',
        ]


class TrackNutritionPlanFilters(BaseFilters):
    """UserFilter will define here"""
    plan = django_filters.CharFilter(
        field_name='plan__meal_type',
        lookup_expr='icontains'
    )

    class Meta:
        model = TrackNutritionPlan
        fields = [
            'id',
            'plan',
        ]


class BodyMeasurementFilters(BaseFilters):
    """body measurement Filter will define here"""
    height = django_filters.CharFilter(
        field_name='height',
        lookup_expr='exact'
    )
    chest = django_filters.CharFilter(
        field_name='chest',
        lookup_expr='exact'
    )
    weight = django_filters.CharFilter(
        field_name='weight',
        lookup_expr='exact'
    )

    class Meta:
        model = TrackBodyMeasurement
        fields = [
            'id',
            'height',
            'chest',
            'weight',
        ]

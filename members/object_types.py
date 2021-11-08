
import graphene
from graphene_django import DjangoObjectType

from backend.count_connection import CountConnection
from members.filters import (
    BodyMeasurementFilters,
    FoodConsumedFilters,
    FoodFilters,
    FoodToEatFilters,
    MemberFilters,
    NutritionPlanFilters,
    TrackNutritionPlanFilters,
)
from members.models import (
    Food,
    FoodsConsumed,
    FoodToEat,
    Member,
    NutritionPlan,
    TrackBodyMeasurement,
    TrackNutritionPlan,
)


class FoodType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = Food
        filterset_class = FoodFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class NutritionPlanType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = NutritionPlan
        filterset_class = NutritionPlanFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class FoodToEatType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = FoodToEat
        filterset_class = FoodToEatFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class FoodsConsumedType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = FoodsConsumed
        filterset_class = FoodConsumedFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class TrackNutritionPlanType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = TrackNutritionPlan
        filterset_class = TrackNutritionPlanFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class BodyMeasurementType(DjangoObjectType):
    object_id = graphene.ID()

    class Meta:
        model = TrackBodyMeasurement
        filterset_class = BodyMeasurementFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class MemberType(DjangoObjectType):
    object_id = graphene.ID()
    current_body_measurement = graphene.Field(BodyMeasurementType)

    class Meta:
        model = Member
        filterset_class = MemberFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id

    @staticmethod
    def resolve_current_body_measurement(self, info, **kwargs):
        return self.current_body_measurement

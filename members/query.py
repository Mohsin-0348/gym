
import graphene

# from django.contrib.auth import get_user_model
from graphene_django.filter import DjangoFilterConnectionField

from backend.permissions import is_authenticated
from members.models import (  # FoodsConsumed,; FoodToEat,
    Food,
    Member,
    NutritionPlan,
    TrackBodyMeasurement,
    TrackNutritionPlan,
)
from members.object_types import (  # FoodsConsumedType,; FoodToEatType,; MemberType,
    BodyMeasurementType,
    FoodType,
    NutritionPlanType,
    TrackNutritionPlanType,
)


class Query(graphene.ObjectType):
    food = graphene.relay.Node.Field(FoodType)
    all_foods = DjangoFilterConnectionField(FoodType)
    nutrition_plan = graphene.relay.Node.Field(NutritionPlanType)
    all_nutrition_plans = DjangoFilterConnectionField(NutritionPlanType)
    track_nutrition_plan = graphene.relay.Node.Field(TrackNutritionPlanType)
    all_track_nutrition_plans = DjangoFilterConnectionField(TrackNutritionPlanType)
    body_measurement_track = graphene.relay.Node.Field(BodyMeasurementType)
    all_body_measurement_tracks = DjangoFilterConnectionField(BodyMeasurementType)

    @is_authenticated
    def resolve_foods(self, info, **kwargs) -> object:
        return Food.objects.all()

    @is_authenticated
    def resolve_all_nutrition_plans(self, info, **kwargs) -> object:
        user = info.context.user
        if not user.is_staff:
            member_user, created = Member.objects.get_or_create(user=user)
            return NutritionPlan.objects.filter(member=member_user)
        return NutritionPlan.objects.all()

    @is_authenticated
    def resolve_all_track_nutrition_plans(self, info, **kwargs) -> object:
        user = info.context.user
        if not user.is_staff:
            member_user, created = Member.objects.get_or_create(user=user)
            return TrackNutritionPlan.objects.filter(plan__member=member_user)
        return TrackNutritionPlan.objects.all()

    @is_authenticated
    def resolve_all_body_measurement_tracks(self, info, **kwargs) -> object:
        user = info.context.user
        if not user.is_staff:
            member_user, created = Member.objects.get_or_create(user=user)
            return TrackBodyMeasurement.objects.filter(member=member_user)
        return TrackBodyMeasurement.objects.all()

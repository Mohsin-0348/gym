import datetime

import graphene
from django.forms import model_to_dict
from django.utils import timezone
from graphene_django.forms.mutation import DjangoFormMutation
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from backend.permissions import is_admin_user, is_authenticated
from bases.constants import HistoryActions

# from hr.models import Employee
from members.forms import (  # BodyMeasurementForm,; TrackNutritionPlanForm,
    FoodForm,
    FoodsConsumedForm,
    FoodToEatForm,
    MemberForm,
    NutritionPlanForm,
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
from members.object_types import (  # MemberType,
    BodyMeasurementType,
    FoodsConsumedType,
    FoodToEatType,
    FoodType,
    NutritionPlanType,
    TrackNutritionPlanType,
)
from members.utils import check_trainer
from users.models import UnitOfHistory
from users.object_types import UserType


class UpdateMemberMutation(DjangoFormMutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    class Meta:
        form_class = MemberForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        user = info.context.user
        form = MemberForm(data=input)
        member_user, created = Member.objects.get_or_create(user=user)
        if form.is_valid():
            Member.objects.filter(id=member_user.id).update(**form.cleaned_data)

        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[error] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        UnitOfHistory.user_history(
            action=HistoryActions.MEMBER_INFO_UPDATE,
            user=user,
            request=info.context
        )

        return UpdateMemberMutation(success=True, message="User info updated", user=user)


class FoodMutation(DjangoFormMutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    food = graphene.Field(FoodType)

    class Meta:
        form_class = FoodForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = FoodForm(data=input)
        object_id = None
        if form.data.get('object_id'):
            object_id = form.data['object_id']
            obj = Food.objects.get(id=object_id)
            form = FoodForm(data=input, instance=obj)
        if form.is_valid():
            obj, created = Food.objects.update_or_create(id=object_id, defaults=form.cleaned_data)
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[error] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        return FoodMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", food=obj
        )


class ObjectInput(graphene.InputObjectType):
    object_id = graphene.ID()


class DeleteFood(graphene.Mutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        object_list = graphene.List(ObjectInput)
        delete_anyway = graphene.Boolean()

    @is_admin_user
    def mutate(self, info, object_list, delete_anyway=False, **kwargs):
        user = info.context.user
        object_list = [obj['object_id'] for obj in object_list]
        foods = Food.objects.filter(id__in=object_list)
        if len(object_list) != len(foods):
            invalid_list = list(filter(lambda x: (x not in foods.values_list('id', flat=True)), object_list))
            raise GraphQLError(
                message=f"Please use valid object-id. ('{invalid_list[-1]}' is invalid)",
                extensions={
                    "errors": f"Please use valid object-id. ('{invalid_list[-1]}' is invalid)",
                    "code": "invalid_request"
                }
            )
        if not delete_anyway:
            for obj in foods:
                if FoodToEat.objects.filter(food=obj) or FoodToEat.objects.filter(food=obj):
                    raise GraphQLError(
                        message=f"Food object({obj.id}) in use.",
                        extensions={
                            "errors": f"Food object({obj.id}) in use.",
                            "code": "invalid_request"
                        }
                    )
        for obj in foods:
            UnitOfHistory.user_history(
                action=HistoryActions.DELETE_FOOD,
                old_meta=model_to_dict(obj),
                user=user,
                request=info.context
            )
        foods.delete()
        return DeleteFood(success=True, message="Successfully deleted.")


class NutritionPlanMutation(DjangoFormMutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    plan_object = graphene.Field(NutritionPlanType)

    class Meta:
        form_class = NutritionPlanForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        trainer = check_trainer(info.context.user)
        form = NutritionPlanForm(data=input)
        if form.is_valid():
            form.cleaned_data['updated_by'] = trainer
            if not form.cleaned_data['object_id']:
                form.cleaned_data['added_by'] = trainer
                exist_plan = NutritionPlan.objects.filter(member=form.cleaned_data['member'],
                                                          meal_type=form.cleaned_data['meal_type'])
                if exist_plan and not exist_plan.first().complete_status:
                    raise GraphQLError(
                        message="Plan is already added for this meal type. User can update that one.",
                        extensions={
                            "errors": {'track': "Plan is already added for this meal type. User can update that one."},
                            "code": "invalid_request"
                        }
                    )

            obj, created = NutritionPlan.objects.update_or_create(
                id=form.cleaned_data['object_id'], defaults=form.cleaned_data
            )
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[error] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        return NutritionPlanMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}.", plan_object=obj
        )


class DiscardNutritionPlan(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    plan = graphene.Field(NutritionPlanType)

    class Arguments:
        object_id = graphene.ID()

    @is_authenticated
    def mutate(self, info, object_id, **kwargs):
        user = info.context.user
        check_trainer(user)
        plan_obj = NutritionPlan.objects.get(id=object_id)
        plan_obj.end_date = timezone.now().date() - datetime.timedelta(days=1)
        plan_obj.save()
        return DiscardNutritionPlan(success=True, message="Successfully discarded.", plan=plan_obj)


class FoodToEatMutation(DjangoFormMutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    food_to_eat = graphene.Field(FoodToEatType)

    class Meta:
        form_class = FoodToEatForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        check_trainer(info.context.user)
        form = FoodToEatForm(data=input)
        object_id = None
        if form.data.get('object_id'):
            obj = FoodToEat.objects.get(id=form.data['object_id'])
            object_id = obj.id
            form = FoodToEatForm(data=input, instance=obj)
        if form.is_valid():
            del form.cleaned_data['object_id']
            if not form.cleaned_data['plan'].complete_status:
                raise GraphQLError(
                    message="Plan was completed. If needed please update plan first.",
                    extensions={
                        "errors": {'plan': "Plan was completed. If needed please update plan first."},
                        "code": "invalid_request"
                    }
                )
            obj, created = FoodToEat.objects.update_or_create(
                id=object_id, defaults=form.cleaned_data
            )
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[error] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        return FoodToEatMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}.", food_to_eat=obj
        )


class DeleteFoodToEat(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        object_id = graphene.ID()

    @is_authenticated
    def mutate(self, info, object_id, **kwargs):
        user = info.context.user
        check_trainer(user)
        obj = FoodToEat.objects.get(id=object_id)
        if not obj.plan.complete_status:
            raise GraphQLError(
                message="Plan was completed. If needed please update plan first.",
                extensions={
                    "errors": {'plan': "Plan was completed. If needed please update plan first."},
                    "code": "invalid_request"
                }
            )
        obj.delete()
        return DeleteFoodToEat(success=True, message="Successfully deleted.")


class TrackNutritionPlanMutation(graphene.Mutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    track_object = graphene.Field(TrackNutritionPlanType)

    class Arguments:
        object_id = graphene.ID()
        plan = graphene.ID()
        photo = Upload()

    @is_authenticated
    def mutate(self, info, plan, photo=None, object_id=None, **kwargs):
        user = info.context.user
        member_user, created = Member.objects.get_or_create(user=user)
        plan = NutritionPlan.objects.get(id=plan)
        if plan.member != member_user or not plan.complete_status:
            raise GraphQLError(
                message="Select a valid choice. That choice is not one of the available choices.",
                extensions={
                    "errors": {'plan': "Select a valid choice. That choice is not one of the available choices."},
                    "code": "invalid_input"
                }
            )
        if object_id and TrackNutritionPlan.objects.get(id=object_id).created_on.date() < timezone.now().date():
            raise GraphQLError(
                message="User can update a track on the following day only.",
                extensions={
                    "errors": {'plan': "User can update a track on the following day only."},
                    "code": "invalid_request"
                }
            )
        if not object_id and TrackNutritionPlan.objects.filter(plan=plan, created_on__date=timezone.now().date()):
            raise GraphQLError(
                message="Today's track for this meal already added. You can update that one.",
                extensions={
                    "errors": {'plan': "Today's track for this meal already added. You can update that one."},
                    "code": "invalid_request"
                }
            )
        obj, created = TrackNutritionPlan.objects.update_or_create(
            id=object_id, defaults={'plan': plan, 'photo': photo}
        )
        return TrackNutritionPlanMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}.", track_object=obj
        )


class ConsumedFoodMutation(DjangoFormMutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    consumed_object = graphene.Field(FoodsConsumedType)

    class Meta:
        form_class = FoodsConsumedForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        form = FoodsConsumedForm(data=input)
        object_id = None
        if form.data.get('object_id'):
            obj = FoodsConsumed.objects.get(id=form.data['object_id'])
            object_id = obj.id
            form = FoodToEatForm(data=input, instance=obj)
        if form.is_valid():
            del form.cleaned_data['object_id']
            if form.cleaned_data['plan_track'].created_on.date() < timezone.now().date():
                raise GraphQLError(
                    message="User can update a track on the following day only.",
                    extensions={
                        "errors": {'plan_track': "User can update a track on the following day only."},
                        "code": "invalid_request"
                    }
                )
            obj, created = FoodsConsumed.objects.update_or_create(
                id=object_id, defaults=form.cleaned_data
            )
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[error] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        return ConsumedFoodMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}.", consumed_object=obj
        )


class DeleteConsumedFood(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        object_id = graphene.ID()

    @is_authenticated
    def mutate(self, info, object_id, **kwargs):
        user = info.context.user
        member_user, created = Member.objects.get_or_create(user=user)
        obj = FoodsConsumed.objects.get(id=object_id, plan_track__plan__member=member_user)
        if obj.plan_track.created_on.date() < timezone.now().date():
            raise GraphQLError(
                message="User can update a track on the following day only.",
                extensions={
                    "errors": {'plan_track': "User can update a track on the following day only."},
                    "code": "invalid_request"
                }
            )
        obj.delete()
        return DeleteConsumedFood(success=True, message="Successfully deleted.")


class BodyMeasurementInput(graphene.InputObjectType):
    object_id = graphene.ID(required=False)
    photo = Upload(required=False)
    weight = graphene.Float(required=True)
    height = graphene.Float(required=True)
    chest = graphene.Float(required=True)
    neck = graphene.Float(required=False)
    left_arm = graphene.Float(required=False)
    right_arm = graphene.Float(required=False)
    waist = graphene.Float(required=False)
    hips = graphene.Float(required=False)
    left_thigh = graphene.Float(required=False)
    right_thigh = graphene.Float(required=False)
    left_calf = graphene.Float(required=False)
    right_calf = graphene.Float(required=False)


class TrackBodyMeasurementMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    track_object = graphene.Field(BodyMeasurementType)

    class Arguments:
        input = BodyMeasurementInput(required=True)

    @is_authenticated
    def mutate(self, info, input, **kwargs):
        user = info.context.user
        member_user, created = Member.objects.get_or_create(user=user)
        input['member'] = member_user
        object_id = None
        if input.get('object_id'):
            object_id = input['object_id']
            TrackBodyMeasurement.objects.get(id=object_id, member=member_user)
            del input['object_id']
        if object_id and TrackBodyMeasurement.objects.get(
                id=object_id).created_on.date() < timezone.now().date():
            raise GraphQLError(
                message="User can update a track on the following day only.",
                extensions={
                    "errors": {'track': "User can update a track on the following day only."},
                    "code": "invalid_request"
                }
            )
        if not object_id and TrackBodyMeasurement.objects.filter(member=member_user,
                                                                 created_on__date=timezone.now().date()):
            raise GraphQLError(
                message="Today's track is already added. User can update that one.",
                extensions={
                    "errors": {'track': "Today's track is already added. User can update that one."},
                    "code": "invalid_request"
                }
            )
        obj, created = TrackBodyMeasurement.objects.update_or_create(
            id=object_id, defaults=input
        )
        return TrackBodyMeasurementMutation(
            success=True, track_object=obj, message=f"Successfully {'added' if created else 'updated'}."
        )


class Mutation(graphene.ObjectType):
    update_member_info = UpdateMemberMutation.Field()
    food_mutation = FoodMutation.Field()
    delete_food = DeleteFood.Field()
    nutrition_plan_mutation = NutritionPlanMutation.Field()
    discard_nutrition_plan = DiscardNutritionPlan.Field()
    food_to_eat_mutation = FoodToEatMutation.Field()
    delete_food_to_eat = DeleteFoodToEat.Field()
    track_nutrition_plan_mutation = TrackNutritionPlanMutation.Field()
    consumed_food_mutation = ConsumedFoodMutation.Field()
    delete_consumed_food = DeleteConsumedFood.Field()
    track_body_measurement_mutation = TrackBodyMeasurementMutation.Field()

import datetime

import graphene
from django.utils import timezone
from graphene_django.forms.mutation import DjangoFormMutation
from graphql import GraphQLError

from backend.permissions import is_admin_user, is_authenticated
from classes.forms import (
    ClassBookingForm,
    ClassForm,
    ClassScheduleForm,
    ClassScheduleUpdateForm,
    WeekDayForm,
)
from classes.models import BaseClass, ClassBooking, ClassSchedule, WeekDay
from classes.object_types import (  # ClassScheduleType,
    ClassBookingType,
    ClassType,
    WeekDayType,
)
from members.models import Member
from members.utils import check_trainer
from users.choices import RoleChoices
from users.models import UserProfile


class WeekDayMutation(DjangoFormMutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    day_object = graphene.Field(WeekDayType)

    class Meta:
        form_class = WeekDayForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = WeekDayForm(data=input)
        object_id = None
        if form.data.get('object_id'):
            obj = WeekDay.objects.get(id=form.data['object_id'])
            object_id = obj.id
            form = WeekDayForm(data=input, instance=obj)
        if form.is_valid():
            del form.cleaned_data['object_id']
            obj, created = WeekDay.objects.update_or_create(
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
        return WeekDayMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}.", day_object=obj
        )


class ClassMutation(DjangoFormMutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    class_object = graphene.Field(ClassType)

    class Meta:
        form_class = ClassForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = ClassForm(data=input)
        object_id = None
        if form.data.get('object_id'):
            obj = BaseClass.objects.get(id=form.data['object_id'])
            object_id = obj.id
            form = ClassForm(data=input, instance=obj)
        if form.is_valid():
            weekday = form.cleaned_data['weekday']
            if not form.cleaned_data['single_class'] and not form.cleaned_data['weekday']:
                raise GraphQLError(
                    message="Should select weekday.",
                    extensions={
                        "errors": {'weekday': "Should select weekday."},
                        "code": "invalid_input"
                    }
                )
            del form.cleaned_data['object_id'], form.cleaned_data['weekday']
            obj, created = BaseClass.objects.update_or_create(
                id=object_id, defaults=form.cleaned_data
            )
            for day in weekday:
                obj.weekday.add(day)
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
        return ClassMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}.", class_object=obj
        )


class ClassBookingMutation(graphene.Mutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    class_booking_object = graphene.Field(ClassBookingType)

    class Arguments:
        object_id = graphene.ID(required=False)
        scheduled_class = graphene.ID()

    @is_authenticated
    def mutate(self, info, scheduled_class, object_id=None, **kwargs):
        user_profile = UserProfile.objects.filter(user=info.context.user)
        # ::ToDo -> will check for active package/membership
        scheduled_class = ClassSchedule.objects.get(id=scheduled_class, postponed=False)
        if not user_profile or (user_profile and user_profile.first().role != RoleChoices.MEMBER):
            raise GraphQLError(
                message="Member should update profile.",
                extensions={
                    "errors": {'profile': "Member should update profile."},
                    "code": "invalid_role"
                }
            )
        if scheduled_class.base_class.gender_type != BaseClass.GenderChoice.NOT_SPECIFIED and \
                user_profile.first().gender != scheduled_class.base_class.gender_type:
            raise GraphQLError(
                message="Member's gender not valid for this class.",
                extensions={
                    "errors": {'gender': "Member's gender not valid for this class."},
                    "code": "invalid_gender"
                }
            )
        member_user, created = Member.objects.get_or_create(user=info.context.user)
        input = {'scheduled_class': scheduled_class, 'member': member_user}
        form = ClassBookingForm(data=input)
        if object_id:
            obj = ClassBooking.objects.get(id=object_id, member=member_user)
            form = ClassBookingForm(data=input, instance=obj)
        if form.is_valid():
            obj, created = ClassBooking.objects.update_or_create(
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
        scheduled_class.members.add(member_user)
        return ClassBookingMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}.", class_booking_object=obj
        )


class ClassScheduleMutation(DjangoFormMutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    class_object = graphene.Field(ClassType)

    class Meta:
        form_class = ClassScheduleForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = ClassScheduleForm(data=input)
        if form.is_valid():
            form.cleaned_data['available_seat'] = form.cleaned_data['limit']
            approximate_final_date = form.cleaned_data['approximate_final_date']
            del form.cleaned_data['approximate_final_date']
            # previous_classes = ClassSchedule.objects.filter(
            #     base_class=form.cleaned_data['base_class'], date__lte=approximate_final_date
            # ).filter(date__gte=timezone.now().date())
            # print(previous_classes)
            if form.cleaned_data['base_class'].single_class:
                form.cleaned_data['date'] = approximate_final_date
                obj = ClassSchedule.objects.create(**form.cleaned_data)
                print(obj)
            else:
                bulk_list = []
                start_date = timezone.now().date()
                delta = datetime.timedelta(days=1)
                while start_date <= approximate_final_date:
                    if str(start_date.weekday()) in [day.day for day in form.cleaned_data['base_class'].weekday.all()]:
                        form.cleaned_data['date'] = start_date
                        bulk_list.append(ClassSchedule(**form.cleaned_data))
                    start_date += delta
                if bulk_list:
                    object_list = ClassSchedule.objects.bulk_create(bulk_list)
                else:
                    raise GraphQLError(
                        message="No date found to the following date and weekday.",
                        extensions={
                            "errors": "No date found to the following date and weekday.",
                            "code": "invalid_input"
                        }
                    )
                print(object_list)
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
        return ClassScheduleMutation(
            success=True, message="Successfully added.", class_object=form.cleaned_data['base_class']
        )


class ClassScheduleUpdateMutation(DjangoFormMutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    class_object = graphene.Field(ClassType)

    class Meta:
        form_class = ClassScheduleUpdateForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        obj = ClassSchedule.objects.get(id=input['object_id'])
        form = ClassScheduleUpdateForm(data=input, instance=obj)
        if form.is_valid():
            del form.cleaned_data['object_id']
            if len(obj.members) > form.cleaned_data['limit']:
                raise GraphQLError(
                    message="Limit should be greater or equal to added members.",
                    extensions={
                        "errors": {"members": "Limit should be greater or equal to added members."},
                        "code": "invalid_input"
                    }
                )
            if obj.limit != form.cleaned_data['limit']:
                form.cleaned_data['available_seat'] = form.cleaned_data['limit'] - len(obj.members)
            obj = ClassSchedule.objects.update(
                id=input['object_id'], defaults=form.cleaned_data
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
        return ClassScheduleUpdateMutation(
            success=True, message="Successfully updated.", class_object=obj
        )


class PostponeClassMutation(graphene.Mutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    class_schedule_object = graphene.Field(ClassBookingType)

    class Arguments:
        object_id = graphene.ID()
        reason = graphene.String()

    @is_admin_user
    def mutate(self, info, object_id, reason, **kwargs):
        if not reason.strip():
            raise GraphQLError(
                message="Should include reason to postpone class.",
                extensions={
                    "reason": "Should include reason to postpone  class.",
                    "code": "invalid_input"
                }
            )
        obj = ClassSchedule.objects.get(id=object_id, postponed=False)
        obj.postponed = True
        obj.postpone_reason = reason
        obj.save()
        return PostponeClassMutation(success=True, message="Successfully postponed.", class_schedule_object=obj)


class ClassAttendanceMutation(graphene.Mutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    class_schedule_object = graphene.Field(ClassBookingType)

    class Arguments:
        object_id = graphene.ID()
        member = graphene.ID()
        remove = graphene.Boolean()

    @is_authenticated
    def mutate(self, info, object_id, member, remove=False, **kwargs):
        trainer = check_trainer(info.context.user)
        obj = ClassSchedule.objects.get(id=object_id, postponed=False)
        if trainer != obj.trainer:
            raise GraphQLError(
                message="Trainer does not have permission to take attendance.",
                extensions={
                    'errors': {"trainer": "Trainer does not have permission to take attendance."},
                    "code": "invalid_trainer"
                }
            )
        member = Member.objects.get(id=member)
        if remove:
            obj.attended_members.remove(member)
        else:
            obj.attended_members.add(member)
        return ClassAttendanceMutation(
            success=True, message=f"Successfully {'removed' if remove else 'added'}.", class_schedule_object=obj
        )


class Mutation(graphene.ObjectType):
    weekday_mutation = WeekDayMutation.Field()
    class_mutation = ClassMutation.Field()
    class_schedule_mutation = ClassScheduleMutation.Field()
    update_class_schedule = ClassScheduleUpdateMutation.Field()
    postpone_class = PostponeClassMutation.Field()
    book_class = ClassBookingMutation.Field()
    class_attendance_mutation = ClassAttendanceMutation.Field()

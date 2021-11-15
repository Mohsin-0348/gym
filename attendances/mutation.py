import graphene
from django.utils import timezone
from graphene_django.forms.mutation import DjangoFormMutation
from graphql import GraphQLError

from attendances.forms import ClassWorkOutForm, GymWorkOutForm, WorkOutForm
from attendances.models import (
    ClassAttendance,
    ClassWorkOut,
    EmployeeAttendance,
    GymAttendance,
    GymWorkOut,
    WorkOut,
)
from attendances.object_types import (
    ClassAttendanceType,
    ClassWorkOutType,
    EmployeeAttendanceType,
    GymAttendanceType,
    GymWorkOutType,
    WorkOutType,
)
from backend.permissions import is_admin_user, is_authenticated
from classes.models import ClassSchedule
from classes.object_types import ClassScheduleType
from hr.models import Employee
from members.models import Member
from members.utils import check_member, check_trainer


class WorkOutMutation(DjangoFormMutation):

    success = graphene.Boolean()
    message = graphene.String()
    workout_object = graphene.Field(WorkOutType)

    class Meta:
        form_class = WorkOutForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        form = WorkOutForm(data=input)
        object_id = None
        if form.data.get('object_id'):
            object_id = form.data['object_id']
            obj = WorkOut.objects.get(id=object_id)
            form = WorkOutForm(data=input, instance=obj)
        if form.is_valid():
            del form.cleaned_data['object_id']
            obj, created = WorkOut.objects.update_or_create(id=object_id, defaults=form.cleaned_data)
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
        return WorkOutMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", workout_object=obj
        )


class ClassWorkOutMutation(DjangoFormMutation):

    success = graphene.Boolean()
    message = graphene.String()
    workout_object = graphene.Field(ClassWorkOutType)

    class Meta:
        form_class = ClassWorkOutForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        user = info.context.user
        form = ClassWorkOutForm(data=input)
        object_id = None
        if form.data.get('object_id'):
            object_id = form.data['object_id']
            obj = ClassWorkOut.objects.get(id=object_id)
            form = ClassWorkOutForm(data=input, instance=obj)
        if form.is_valid():
            trainer = check_trainer(user)
            ClassAttendance.objects.get(id=form.cleaned_data['class_attendance'].id, class_schedule__trainer=trainer)
            del form.cleaned_data['object_id']
            obj, created = ClassWorkOut.objects.update_or_create(id=object_id, defaults=form.cleaned_data)
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
        return ClassWorkOutMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", workout_object=obj
        )


class DeleteClassWorkOut(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        object_id = graphene.ID()

    @is_authenticated
    def mutate(self, info, object_id, **kwargs):
        user = info.context.user
        trainer = check_trainer(user)
        obj = ClassWorkOut.objects.get(id=object_id, class_attendance__class_schedule__trainer=trainer)
        obj.delete()
        return DeleteClassWorkOut(success=True, message="Successfully deleted.")


class GymWorkOutMutation(DjangoFormMutation):

    success = graphene.Boolean()
    message = graphene.String()
    workout_object = graphene.Field(GymWorkOutType)

    class Meta:
        form_class = GymWorkOutForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        user = info.context.user
        form = GymWorkOutForm(data=input)
        object_id = None
        if form.data.get('object_id'):
            object_id = form.data['object_id']
            obj = GymWorkOut.objects.get(id=object_id)
            form = GymWorkOutForm(data=input, instance=obj)
        if form.is_valid():
            member = check_member(user)
            GymAttendance.objects.get(id=form.cleaned_data['gym_attendance'].id, member=member)
            del form.cleaned_data['object_id']
            obj, created = GymWorkOut.objects.update_or_create(id=object_id, defaults=form.cleaned_data)
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
        return GymWorkOutMutation(
            success=True, message=f"Successfully {'added' if created else 'updated'}", workout_object=obj
        )


class DeleteGymWorkOut(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        object_id = graphene.ID()

    @is_authenticated
    def mutate(self, info, object_id, **kwargs):
        user = info.context.user
        member = check_member(user)
        obj = GymWorkOut.objects.get(id=object_id, gym_attendance__member=member)
        obj.delete()
        return DeleteGymWorkOut(success=True, message="Successfully deleted.")


class MemberAttendanceMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    attendance_object = graphene.Field(GymAttendanceType)

    class Arguments:
        check_out = graphene.Boolean()

    @is_authenticated
    def mutate(self, info, check_out=False, **kwargs):
        user = info.context.user
        member = check_member(user)
        if check_out:
            if not GymAttendance.objects.filter(member=member, check_in__date=timezone.now().date(), check_out=None):
                raise GraphQLError(
                    message="Invalid request.",
                    extensions={
                        "errors": {"check_in": "User did not check in yet."},
                        "code": "not_checked_in"
                    }
                )
            attendance = GymAttendance.objects.get(member=member, check_in__date=timezone.now().date(), check_out=None)
            attendance.check_out = timezone.now()
            attendance.save()
        else:
            if GymAttendance.objects.filter(member=member, check_in__date=timezone.now().date()):
                raise GraphQLError(
                    message="Invalid request.",
                    extensions={
                        "errors": {"check_in": "User already checked in."},
                        "code": "already_check_in"
                    }
                )
            attendance = GymAttendance.objects.create(member=member)
        return MemberAttendanceMutation(
            success=True, message=f"Successfully {'checked out' if check_out else 'checked in'}.",
            attendance_object=attendance
        )


class ClassAttendanceMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    attendance_object = graphene.Field(ClassAttendanceType)

    class Arguments:
        class_id = graphene.ID()
        check_out = graphene.Boolean()

    @is_authenticated
    def mutate(self, info, class_id, check_out=False, **kwargs):
        user = info.context.user
        trainer = check_trainer(user)
        class_schedule = ClassSchedule.objects.get(
            id=class_id, trainer=trainer, postponed=False, date=timezone.now().date(), start_time__lte=timezone.now()
        )
        if check_out:
            if not ClassAttendance.objects.filter(class_schedule=class_schedule, check_out=None):
                raise GraphQLError(
                    message="Invalid request.",
                    extensions={
                        "errors": {"check_in": "Class did not start in yet."},
                        "code": "not_started"
                    }
                )
            attendance = ClassAttendance.objects.get(class_schedule=class_schedule)
            attendance.check_out = timezone.now()
            attendance.save()
        else:
            if ClassAttendance.objects.filter(class_schedule=class_schedule):
                raise GraphQLError(
                    message="Invalid request.",
                    extensions={
                        "errors": {"check_in": "Class already started."},
                        "code": "already_started"
                    }
                )
            attendance = ClassAttendance.objects.create(class_schedule=class_schedule)
        return ClassAttendanceMutation(
            success=True, message=f"Successfully {'checked out' if check_out else 'checked in'}.",
            attendance_object=attendance
        )


class ClassMemberAttendanceMutation(graphene.Mutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    class_schedule_object = graphene.Field(ClassScheduleType)

    class Arguments:
        class_id = graphene.ID()
        member = graphene.ID()
        remove = graphene.Boolean()

    @is_authenticated
    def mutate(self, info, class_id, member, remove=False, **kwargs):
        trainer = check_trainer(info.context.user)
        obj = ClassSchedule.objects.get(
            id=class_id, trainer=trainer, postponed=False, date=timezone.now().date()
        )
        if not ClassAttendance.objects.filter(class_schedule=obj, check_out=None):
            raise GraphQLError(
                message="Invalid request.",
                extensions={
                    "errors": {"check_in": "Class did not start in yet."},
                    "code": "not_started"
                }
            )
        class_attendance = ClassAttendance.objects.get(class_schedule=obj)
        member = Member.objects.get(id=member)
        if member not in obj.members.all():
            raise GraphQLError(
                message="Invalid request.",
                extensions={
                    "errors": {"members": "Member did not registered for this class."},
                    "code": "not_registered"
                }
            )
        if remove:
            if not class_attendance.attended_members.filter(id=member.id):
                raise GraphQLError(
                    message="Invalid request.",
                    extensions={
                        "errors": {"members": "Member did not attend yet."},
                        "code": "not_attended"
                    }
                )
            class_attendance.attended_members.remove(member)
        else:
            if class_attendance.attended_members.filter(id=member.id):
                raise GraphQLError(
                    message="Invalid request.",
                    extensions={
                        "errors": {"members": "Member already attended."},
                        "code": "already_attended"
                    }
                )
            class_attendance.attended_members.add(member)
        return ClassMemberAttendanceMutation(
            success=True, message=f"Successfully {'removed' if remove else 'added'}.", class_schedule_object=obj
        )


class EmployeeAttendanceMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    attendance_object = graphene.Field(EmployeeAttendanceType)

    class Arguments:
        check_out = graphene.Boolean()

    @is_authenticated
    def mutate(self, info, check_out=False, **kwargs):
        user = info.context.user
        employee = Employee.objects.get(user=user)
        if user.is_staff:
            employee, created = Employee.objects.get_or_create(user=user)
        if check_out:
            if not EmployeeAttendance.objects.filter(
                    employee=employee, check_in__date=timezone.now().date(), check_out=None
            ):
                raise GraphQLError(
                    message="Invalid request.",
                    extensions={
                        "errors": {"check_in": "User did not check in yet."},
                        "code": "not_checked_in"
                    }
                )
            attendance = EmployeeAttendance.objects.get(
                employee=employee, check_in__date=timezone.now().date(), check_out=None
            )
            attendance.check_out = timezone.now()
            attendance.save()
        else:
            if EmployeeAttendance.objects.filter(employee=employee, check_in__date=timezone.now().date()):
                raise GraphQLError(
                    message="Invalid request.",
                    extensions={
                        "errors": {"check_in": "User already checked in."},
                        "code": "already_check_in"
                    }
                )
            attendance = EmployeeAttendance.objects.create(employee=employee)
        return EmployeeAttendanceMutation(
            success=True, message=f"Successfully {'checked out' if check_out else 'checked in'}.",
            attendance_object=attendance
        )


class Mutation(graphene.ObjectType):
    workout_mutation = WorkOutMutation.Field()

    member_attendance_mutation = MemberAttendanceMutation.Field()
    gym_workout_mutation = GymWorkOutMutation.Field()
    delete_gym_workout = DeleteGymWorkOut.Field()

    class_attendance_mutation = ClassAttendanceMutation.Field()
    class_workout_mutation = ClassWorkOutMutation.Field()
    delete_class_workout = DeleteClassWorkOut.Field()
    class_member_attendance_mutation = ClassMemberAttendanceMutation.Field()

    employee_attendance_mutation = EmployeeAttendanceMutation.Field()

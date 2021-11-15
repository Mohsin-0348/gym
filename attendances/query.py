import graphene
from graphene_django.filter import DjangoFilterConnectionField

from attendances.models import EmployeeAttendance, GymAttendance, WorkOut
from attendances.object_types import (
    EmployeeAttendanceType,
    GymAttendanceType,
    WorkOutType,
)
from backend.permissions import is_admin_user, is_authenticated
from hr.models import Employee
from members.utils import check_member


class Query(graphene.ObjectType):
    all_work_outs = DjangoFilterConnectionField(WorkOutType)
    work_out = DjangoFilterConnectionField(WorkOutType)
    gym_attendances = DjangoFilterConnectionField(GymAttendanceType)
    gym_attendance = graphene.relay.Node.Field(GymAttendanceType)
    employee_attendances = DjangoFilterConnectionField(EmployeeAttendanceType)
    employee_attendance = graphene.relay.Node.Field(EmployeeAttendanceType)

    @is_admin_user
    def resolve_all_work_outs(self, info, **kwargs) -> object:
        return WorkOut.objects.all()

    @is_authenticated
    def resolve_gym_attendances(self, info, **kwargs) -> object:
        user = info.context.user
        if not user.is_staff:
            member = check_member(user)
            return GymAttendance.objects.filter(member=member)
        return GymAttendance.objects.all()

    # @is_authenticated
    # def resolve_gym_attendance(self, info, id, **kwargs) -> object:
    #     user = info.context.user
    #     if not user.is_staff:
    #         member = check_member(user)
    #         return GymAttendance.objects.get(id=id, member=member)
    #     return GymAttendance.objects.get(id=id)

    @is_authenticated
    def resolve_employee_attendances(self, info, **kwargs) -> object:
        user = info.context.user
        if not user.is_staff:
            user_employee = Employee.objects.get(user=user)
            return EmployeeAttendance.objects.filter(employee=user_employee)
        return EmployeeAttendance.objects.all()

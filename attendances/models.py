
from django.contrib.auth import get_user_model
from django.db import models

from bases.models import CheckInCheckOut
from classes.models import ClassSchedule

# from packages.models import PersonalTrainingBooking
from hr.models import Employee
from members.models import Member

User = get_user_model()


class WorkOut(models.Model):
    class UOMChoice(models.TextChoices):
        COUNT = 'count'
        KG = 'kg'

    name = models.CharField(max_length=128)
    uom = models.CharField(max_length=8, choices=UOMChoice.choices, default=UOMChoice.COUNT)
    base_amount = models.FloatField(default=1)
    reduce_calorie = models.FloatField(default=1)


class ClassAttendance(CheckInCheckOut):
    class_schedule = models.OneToOneField(ClassSchedule, on_delete=models.DO_NOTHING, related_name="class_attendance")
    attended_members = models.ManyToManyField(Member, related_name='attended_members', blank=True, null=True)


class ClassWorkOut(models.Model):
    class_attendance = models.ForeignKey(ClassAttendance, on_delete=models.DO_NOTHING, related_name="class_workouts")
    base_type = models.ForeignKey(WorkOut, on_delete=models.DO_NOTHING, related_name="workouts_for_classes")
    amount = models.FloatField(default=1)

    @property
    def burnt_calorie(self):
        return (self.base_type.reduce_calorie / self.base_type.base_amount) * self.amount

    class Meta:
        unique_together = ('class_attendance', 'base_type')


class GymAttendance(CheckInCheckOut):
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='gym_attendances')


class GymWorkOut(models.Model):
    gym_attendance = models.ForeignKey(GymAttendance, on_delete=models.DO_NOTHING, related_name="gym_workouts")
    base_type = models.ForeignKey(WorkOut, on_delete=models.DO_NOTHING, related_name="workouts_for_gym")
    amount = models.FloatField(default=1)

    @property
    def burnt_calorie(self):
        return (self.base_type.reduce_calorie / self.base_type.base_amount) * self.amount

    class Meta:
        unique_together = ('gym_attendance', 'base_type')


class EmployeeAttendance(CheckInCheckOut):
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name='employee_attendances')


# class SessionAttendance(CheckInCheckOut):
#     package = models.ForeignKey(PersonalTrainingBooking, on_delete=models.DO_NOTHING,
#                                 related_name='personal_training_attendances')
#
#
# class SessionWorkOut(models.Model):
#     session_attendance = models.ForeignKey(SessionAttendance, on_delete=models.DO_NOTHING,
#                                            related_name="session_workouts")
#     base_type = models.ForeignKey(WorkOut, on_delete=models.DO_NOTHING, related_name="workouts_for_training")
#     amount = models.FloatField(default=1)
#
#     @property
#     def burnt_calorie(self):
#         return (self.base_type.reduce_calorie / self.base_type.base_amount) * self.amount

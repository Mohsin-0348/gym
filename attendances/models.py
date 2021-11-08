# from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from bases.models import CheckInCheckOut
from classes.models import ClassSchedule
from members.models import Member
from packages.models import PersonalTrainingBooking

# from django.utils import timezone
# from easy_thumbnails.fields import ThumbnailerImageField


User = get_user_model()


class WorkOutType(models.Model):
    name = models.CharField(max_length=128)
    uom = models.CharField(max_length=128)  # ::ToDo -> will be choice field
    base_amount = models.FloatField(default=1)
    base_in_calorie = models.FloatField(default=1)


class WorkOut(models.Model):
    base_type = models.ForeignKey(WorkOutType, on_delete=models.DO_NOTHING, related_name="workouts")
    amount = models.FloatField(default=1)

    @property
    def burnt_calorie(self):
        return (self.base_type.base_in_calorie / self.base_type.base_amount) * self.amount

    class Meta:
        abstract = True  # define this table/model is abstract.


class ClassWorkOut(WorkOut):
    class_attendance = models.ForeignKey(ClassSchedule, on_delete=models.DO_NOTHING, related_name="class_workouts")


class GymAttendance(CheckInCheckOut):
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='gym_attendances')
    work_outs = models.ManyToManyField(WorkOut)


class GymWorkOut(WorkOut):
    gym_attendance = models.ForeignKey(GymAttendance, on_delete=models.DO_NOTHING, related_name="gym_workouts")


class SessionAttendance(CheckInCheckOut):
    package = models.ForeignKey(PersonalTrainingBooking, on_delete=models.DO_NOTHING,
                                related_name='personal_training_attendances')


class SessionWorkOut(WorkOut):
    session_attendance = models.ForeignKey(SessionAttendance, on_delete=models.DO_NOTHING,
                                           related_name="session_workouts")

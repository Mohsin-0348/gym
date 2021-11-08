from django.conf import settings
from django.db import models

from bases.constants import WeekDayChoice
from bases.models import BaseModelWithOutId
from hr.models import Employee
from members.models import Member


class WeekDay(models.Model):
    day = models.CharField(max_length=1, choices=WeekDayChoice.choices, default=WeekDayChoice.SUNDAY, unique=True)

    def __str__(self):
        return self.day


class BaseClass(models.Model):
    """
        Basic class information to be stored.
        Weekday will be selection field that will provide week day names.
    """
    class GenderChoice(models.TextChoices):
        MALE = 'male'
        FEMALE = 'female'
        NOT_SPECIFIED = 'not-specified'

    name = models.CharField(max_length=128)
    description = models.TextField()
    single_class = models.BooleanField(default=False)
    weekday = models.ManyToManyField(WeekDay, blank=True, null=True)
    gender_type = models.CharField(max_length=16, choices=GenderChoice.choices, default=GenderChoice.NOT_SPECIFIED)

    def __str__(self):
        return self.name


class ClassSchedule(BaseModelWithOutId):
    """

        Will need an end-date input to generate class schedule till that date.
        No necessary to store end-date data.
    """
    base_class = models.ForeignKey(BaseClass, on_delete=models.DO_NOTHING, related_name="class_schedules")
    trainer = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name="trainer_classes")
    members = models.ManyToManyField(Member, related_name='members', blank=True, null=True)
    attended_members = models.ManyToManyField(Member, related_name='attended_members', blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    limit = models.PositiveIntegerField(default=settings.DEFAULT_SEAT_LIMIT_FOR_CLASS)
    available_seat = models.PositiveIntegerField()
    postponed = models.BooleanField(default=False)
    postpone_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.base_class.name} // {self.date}"


class ClassBooking(BaseModelWithOutId):
    scheduled_class = models.ForeignKey(ClassSchedule, on_delete=models.DO_NOTHING, related_name="class_bookings")
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='booked_classes')

    class Meta:
        unique_together = ('scheduled_class', 'member')

    def __str__(self):
        return f"{self.scheduled_class} // {self.member}"

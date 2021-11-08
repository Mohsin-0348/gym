from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from bases.models import CheckInCheckOut
from members.models import Member

User = get_user_model()


class Locker(models.Model):
    serial_no = models.CharField(max_length=16)
    description = models.TextField()
    availability = models.BooleanField(default=True)


class MemberLocker(models.Model):
    locker = models.ForeignKey(Locker, on_delete=models.DO_NOTHING, related_name="locker_users")
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING, null=True, blank=True,
                               related_name='booked_lockers')
    issue_date = models.DateField(default=timezone.now().date())
    expiry_date = models.DateField()


class TrackingLocker(CheckInCheckOut):
    locker = models.ForeignKey(Locker, on_delete=models.DO_NOTHING, related_name="locker_entries")
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING, null=True, blank=True,
                               related_name='locker_usage')

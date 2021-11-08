from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from bases.models import BaseModelWithOutId
from members.models import Member

User = get_user_model()


class Package(BaseModelWithOutId):
    name = models.CharField(max_length=128)
    description = models.TextField()
    month_duration = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=1)


class PackageBooking(BaseModelWithOutId):
    package = models.ForeignKey(Package, on_delete=models.DO_NOTHING, related_name="package_bookings")
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='booked_packages')
    start_date = models.DateField(default=timezone.now().date())
    end_date = models.DateField(null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    payment_method = models.CharField(max_length=32)  # ::ToDo -> will be choice field


class PersonalTrainingPackage(BaseModelWithOutId):
    name = models.CharField(max_length=128)
    description = models.TextField()
    month_duration = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=1)


class PersonalTrainingBooking(BaseModelWithOutId):
    package = models.ForeignKey(PersonalTrainingPackage, on_delete=models.DO_NOTHING,
                                related_name="personal_training_bookings")
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='booked_personal_training_packages')
    start_date = models.DateField(default=timezone.now().date())
    end_date = models.DateField(null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    payment_method = models.CharField(max_length=32)  # ::ToDo -> will be choice field


class Membership(models.Model):
    member = models.OneToOneField(Member, on_delete=models.DO_NOTHING, related_name="membership_info")
    package = models.ForeignKey(PackageBooking, on_delete=models.DO_NOTHING, related_name="booked_membership")
    personal_training = models.ForeignKey(PersonalTrainingBooking, on_delete=models.DO_NOTHING,
                                          related_name="booked_personal_training")
    freezing_date = models.DateField(default=timezone.now().date(), null=True, blank=True)

    @property
    def freezing_status(self):
        if self.freezing_date:
            return True
        return False


class Discount(BaseModelWithOutId):
    name = models.CharField(max_length=32)
    discount_type = models.CharField(max_length=128)  # ::ToDo -> will be choice field
    value = models.PositiveIntegerField(default=1)
    min_amount_to_use = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    max_user_limit = models.PositiveIntegerField(default=settings.DISCOUNT_USER_LIMIT)
    max_limit_per_user = models.IntegerField(default=1)
    expiry_date = models.DateField()

    @property
    def expiry_status(self):
        if self.expiry_date > timezone.now().date():
            return True
        return False


class PaymentHistory(BaseModelWithOutId):
    member = models.OneToOneField(Member, on_delete=models.DO_NOTHING, related_name="payments")
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    receiver = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="received_payments")
    category = models.CharField(max_length=32)  # ::ToDo -> will be choice field
    # specific action for employee/or user e.g. payroll change.
    # Generic Foreignkey Configuration. DO NOT CHANGE
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.CharField(
        max_length=100
    )
    content_object = GenericForeignKey()

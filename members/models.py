from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from easy_thumbnails.fields import ThumbnailerImageField

from bases.models import BaseBodyMeasurement, BaseIdentification, BaseModelWithOutId
from hr.models import Employee
from members.choices import MealTypeChoice, UOMChoice

User = get_user_model()


class Food(models.Model):
    name = models.CharField(max_length=64)
    uom = models.CharField(max_length=16, choices=UOMChoice.choices)
    base_amount = models.FloatField(default=1)
    base_in_calorie = models.FloatField(default=1)

    def __str__(self):
        return f"{self.name} - {self.base_in_calorie}Calorie in per {self.base_amount}{self.uom}"

    class Meta:
        unique_together = ('name', 'uom')
        ordering = ['-id']  # define default order as id in descending


class Member(BaseIdentification):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name="member_info")
    allergy_foods = models.ManyToManyField(Food, null=True, blank=True)
    medical_issues = models.JSONField(null=True, blank=True)

    @property
    def current_body_measurement(self) -> object:
        if TrackBodyMeasurement.objects.filter(member=self):
            return TrackBodyMeasurement.objects.filter(member=self).first()
        return None

    def __str__(self):
        return self.user.username


class NutritionPlan(BaseModelWithOutId):
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name="nutrition_plans")
    meal_type = models.CharField(max_length=16, choices=MealTypeChoice.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    added_by = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name="plans_added")
    updated_by = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name="plans_updated")

    @property
    def complete_status(self):
        if self.end_date < timezone.now().date():
            return False
        return True

    def __str__(self):
        return f"{self.member.user.username} - {self.meal_type}"

    class Meta:
        ordering = ['-created_on']  # define default order as created_on in descending


class FoodToEat(models.Model):
    plan = models.ForeignKey(NutritionPlan, on_delete=models.CASCADE, related_name="foods_to_eat")
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('plan', 'food')


class TrackNutritionPlan(BaseModelWithOutId):
    plan = models.ForeignKey(NutritionPlan, on_delete=models.CASCADE, related_name="daily_tracks")
    photo = ThumbnailerImageField(
        'ProfilePicture',
        upload_to=f"nutrition_plans/{timezone.now().date()}/",
        blank=True,
        null=True
    )
    # checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.plan.member.user.username} - {self.plan.meal_type} // {self.created_on.date()}"

    class Meta:
        ordering = ['-created_on']  # define default order as created_on in descending


class FoodsConsumed(models.Model):
    plan_track = models.ForeignKey(TrackNutritionPlan, on_delete=models.CASCADE, related_name="consumed_foods")
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('plan_track', 'food')


class TrackBodyMeasurement(BaseModelWithOutId, BaseBodyMeasurement):
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='body_measurements_tracking')
    photo = ThumbnailerImageField(
        'ProfilePicture',
        upload_to=f"body_measurements/{timezone.now().date()}/",
        blank=True,
        null=True
    )
    # checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.member.user.username} // {self.created_on.date()}"

    class Meta:
        ordering = ['-created_on']  # define default order as created_on in descending

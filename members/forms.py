from django import forms

from members.models import (
    Food,
    FoodsConsumed,
    FoodToEat,
    Member,
    NutritionPlan,
    TrackBodyMeasurement,
    TrackNutritionPlan,
)


class MemberForm(forms.ModelForm):

    class Meta:
        model = Member
        exclude = ("user",)


class FoodForm(forms.ModelForm):
    object_id = forms.CharField(max_length=64, required=False)

    class Meta:
        model = Food
        fields = '__all__'


class NutritionPlanForm(forms.ModelForm):
    object_id = forms.CharField(max_length=64, required=False)

    class Meta:
        model = NutritionPlan
        exclude = ('added_by', 'updated_by')


class TrackNutritionPlanForm(forms.ModelForm):
    object_id = forms.CharField(max_length=64, required=False)

    class Meta:
        model = TrackNutritionPlan
        fields = ('plan', 'photo')


class FoodToEatForm(forms.ModelForm):
    object_id = forms.CharField(max_length=64, required=False)

    class Meta:
        model = FoodToEat
        fields = '__all__'


class FoodsConsumedForm(forms.ModelForm):
    object_id = forms.CharField(max_length=64, required=False)

    class Meta:
        model = FoodsConsumed
        fields = '__all__'


class BodyMeasurementForm(forms.ModelForm):

    class Meta:
        model = TrackBodyMeasurement
        fields = '__all__'

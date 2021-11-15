from django import forms

from attendances.models import ClassWorkOut, GymWorkOut, WorkOut


class WorkOutForm(forms.ModelForm):
    object_id = forms.CharField(max_length=8, required=False)

    class Meta:
        model = WorkOut
        fields = '__all__'


class ClassWorkOutForm(forms.ModelForm):
    object_id = forms.CharField(max_length=8, required=False)

    class Meta:
        model = ClassWorkOut
        fields = '__all__'


class GymWorkOutForm(forms.ModelForm):
    object_id = forms.CharField(max_length=8, required=False)

    class Meta:
        model = GymWorkOut
        fields = '__all__'

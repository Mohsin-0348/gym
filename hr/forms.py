from django import forms

from hr.models import Employee


class EmployeeForm(forms.ModelForm):
    object_id = forms.CharField(max_length=64, required=False)
    username = forms.CharField(max_length=128)
    email = forms.EmailField(max_length=128)

    class Meta:
        model = Employee
        exclude = ('user', )

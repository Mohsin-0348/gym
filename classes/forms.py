from django import forms

from classes.models import BaseClass, ClassBooking, ClassSchedule, WeekDay


class WeekDayForm(forms.ModelForm):
    object_id = forms.CharField(max_length=2, required=False)

    class Meta:
        model = WeekDay
        fields = '__all__'


class ClassForm(forms.ModelForm):
    object_id = forms.CharField(max_length=8, required=False)

    class Meta:
        model = BaseClass
        fields = '__all__'


class ClassScheduleForm(forms.ModelForm):
    approximate_final_date = forms.DateField(required=True)

    class Meta:
        model = ClassSchedule
        fields = ('base_class', 'trainer', 'start_time', 'end_time', 'limit')


class ClassScheduleUpdateForm(forms.ModelForm):
    object_id = forms.CharField(max_length=8, required=True)

    class Meta:
        model = ClassSchedule
        fields = ('trainer', 'date', 'start_time', 'end_time', 'limit')


class ClassBookingForm(forms.ModelForm):

    class Meta:
        model = ClassBooking
        fields = '__all__'

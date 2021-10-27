from django import forms
from django.contrib.auth import get_user_model

from users.models import Address, UserProfile

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("username", "email", "password")


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "gender", "phone", "date_of_birth")


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = "__all__"

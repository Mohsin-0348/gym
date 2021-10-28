# at w3gym/backend/users/filters.py

import django_filters
from django.contrib.auth import get_user_model

from bases.filters import BaseFilters
from users.models import Address, UnitOfHistory, UserProfile

User = get_user_model()


class UserFilters(BaseFilters):
    """UserFilter will define here"""
    username = django_filters.CharFilter(
        field_name='username',
        lookup_expr='icontains'
    )
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains'
    )
    first_name = django_filters.CharFilter(
        field_name='first_name',
        lookup_expr='icontains'
    )
    last_name = django_filters.CharFilter(
        field_name='last_name',
        lookup_expr='icontains'
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_email_verified',
            'is_active',
            'is_staff',
            'is_superuser',
            'is_deleted',
        ]


class UserProfileFilters(BaseFilters):
    """UserFilter will define here"""

    user = django_filters.CharFilter(
        field_name='user__email',
        lookup_expr='icontains'
    )

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'phone',
            'gender',
            'date_of_birth',
            'term_and_condition_accepted',
            'privacy_policy_accepted',
            'is_phone_verified',
            'is_profile_pic_verified',
            'is_document_verified',
        ]


class LogsFilters(BaseFilters):
    action = django_filters.CharFilter(
        field_name='action',
        lookup_expr='icontains'
    )
    user = django_filters.CharFilter(
        field_name='user__email',
        lookup_expr='icontains'
    )
    perform_for = django_filters.CharFilter(
        field_name='perform_for__email',
        lookup_expr='icontains'
    )

    class Meta:
        model = UnitOfHistory
        fields = [
            'id',
            'action',
            'user',
            'perform_for',

        ]


class AddressFilters(BaseFilters):
    address1 = django_filters.CharFilter(
        field_name='address1',
        lookup_expr='icontains'
    )
    city = django_filters.CharFilter(
        field_name='city',
        lookup_expr='icontains'
    )
    state = django_filters.CharFilter(
        field_name='state',
        lookup_expr='icontains'
    )
    postal_code = django_filters.CharFilter(
        field_name='postal_code',
        lookup_expr='icontains'
    )
    country = django_filters.CharFilter(
        field_name='country',
        lookup_expr='icontains'
    )

    class Meta:
        model = Address
        fields = [
            'id',
            'address1',
            'city',
            'state',
            'postal_code',
            'country',

        ]

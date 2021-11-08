from django.db import models


class VerifyActionChoices(models.TextChoices):
    APPROVE = 'approve'
    REJECT = 'reject'


class HistoryActions(models.TextChoices):
    USER_SIGNUP = 'user-signup'
    USER_LOGIN = 'user-login'
    USER_UPDATE = 'user-update'
    EMAIL_VERIFIED = 'email-verified'
    RESEND_ACTIVATION = 'resend-email-activation'
    PASSWORD_CHANGE = 'password-change'
    PASSWORD_RESET_REQUEST = 'password-reset-request'
    PASSWORD_RESET = 'password-reset'
    ACCOUNT_DEACTIVATE = 'account-deactivate'
    ADDRESS_ADDED = 'address-added'
    SOCIAL_SINGUP = 'social-signup'
    SOCIAL_LOGIN = 'social-login'
    NEW_ADMIN_ADDED = 'new-admin-added'
    MEMBER_INFO_UPDATE = 'member-info-update'
    DELETE_FOOD = 'delete-food'
    EMPLOYEE_ADDED = 'employee-added'
    EMPLOYEE_UPDATED = 'employee-updated'


class WeekDayChoice(models.TextChoices):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

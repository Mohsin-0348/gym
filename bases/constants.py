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

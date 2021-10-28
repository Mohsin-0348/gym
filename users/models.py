# at w3gym/backend/users/models.py

from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# ThirdParty Library imports
from easy_thumbnails.fields import ThumbnailerImageField

# local imports
from bases.models import BaseModel, BaseModelWithOutId
from bases.utils import create_token

from .choices import (
    DeviceTypeChoices,
    GenderChoices,
    RoleChoices,
    SocialAccountTypeChoices,
)
from .managers import (
    UserDeviceTokenManager,
    UserOTPManager,
    UserPasswordResetManager,
    UserSocialAccountManager,
)

# Create your models here.


class User(BaseModelWithOutId, AbstractUser, PermissionsMixin):
    """Store custom user information.
    all fields are common for all users."""
    # username = models.CharField(
    #     max_length=20,
    #     unique=True,
    #     null=True
    # )  # unique user name to perform username password login.
    email = models.EmailField(
        max_length=100,
        unique=True
    )  # unique email to perform email login and send alert mail.
    is_email_verified = models.BooleanField(
        default=False
    )
    # is_active = models.BooleanField(
    #     default=True
    # )
    # is_staff = models.BooleanField(
    #     default=False
    # )
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False
    )  # main man of this application.
    last_active_on = models.DateTimeField(
        null=True,
        blank=True
    )
    # date_joined = models.DateTimeField(
    #     _('date joined'),
    #     default=timezone.now
    # )
    activation_token = models.UUIDField(
        blank=True,
        null=True
    )
    deactivation_reason = models.TextField(
        null=True,
        blank=True
    )
    is_deleted = models.BooleanField(
        default=False
    )
    deleted_on = models.DateTimeField(
        null=True,
        blank=True
    )
    # last login will provide by django abstract_base_user.
    # password also provide by django abstract_base_user.

    # objects = UserManager()

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']

    # class Meta:
    #     db_table = f"{settings.DB_PREFIX}_users"

    @property
    def is_admin(self) -> bool:
        return self.is_staff or self.is_superuser

    @property
    def status(self) -> str:
        status = "active"
        if self.is_deleted:
            status = "deleted"
        elif self.is_active and not self.deactivation_reason:
            status = "active"
        elif not self.is_active and not self.deactivation_reason:
            status = "blocked"
        elif not self.is_active and self.deactivation_reason:
            status = "deactivated"
        return status

    def send_email_verification(self):
        self.activation_token = create_token()
        self.is_email_verified = False
        self.save()
        # context = {
        #     'username': self.username,
        #     'email': self.email,
        #     'url': build_absolute_uri(f"verify/{self.activation_token}/"),
        # }
        # template = 'emails/sing_up_email.html'
        # subject = 'Email Verification'
        # send_email_on_delay.delay(template, context, subject, self.email)


class Address(models.Model):
    address1 = models.TextField()
    address2 = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=128)
    postal_code = models.CharField(max_length=32)
    country = models.CharField(max_length=128)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_profile"
    )
    # first_name = models.CharField(
    #     max_length=150,
    # )
    # last_name = models.CharField(
    #     max_length=150,
    # )
    address = models.OneToOneField(Address, on_delete=models.DO_NOTHING, null=True, blank=True)
    role = models.CharField(
        max_length=16, choices=RoleChoices.choices, default=RoleChoices.MEMBER
    )  # role of user
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Enter Phone number with country code"
    )  # phone number validator.
    phone = models.CharField(
        _("phone number"),
        validators=[phone_regex],
        max_length=15,
        unique=True,
        blank=True,
        null=True
    )
    is_phone_verified = models.BooleanField(
        default=False
    )
    gender = models.CharField(
        max_length=8,
        choices=GenderChoices.choices,
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )
    # Profile Picture
    photo = ThumbnailerImageField(
        'ProfilePicture',
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    photo_uploaded_on = models.DateTimeField(
        blank=True,
        null=True
    )
    is_profile_pic_verified = models.BooleanField(
        default=False
    )
    rejection_reason_profile_pic = models.TextField(
        blank=True,
        null=True
    )
    # Document
    document_front = models.FileField(
        upload_to='documents',
        blank=True,
        null=True
    )
    document_rear = models.FileField(
        upload_to='documents',
        blank=True,
        null=True
    )
    document_uploaded_on = models.DateTimeField(
        blank=True,
        null=True
    )
    document_expiry_date = models.DateField(
        blank=True,
        null=True
    )
    is_document_verified = models.BooleanField(
        default=False
    )
    rejection_reason_document = models.TextField(
        blank=True,
        null=True
    )

    term_and_condition_accepted = models.BooleanField(
        default=False
    )
    privacy_policy_accepted = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.user.username


class UnitOfHistory(models.Model):
    """We will create log for every action
    those data will store in this model"""

    action = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )  # in this field we will define which action was perform.
    created = models.DateTimeField(
        auto_now_add=True
    )
    old_meta = models.JSONField(
        null=True
    )  # we store data what was the scenario before perform this action.
    new_meta = models.JSONField(
        null=True
    )  # we store data after perform this action.
    header = models.JSONField(
        null=True
    )  # request header that will provide user browser
    # information and others details.
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="performer"
    )  # this user will be action performer.
    perform_for = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="perform_for"
    )  # sometime admin/superior  will perform some
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

    # class Meta:
    #     db_table = f"{settings.DB_PREFIX}_unit_of_history"

    def __str__(self) -> str:
        return self.action or "action"

    @classmethod
    def user_history(
        cls,
        action,
        user,
        request,
        new_meta=None,
        old_meta=None,
        perform_for=None
    ) -> object:
        try:
            data = {i[0]: i[1] for i in request.META.items() if i[0].startswith('HTTP_')}
        except BaseException:
            data = None
        cls.objects.create(
            action=action,
            user=user,
            old_meta=old_meta,
            new_meta=new_meta,
            header=data,
            perform_for=perform_for,
            content_type=ContentType.objects.get_for_model(User),
            object_id=user.id
        )


class ResetPassword(models.Model):
    """
    Reset Password will store user data
    who request for reset password.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    token = models.UUIDField()
    created_on = models.DateTimeField(auto_now_add=True)

    objects = UserPasswordResetManager()

    # class Meta:
    #     db_table = f"{settings.DB_PREFIX}_users_password_reset"


class UserDeviceToken(BaseModel):
    """
    To Trigger FMC notification we need
    device token will store user device token
    to trigger notification.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    device_token = models.CharField(
        max_length=200
    )
    device_type = models.CharField(
        max_length=8,
        choices=DeviceTypeChoices.choices
    )
    objects = UserDeviceTokenManager()

    # class Meta:
    #     db_table = f"{settings.DB_PREFIX}_user_device_tokens"


class UserSocialAccount(BaseModel):
    """Social Account will store will
    type id and for whom."""

    social_id = models.CharField(
        max_length=100
    )
    social_type = models.CharField(
        max_length=20,
        choices=SocialAccountTypeChoices.choices
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    objects = UserSocialAccountManager()

    class Meta:
        # db_table = f"{settings.DB_PREFIX}_user_social_accounts"
        unique_together = (("user", "social_type"),)


class UserOTP(models.Model):
    """
        Store information for user otp verification
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_otp"
    )  # user who responsible for
    otp = models.CharField(max_length=6)  # exact value of one time pin
    created_on = models.DateTimeField(
        auto_now_add=True
    )  # object creation time. will automatically generate
    updated_on = models.DateTimeField(
        auto_now=True
    )  # object update time. will automatically generate

    objects = UserOTPManager()

    def __str__(self):
        return f"{self.user.email}: {self.otp}"

    class Meta:
        # db_table = f"{settings.DB_PREFIX}_user_otps"  # define database table name
        ordering = ['-updated_on']  # define default order as updated_on in descending
        unique_together = ("user", "otp")  # make user and otp unique together

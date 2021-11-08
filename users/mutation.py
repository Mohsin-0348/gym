# at w3universal/backend/users/schema.py
import re

import graphene
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from graphene_django.forms.mutation import DjangoFormMutation
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from backend.authentication import TokenManager
from backend.permissions import is_admin_user, is_authenticated, is_super_admin
from backend.sms import generate_otp  # send_otp
from bases.constants import HistoryActions, VerifyActionChoices
from bases.utils import create_token
from users.choices import RoleChoices
from users.forms import (
    AddressForm,
    AdminRegistrationForm,
    UserRegistrationForm,
    UserUpdateForm,
)
from users.login_backends import signup, social_signup
from users.models import (
    Address,
    ResetPassword,
    UnitOfHistory,
    UserDeviceToken,
    UserOTP,
    UserProfile,
)
from users.object_types import AddressType, UserType

# from users.tasks import send_password_reset_mail

User = get_user_model()


class RegisterUser(DjangoFormMutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    class Meta:
        form_class = UserRegistrationForm

    def mutate_and_get_payload(self, info, **input):
        form = UserRegistrationForm(data=input)
        if form.is_valid():
            if form.cleaned_data['password'] and validate_password(form.cleaned_data['password']):
                pass
            user = User.objects.create_user(**form.cleaned_data)
            UserProfile.objects.create(user=user)
            user.send_email_verification(info.context.headers['host'])
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[error] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        UnitOfHistory.user_history(
            action=HistoryActions.SOCIAL_SINGUP,
            user=user,
            request=info.context
        )
        return RegisterUser(
            message="A mail was sent to this email address.",
            user=user,
            success=True
        )


class UpdateUser(DjangoFormMutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    class Meta:
        form_class = UserUpdateForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        user = info.context.user
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        form = UserUpdateForm(data=input)
        if not created:
            form = UserUpdateForm(data=input, instance=user_profile)
        if User.objects.filter(username=form.data['username']).exclude(id=user.id):
            raise GraphQLError(
                message="Username already exists.",
                extensions={
                    "errors": "Username already exists.",
                    "code": "invalid_input"
                }
            )
        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            del form.cleaned_data['first_name'], form.cleaned_data['last_name'], form.cleaned_data['username']
            if user.is_admin and created:
                form.cleaned_data['role'] = RoleChoices.ADMIN
            UserProfile.objects.filter(id=user_profile.id).update(**form.cleaned_data)
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[error] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        UnitOfHistory.user_history(
            action=HistoryActions.USER_UPDATE,
            user=user,
            request=info.context
        )
        return UpdateUser(
            message="Profile updated successfully.",
            user=user,
            success=True
        )


class AddressMutation(DjangoFormMutation):
    success = graphene.Boolean()
    message = graphene.String()
    address = graphene.Field(AddressType)

    class Meta:
        form_class = AddressForm

    @is_authenticated
    def mutate_and_get_payload(self, info, **input):
        user = info.context.user
        form = AddressForm(data=input)
        if form.is_valid():
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            if user_profile.address:
                address = user_profile.address
                Address.objects.filter(id=address.id).update(**form.cleaned_data)
            else:
                address = Address.objects.create(**form.cleaned_data)
                UserProfile.objects.filter(id=user_profile.id).update(address=address)
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[error] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        UnitOfHistory.user_history(
            action=HistoryActions.ADDRESS_ADDED,
            user=user,
            request=info.context
        )
        return AddressMutation(
            message="Profile updated successfully.",
            address=address,
            success=True
        )


class ResendActivationMail(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info, email):
        user_exist = User.objects.filter(email=email)
        if user_exist:
            if user_exist.filter(is_email_verified=True):
                raise GraphQLError(
                    message="User already verified.",
                    extensions={
                        "errors": "User already verified.",
                        "code": "already_verified"
                    }
                )
            user_exist.last().send_email_verification(info.context.headers['host'])
        else:
            raise GraphQLError(
                message="Invalid email!",
                extensions={
                    "errors": "Invalid email address!",
                    "code": "invalid_email"
                }
            )
        UnitOfHistory.user_history(
            action=HistoryActions.RESEND_ACTIVATION,
            user=user_exist.last(),
            request=info.context
        )
        return ResendActivationMail(
            success=True,
            user=user_exist.last(),
            message="Mail sent successfully."
        )


class LoginUser(graphene.Mutation):
    """
    User Login Mutation::
    user will able to login by email and password
    will get
        1. access_token as access
        2. refresh_token as refresh
        3. user data
        4. success status as bol true or false
    """

    success = graphene.Boolean()
    access = graphene.String()
    refresh = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        activate = graphene.Boolean()

    def mutate(
        self,
        info,
        email,
        password,
        activate=False
    ) -> object:
        user = signup(info.context, email, password, activate)
        access = TokenManager.get_access({"user_id": str(user.id)})
        refresh = TokenManager.get_refresh({"user_id": str(user.id)})

        return LoginUser(
            access=access,
            refresh=refresh,
            user=user,
            success=True
        )


class SocialLogin(graphene.Mutation):
    """
    Social Login Mutation::
    user will be able to sign in via
    social accounts like, facebook
    google and apple etc.
    apple user have to pass id_token
    """

    success = graphene.Boolean()
    access = graphene.String()
    refresh = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        social_type = graphene.String(required=True)
        social_id = graphene.String(required=True)
        email = graphene.String()
        id_token = graphene.String()  # only for apple
        activate = graphene.Boolean()
        verification = graphene.Boolean()

    def mutate(
        self,
        info,
        social_type,
        social_id,
        email,
        id_token=None,
        need_verification=False,
        activate=False
    ):
        if social_type == 'apple' and not id_token:
            raise GraphQLError(
                message="Should provide id token.",
                extensions={
                    "message": "Should provide id token.",
                    "code": "id_token_not_found"
                }
            )

        if not email and id_token and social_type == 'apple':
            email = TokenManager.get_email(id_token)
        user = social_signup(
            info.context,
            social_type,
            social_id,
            email,
            activate,
            need_verification
        )
        access = TokenManager.get_access({"user_id": str(user.id)})
        refresh = TokenManager.get_refresh({"user_id": str(user.id)})

        return SocialLogin(
            access=access,
            refresh=refresh,
            user=user,
            success=True
        )


class GetAccessToken(graphene.Mutation):
    """
    Get Access Mutation::
    if user access token is expired.
    then user will able to get new access token.
    by verifiy theire refresh token.
    """

    access = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        refresh = graphene.String(required=True)

    def mutate(self, info, refresh):
        token = TokenManager.decode_token(refresh)
        if not token or token["type"] != "refresh":
            raise GraphQLError(
                message="Invalid token or has expired",
                extensions={
                    "message": "Invalid token or has expired",
                    "code": "invalid_token"
                }
            )

        access = TokenManager.get_access({"user_id": token["user_id"]})
        return GetAccessToken(
            access=access,
            success=True
        )


class OTPMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        otp = graphene.String(required=False)

    @is_authenticated
    def mutate(self, info, otp=None, **kwargs):
        user = info.context.user
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        if not user_profile.phone:
            raise GraphQLError(
                message="No phone number is associated with this account.",
                extensions={
                    "message": "No phone number is associated with this account.",
                    "code": "no_number_exists"
                }
            )
        elif user_profile.phone and user_profile.is_phone_verified:
            raise GraphQLError(
                message="Phone number is already verified.",
                extensions={
                    "message": "Phone number is already verified.",
                    "code": "already_verified"
                }
            )
        pattern = r"^8801[^02]\d{8}$"
        if not bool(re.match(pattern, user_profile.phone)):
            raise GraphQLError(
                message="Phone number is not valid.(Valid sample- 8801*********).",
                extensions={
                    "message": "Phone number is not valid.(Valid sample- 8801*********).",
                    "code": "invalid_number"
                }
            )
        if not otp:
            gen_otp = generate_otp()
            # try:
            #     send_otp(user_profile.phone, gen_otp)
            # except TwilioRestException:
            #     raise GraphQLError(
            #         message="Not valid number.",
            #         extensions={
            #             "message": "Not valid number.",
            #             "code": "invalid_number"
            #         }
            #     )
            UserOTP.objects.create_or_update(user=user, otp=gen_otp)
        else:
            user_otp = UserOTP.objects.check_otp(otp=otp, user=user)
            if user_otp and user.is_active:
                user_profile.is_phone_verified = True
                user_profile.save()
            else:
                raise GraphQLError(
                    message="OTP is invalid or expired.",
                    extensions={
                        "message": "OTP is invalid or expired.",
                        "code": "invalid_otp"
                    }
                )
        return OTPMutation(success=True,
                           message="Successfully verified." if otp else "OTP sent successfully.",
                           user=user)


class PasswordChange(graphene.Mutation):
    """
    Password Change Mutation::
    Password change by using old password.
    password length should min 8.
    not similar to username or email.
    password must contain number
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        old_password = graphene.String(required=True)
        new_password = graphene.String(required=True)

    @is_authenticated
    def mutate(self, info, old_password, new_password):
        user = info.context.user
        if not user.check_password(old_password):
            raise GraphQLError(
                message="Wrong password",
                extensions={
                    "message": "Wrong password",
                    "code": "wrong_password"
                }
            )

        validate_password(new_password)
        user.set_password(new_password)
        user.save()
        UnitOfHistory.user_history(
            action=HistoryActions.PASSWORD_CHANGE,
            user=user,
            request=info.context
        )
        return PasswordChange(
            success=True,
            message="Password change successful"
        )


class PasswordResetMail(graphene.Mutation):
    """
        Password Rest Mail mutation::
        User will be able to Request Rest their password.
        by using register email.
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info, email):
        user = User.objects.filter(email=email).first()
        if not user:
            raise GraphQLError(
                message="No user associate with this email",
                extensions={
                    "message": "No user associate with this email",
                    "code": "not_found"
                }
            )
        token = create_token()
        ResetPassword.objects.create_or_update(user, token)
        # send_password_reset_mail.delay(email, token)
        UnitOfHistory.user_history(
            action=HistoryActions.PASSWORD_RESET_REQUEST,
            user=user,
            request=info.context
        )
        return PasswordResetMail(
            success=True,
            message="Password reset mail send successfully"
        )


class PasswordReset(graphene.Mutation):
    """
    Password Rest Mutation::
    after getting rest mail user will
    get a link to reset password.
    To verify Password:
        1. password length should min 8.
        2. not similar to username or email.
        3. password must contain number
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        token = graphene.String(required=True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)

    def mutate(
        self,
        info,
        email,
        token,
        password1,
        password2
    ):
        user = User.objects.filter(email=email).first()
        if not user:
            raise GraphQLError(
                message="No user associate with this email",
                extensions={
                    "message": "No user associate with this email",
                    "code": "not_found"
                }
            )
        if not ResetPassword.objects.check_key(token, email):
            raise GraphQLError(
                message="Invalid token or has expired",
                extensions={
                    "message": "Invalid token or has expired",
                    "code": "invalid_token"
                }
            )
        validate_password(password1)
        if not password1 == password2:
            raise GraphQLError(
                message="Password not match",
                extensions={
                    "message": "Password not match",
                    "code": "not_match"
                }
            )
        user.set_password(password2)
        user.save()
        UnitOfHistory.user_history(
            action=HistoryActions.PASSWORD_RESET,
            user=user,
            request=info.context
        )
        return PasswordReset(
            success=True,
            message="Password reset successful"
        )


class ProfilePictureUpload(graphene.Mutation):
    """
    Upload Profile Picture Mutation::
    user will able to upload theire profile picture
    after upload picture will automatic crop.
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        photo = Upload(required=True)

    @is_authenticated
    def mutate(self, info, photo):
        user = info.context.user
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.photo.save(
            f"{user_profile.first_name}_profile{photo.name}",
            photo,
            save=True
        )
        user_profile.photo_uploaded_at = timezone.now()
        user_profile.is_profile_pic_verified = False
        user_profile.rejection_reason_profile_pic = None
        user_profile.save()
        UnitOfHistory.user_history(
            action=HistoryActions.PROFILE_PICTURE_UPLOAD,
            user=user,
            request=info.context
        )
        return ProfilePictureUpload(
            success=True,
            message="profile picture upload successfully"
        )


class DocumentUpload(graphene.Mutation):
    """
    Document Upload Mutation::
    Every user have to upload theire identatiy document.
    it could be passport national id driving license etc.
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        front = Upload(required=True)
        rear = Upload(required=True)

    @is_authenticated
    def mutate(self, info, front, rear):
        user = info.context.user
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.document_front.save(
            f"{user_profile.first_name}document_front{front.name}",
            front,
            save=True
        )
        user_profile.document_rear.save(
            f"{user_profile.first_name}document_rear{rear.name}",
            rear,
            save=True
        )
        user_profile.document_created_at = timezone.now()
        user_profile.is_document_verified = False
        user_profile.document_expiry_date = None
        user_profile.rejection_reason_document = None
        user_profile.save()
        UnitOfHistory.user_history(
            action=HistoryActions.DOCUMENT_UPLOADED,
            user=user,
            request=info.context
        )
        return DocumentUpload(
            success=True,
            message="document upload successfully"
        )


class DeviceToken(graphene.Mutation):
    """
    User Device Token::
    every user will have a device token it could be
    web or mobile device token. to tigger fmc notification.
    """

    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        device_type = graphene.String(required=True)
        device_token = graphene.String(required=True)

    @is_authenticated
    def mutate(
        self,
        info,
        device_type,
        device_token,
    ):
        user = info.context.user
        UserDeviceToken.objects.create_or_update(user, device_type, device_token)
        return DeviceToken(
            success=True,
            message="Token added successfully"
        )


class ProfileDeactivation(graphene.Mutation):
    """
    Account Deactivation Mutation::
    User will be able to deactivate their profile.
    by putting reason why want to deactive.
    """

    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        reason = graphene.String(required=True)

    @is_authenticated
    def mutate(self, info, reason):
        user = info.context.user
        if not reason.strip():
            raise GraphQLError(
                message="User should enter reason.",
                extensions={
                    "message": "User should enter reason.",
                    "code": "reason_not_found"
                }
            )
        user.is_active = False
        user.deactivation_reason = reason
        user.is_expired = True
        user.save()
        UnitOfHistory.user_history(
            action=HistoryActions.ACCOUNT_DEACTIVATE,
            user=user,
            request=info.context
        )
        return ProfileDeactivation(
            success=True,
            message="Deactivation successful"
        )


class UserBlockUnBlock(graphene.Mutation):
    """
    User block or unblock Mutation::
    if admin want to control user access.
    they can block and unblock user.
    """

    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)

    @is_admin_user
    def mutate(self, info, email):
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                user.is_active = False
                user.is_expired = True
                msg = "blocked"
                act = HistoryActions.USER_BLOCKED
            else:
                user.is_active = True
                msg = "unblocked"
                act = HistoryActions.USER_UNBLOCKED
            user.save()
            UnitOfHistory.user_history(
                action=act,
                user=info.context.user,
                request=info.context,
                perform_for=user
            )
            return UserBlockUnBlock(
                user=user,
                success=True,
                message=f"Successfully {msg}"
            )
        except User.DoesNotExist:
            raise GraphQLError(
                message="User not found",
                extensions={
                    "message": "User not found",
                    "code": "not_found"
                }
            )


class VerifyDocuments(graphene.Mutation):
    """
    Document Verification Mutation::
    While Verify Admin have to choose action
    like approve or reject. if reject have to
    reason of rejection.
    """

    message = graphene.String()
    success = graphene.Boolean()
    user = graphene.Field(UserType)

    class Arguments:
        action = graphene.String(required=True)
        reason = graphene.String()
        email = graphene.String(required=True)
        expire_date = graphene.Date()

    @is_admin_user
    def mutate(self, info, email, action, expire_date, reason):
        if action not in [VerifyActionChoices.APPROVE, VerifyActionChoices.REJECT]:
            raise GraphQLError(
                message="Please Choose between 'approve' or 'reject'",
                extensions={
                    "message": "Please Choose between 'approve' or 'reject'",
                    "code": "wrong_selection"
                }
            )
        try:
            user = User.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
            act = ''
            if user_profile.document_front and user_profile.document_rear and user_profile.is_document_verified \
                    and action == "approve":
                raise GraphQLError(
                    message="Documents already verified.",
                    extensions={
                        "message": "Documents already verified.",
                        "code": "verified"
                    }
                )
            elif user_profile.rejection_reason_document and not user_profile.is_document_verified \
                    and action == VerifyActionChoices.REJECT:
                raise GraphQLError(
                    message="Documents already rejected.",
                    extensions={
                        "message": "Documents already rejected.",
                        "code": "verified"
                    }
                )
            elif user_profile.document_front and user_profile.document_rear:
                if action == VerifyActionChoices.APPROVE and expire_date:
                    user_profile.is_document_verified = True
                    user_profile.document_expiry_date = expire_date
                    user_profile.rejection_reason_document = None
                    act = HistoryActions.DOCUMENT_VERIFIED
                elif action == VerifyActionChoices.REJECT and not reason:
                    raise GraphQLError(
                        message="Reason is required for rejection",
                        extensions={
                            "message": "Reason is required for rejection",
                            "code": "required"
                        }
                    )
                elif action == VerifyActionChoices.REJECT and reason:
                    user_profile.is_document_verified = False
                    user_profile.is_document_uploaded = False
                    user_profile.document_expiry_date = None
                    user_profile.rejection_reason_document = reason
                    act = HistoryActions.DOCUMENT_REJECTED
                user_profile.save()
                UnitOfHistory.user_history(
                    action=act,
                    user=info.context.user,
                    request=info.context,
                    perform_for=user
                )
                # document_verification.delay(user.id)
                return VerifyDocuments(
                    user=user,
                    success=True,
                    message=f"Successfully {'verified' if action == VerifyActionChoices.APPROVE else 'rejected'}"
                )
            raise GraphQLError(
                message="Document Not uploaded",
                extensions={
                    "message": "Document Not uploaded",
                    "code": "not_found"
                }
            )
        except User.DoesNotExist:
            raise GraphQLError(
                message="User not found",
                extensions={
                    "message": "User not found",
                    "code": "not_found"
                }
            )


class VerifyProfilePicture(graphene.Mutation):
    """
    Profile Picture Verification Mutation::
    While Verify Admin have to choose action
    like approve or reject. if reject have to
    reason of rejection.
    """

    message = graphene.String()
    success = graphene.Boolean()
    user = graphene.Field(UserType)

    class Arguments:
        action = graphene.String(required=True)
        reason = graphene.String()
        email = graphene.String(required=True)

    @is_admin_user
    def mutate(self, info, email, action, reason):
        if action not in [VerifyActionChoices.APPROVE, VerifyActionChoices.REJECT]:
            raise GraphQLError(
                message="Please Choose between 'approve' or 'reject'",
                extensions={
                    "message": "Please Choose between 'approve' or 'reject'",
                    "code": "wrong_selection"
                }
            )
        try:
            user = User.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.photo and user_profile.is_profile_pic_verified and action == VerifyActionChoices.APPROVE:
                raise GraphQLError(
                    message="Picture already verified.",
                    extensions={
                        "message": "Picture already verified.",
                        "code": "verified"
                    }
                )
            elif user_profile.rejection_reason_profile_pic and not user_profile.is_profile_pic_verified \
                    and action == VerifyActionChoices.REJECT:
                raise GraphQLError(
                    message="Picture already rejected.",
                    extensions={
                        "message": "Picture already rejected.",
                        "code": "verified"
                    }
                )
            elif user_profile.photo:
                act = None
                if action == VerifyActionChoices.APPROVE:
                    user_profile.is_profile_pic_verified = True
                    user_profile.rejection_reason_profile_pic = None
                    act = HistoryActions.PROFILE_PICTURE_VERIFIED
                elif action == VerifyActionChoices.REJECT and not reason:
                    raise GraphQLError(
                        message="Reason is required for rejection",
                        extensions={
                            "message": "Reason is required for rejection",
                            "code": "required"
                        }
                    )
                elif action == VerifyActionChoices.REJECT and reason:
                    user_profile.is_profile_pic_verified = False
                    user_profile.rejection_reason_profile_pic = reason
                    act = HistoryActions.PROFILE_PICTURE_REJECTED
                user_profile.save()
                UnitOfHistory.user_history(
                    action=act,
                    user=info.context.user,
                    request=info.context,
                    perform_for=user
                )
                return VerifyProfilePicture(
                    user=user,
                    success=True,
                    message=f"Successfully {'verified' if action == VerifyActionChoices.APPROVE else 'rejected'}"
                )
            raise GraphQLError(
                message="Picture Not uploaded",
                extensions={
                    "message": "Picture Not uploaded",
                    "code": "not_found"
                }
            )

        except User.DoesNotExist:
            raise GraphQLError(
                message="User not found",
                extensions={
                    "message": "User not found",
                    "code": "not_found"
                }
            )


class AddNewAdmin(DjangoFormMutation):
    """
        Will take email, username and password as required fields.
        And super_user field to define whether admin super user or staff user.
    """

    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    class Meta:
        form_class = AdminRegistrationForm

    @is_super_admin
    def mutate_and_get_payload(self, info, **input):
        form = AdminRegistrationForm(data=input)
        if form.is_valid():
            if form.cleaned_data['password'] and validate_password(form.cleaned_data['password']):
                pass
            super_user = form.cleaned_data['super_user']
            del form.cleaned_data['super_user']
            user = User.objects.create_user(**form.cleaned_data)
            user.is_staff = True
            user.is_superuser = super_user
            user.save()
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[error] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        UnitOfHistory.user_history(
            action=HistoryActions.NEW_ADMIN_ADDED,
            user=info.context.user,
            perform_for=user,
            request=info.context
        )
        return AddNewAdmin(
            message="New admin successfully added.",
            success=True,
            user=user
        )


class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    login_user = LoginUser.Field()
    social_login = SocialLogin.Field()
    get_access = GetAccessToken.Field()
    resend_verification_email = ResendActivationMail.Field()
    upload_profile_picture = ProfilePictureUpload.Field()
    update_profile = UpdateUser.Field()
    document_upload = DocumentUpload.Field()
    password_change = PasswordChange.Field()
    password_reset_mail = PasswordResetMail.Field()
    password_reset = PasswordReset.Field()
    add_device_token = DeviceToken.Field()
    account_deactivate = ProfileDeactivation.Field()
    user_block_or_unblock = UserBlockUnBlock.Field()
    profile_picture_verification = VerifyProfilePicture.Field()
    document_verification = VerifyDocuments.Field()
    otp_mutation = OTPMutation.Field()
    add_new_admin = AddNewAdmin.Field()
    # user_address_mutation = AddressMutation.Field()

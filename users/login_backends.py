# at w3universal/backend/users/login_backends.py
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from graphql import GraphQLError

from bases.constants import HistoryActions
from bases.utils import email_checker

from .models import UnitOfHistory, UserSocialAccount

User = get_user_model()


def check_user(user, activate) -> bool:
    if not user.is_admin and not user.is_email_verified:
        raise GraphQLError(
            message="Please verify your email",
            extensions={
                "message": "Please verify your email",
                "code": "unverified_email"
            }
        )
    elif not user.is_active and user.deactivation_reason:
        if activate:
            user.is_active = True
            user.deactivation_reason = None
            user.save()
        else:
            raise GraphQLError(
                message="Account is deactivated",
                extensions={
                    "message": "Account is deactivated",
                    "code": "account_deactive"
                }
            )
    elif not user.is_active:
        raise GraphQLError(
            message="Account is temporary bolcked",
            extensions={
                "message": "Account is temporary bolcked",
                "code": "account_blocked"
            }
        )
    return True


def signup(
    request,
    email,
    password,
    activate=False
) -> object:
    try:
        user = User.objects.get(email=email)
        if check_user(user, activate):
            user = authenticate(
                username=user.username,
                password=password
            )
            if not user:
                raise GraphQLError(
                    message="Invalid credentials",
                    extensions={
                        "message": "invalid credentials",
                        "code": "invalid_credentials"
                    }
                )
            user.last_login = timezone.now()
            user.save()
            UnitOfHistory.user_history(
                action=HistoryActions.USER_LOGIN,
                user=user,
                request=request
            )
            return user
    except User.DoesNotExist:
        raise GraphQLError(
            message="Email is not associate with any existing user.",
            extensions={
                "message": "Email is not associate with any existing user.",
                "code": "invalid_email"
            }
        )


def social_signup(
    request,
    social_type,
    social_id,
    email,
    activate=False,
    verification=False
):
    user_account = UserSocialAccount.objects.checkSocialAccount(
        social_id,
        social_type,
        email
    )
    if user_account:
        user = UserSocialAccount.objects.get(
            social_type=social_type,
            social_id=social_id
        ).user
        check_user(user, activate)
        user.last_login = timezone.now()
        user.save()
        UnitOfHistory.user_history(
            action=HistoryActions.SOCIAL_LOGIN,
            user=user,
            request=request
        )
        return user
    if not email:
        raise GraphQLError(
            message="Email is required",
            extensions={
                "message": "Email is required",
                "code": "email_not_found"
            }
        )
    elif not email_checker(email):
        raise GraphQLError(
            message="Invalid email address",
            extensions={
                "message": "Invalid email address",
                "code": "invalid_email"
            }
        )
    if email_checker(email):
        if User.objects.filter(email=email).exists():
            raise GraphQLError(
                message="Email is already exits",
                extensions={
                    "message": "Email is already exits",
                    "code": "duplicate_email"
                }
            )
    user = User.objects.create_user(email)
    UserSocialAccount.objects.create(
        user=user,
        social_id=social_id,
        social_type=social_type
    )
    if verification:
        user.send_email_verification()
        raise GraphQLError(
            message="Please verify your email",
            extensions={
                "message": "Please verify your email",
                "code": "unverified_email"
            }
        )
    user.is_email_verified = True
    user.last_login = timezone.now()
    user.save()
    UnitOfHistory.user_history(
        action=HistoryActions.SOCIAL_SINGUP,
        user=user,
        request=request
    )
    return user

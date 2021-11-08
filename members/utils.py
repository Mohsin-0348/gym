
from graphql import GraphQLError

from hr.models import Employee
from users.models import UserProfile


def check_user_role(user, role):
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        user_profile.role = role
        user_profile.save()
        return True
    elif not created and user_profile.role == role:
        return True
    elif not created and user_profile.role != role:
        raise GraphQLError(
            message="User role not valid for this operation.",
            extensions={
                "errors": "User role not valid for this operation.",
                "code": "invalid_role"
            }
        )
    else:
        raise GraphQLError(
            message="Function mis-operated.",
            extensions={
                "errors": "Function mis-operated.",
                "code": "invalid_operation"
            }
        )


def check_trainer(user):
    user_employee = Employee.objects.get(user=user)
    if user_employee.designation == Employee.DesignationChoice.TRAINER or \
            user_employee.designation == Employee.DesignationChoice.ADMINISTRATOR:
        return user_employee
    else:
        raise GraphQLError(
            message="User can't perform this operation.",
            extensions={
                "errors": "User can't perform this operation.",
                "code": "invalid_role"
            }
        )

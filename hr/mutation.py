import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# from django.forms import model_to_dict
# from django.utils import timezone
from graphene_django.forms.mutation import DjangoFormMutation

# from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from backend.permissions import is_admin_user  # , is_authenticated
from bases.constants import HistoryActions
from hr.forms import EmployeeForm
from hr.models import Employee
from users.choices import RoleChoices
from users.forms import UserRegistrationForm
from users.models import UnitOfHistory, UserProfile
from users.object_types import UserType

User = get_user_model()


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


class EmployeeMutation(DjangoFormMutation):
    """

    """
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    class Meta:
        form_class = EmployeeForm

    @is_admin_user
    def mutate_and_get_payload(self, info, **input):
        employee = None
        user_data = {'username': input['username'], 'email': input['email'], 'password': settings.DEFAULT_PASSWORD}
        form = UserRegistrationForm(
            data=user_data
        )
        if input.get('object_id'):
            employee = User.objects.get(id=input['object_id'])
            form = UserRegistrationForm(
                data=user_data, instance=employee
            )
        employee_form = EmployeeForm(data=input)
        if form.is_valid() and employee_form.is_valid():
            del employee_form.cleaned_data['username'], employee_form.cleaned_data['email']
            if employee:
                if employee.username != form.cleaned_data['username']:
                    employee.email = form.cleaned_data['username']
                    employee.save()
                if employee.email != form.cleaned_data['email']:
                    employee.email = form.cleaned_data['email']
                    employee.is_email_verified = False
                    employee.save()
                check_user_role(employee, RoleChoices.EMPLOYEE)
                del employee_form.cleaned_data['object_id']
                employee_user, created = Employee.objects.get_or_create(user=employee)
                Employee.objects.filter(id=employee_user.id).update(**employee_form.cleaned_data)
                action = HistoryActions.EMPLOYEE_UPDATED
            else:
                if validate_password(form.cleaned_data['password']):
                    pass
                employee = User.objects.create_user(**form.cleaned_data)
                employee.send_email_verification(info.context.headers['host'])
                UserProfile.objects.create(user=employee, role=RoleChoices.EMPLOYEE)
                employee_form.cleaned_data['user'] = employee
                Employee.objects.create(**employee_form.cleaned_data)
                action = HistoryActions.EMPLOYEE_ADDED
        else:
            error_data = {}
            for error in form.errors:
                for err in form.errors[error]:
                    error_data[error] = err
            for error in employee_form.errors:
                for err in employee_form.errors[error]:
                    error_data[error] = err
            raise GraphQLError(
                message="Invalid input request.",
                extensions={
                    "errors": error_data,
                    "code": "invalid_input"
                }
            )
        UnitOfHistory.user_history(
            action=action,
            user=info.context.user,
            perform_for=employee,
            request=info.context
        )
        return EmployeeMutation(
            success=True,
            message=f"Employee successfully {'updated' if action == HistoryActions.EMPLOYEE_UPDATED else 'added'}.",
            user=employee
        )


class Mutation(graphene.ObjectType):
    employee_mutation = EmployeeMutation.Field()

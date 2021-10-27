# at w3universal/backend/users/schema.py

import graphene
from django.contrib.auth import get_user_model
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from backend.permissions import is_admin_user, is_authenticated
from users.models import UnitOfHistory
from users.object_types import LogType, UserType

User = get_user_model()


class Query(graphene.ObjectType):
    user = graphene.relay.Node.Field(UserType)
    users = DjangoFilterConnectionField(UserType)
    me = graphene.Field(UserType)
    logs = DjangoFilterConnectionField(LogType)
    log = graphene.relay.Node.Field(LogType)

    @is_authenticated
    def resolve_me(self, info) -> object:
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError(
                message='Your are not login',
                extensions={
                    "message": "Your are not login",
                    "code": "unauthorised"
                })
        return user

    @is_admin_user
    def resolve_users(self, info, **kwargs) -> object:
        return User.objects.all()

    @is_admin_user
    def resolve_logs(self, info, **kwargs) -> object:
        return UnitOfHistory.objects.all()

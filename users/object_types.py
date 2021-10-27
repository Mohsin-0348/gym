# at w3universal/backend/users/schema.py

import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from backend.count_connection import CountConnection
from users.filters import AddressFilters, LogsFilters, UserFilters, UserProfileFilters
from users.models import Address, UnitOfHistory, UserProfile

User = get_user_model()


class UserType(DjangoObjectType):
    object_id = graphene.Boolean()

    class Meta:
        model = User
        filterset_class = UserFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection

    @staticmethod
    def resolve_object_id(self, info, **kwargs):
        return self.id


class UserProfileType(DjangoObjectType):

    class Meta:
        model = UserProfile
        filterset_class = UserProfileFilters
        interfaces = (graphene.relay.Node, )
        convert_choices_to_enum = False
        connection_class = CountConnection


class LogType(DjangoObjectType):
    class Meta:
        model = UnitOfHistory
        filterset_class = LogsFilters
        interfaces = (graphene.relay.Node, )
        connection_class = CountConnection


class AddressType(DjangoObjectType):
    class Meta:
        model = Address
        filterset_class = AddressFilters
        interfaces = (graphene.relay.Node, )
        connection_class = CountConnection

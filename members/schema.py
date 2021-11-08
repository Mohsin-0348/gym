import graphene

from members.mutation import Mutation as memberMutation
from members.query import Query as memberQuery


class Query(memberQuery, graphene.ObjectType):
    pass


class Mutation(memberMutation, graphene.ObjectType):
    pass

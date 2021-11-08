import graphene

from hr.mutation import Mutation as hrMutation
from hr.query import Query as hrQuery


class Query(hrQuery, graphene.ObjectType):
    pass


class Mutation(hrMutation, graphene.ObjectType):
    pass

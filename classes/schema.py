import graphene

from classes.mutation import Mutation as classMutation
from classes.query import Query as classQuery


class Query(classQuery, graphene.ObjectType):
    pass


class Mutation(classMutation, graphene.ObjectType):
    pass

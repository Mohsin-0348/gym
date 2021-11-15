import graphene

from attendances.mutation import Mutation as attendanceMutation
from attendances.query import Query as attendanceQuery


class Query(attendanceQuery, graphene.ObjectType):
    pass


class Mutation(attendanceMutation, graphene.ObjectType):
    pass

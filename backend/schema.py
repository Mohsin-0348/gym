import graphene

import classes.schema as class_schema
import hr.schema as hr_schema
import members.schema as member_schema
import users.schema as user_schema


class Query(
    user_schema.Query,
    member_schema.Query,
    hr_schema.Query,
    class_schema.Query,
    graphene.ObjectType
):
    pass


class Mutation(
    user_schema.Mutation,
    member_schema.Mutation,
    hr_schema.Mutation,
    class_schema.Mutation,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

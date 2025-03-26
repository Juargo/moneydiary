""" Esquema de GraphQL """
import strawberry

@strawberry.type
class Query:
    """ Query type """
    @strawberry.field
    def hello(self) -> str:
        """ Hello world """
        return "Hola desde GraphQL 🚀"

schema = strawberry.Schema(query=Query)

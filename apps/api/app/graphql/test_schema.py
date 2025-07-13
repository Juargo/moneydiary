import strawberry

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World!"
    
    @strawberry.field
    def version(self) -> str:
        return "1.0.0"

# Schema mínimo para testing
test_schema = strawberry.Schema(query=Query)
# Ejemplos de consultas GraphQL para usuarios

## Configuración

Asegúrate de tener tu servidor GraphQL ejecutándose. La URL típica sería: `http://localhost:8000/graphql`.

## Consultar todos los usuarios

```graphql
query {
  users {
    id
    username
    createdAt
    updatedAt
  }
}
```

## Consultar un usuario específico por ID

```graphql
query {
  user(userId: 1) {
    id
    username
    createdAt
    updatedAt
  }
}
```

## Consulta con campos seleccionados

Solo solicitar el nombre de usuario:

```graphql
query {
  users {
    username
  }
}
```

## Consulta con GraphQL variables

```graphql
query GetUser($userId: Int!) {
  user(userId: $userId) {
    id
    username
    createdAt
  }
}
```

Variables:
```json
{
  "userId": 1
}
```

## Uso con curl

```bash
# Consulta de todos los usuarios
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "{ users { id username createdAt updatedAt } }"}' \
  http://localhost:8000/graphql

# Consulta de un usuario específico
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "{ user(userId: 1) { id username createdAt updatedAt } }"}' \
  http://localhost:8000/graphql
```

## Uso con Python requests

```python
import requests

# URL del endpoint GraphQL
url = 'http://localhost:8000/graphql'

# Consulta de todos los usuarios
query_all = """
{
  users {
    id
    username
    createdAt
    updatedAt
  }
}
"""

response = requests.post(url, json={'query': query_all})
print(response.json())

# Consulta de un usuario específico
query_one = """
{
  user(userId: 1) {
    id
    username
    createdAt
    updatedAt
  }
}
"""

response = requests.post(url, json={'query': query_one})
print(response.json())
```

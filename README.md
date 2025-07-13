# MoneyDiary

# MoneyDiary

Sistema de gestión y proyección de finanzas personales.

## Descripción

MoneyDiary es una aplicación completa para gestionar y proyectar tus finanzas personales utilizando diferentes métodos:

- Presupuesto 50/30/20
- Método de Sobres (Envelopes)
- Sistema Cero (Zero-Based Budgeting)
- Método Kakebo
- Pay Yourself First

## Estructura del Proyecto

Este proyecto utiliza una arquitectura de monorepo con una versión unificada:

- `apps/web`: Frontend con Astro, Vue y Tailwind
- `apps/api`: Backend con FastAPI y GraphQL
- `apps/android`: App nativa para Android con Kotlin
- `apps/ios`: App nativa para iOS/Mac con Swift
- `packages/`: Componentes compartidos

## Requisitos

- Node.js 18+
- PNPM 8+
- Python 3.9+
- PostgreSQL 14+
- Docker y Docker Compose (opcional)
- Android Studio y JDK 17+ (para desarrollo Android)
- Xcode 14+ (para desarrollo iOS/Mac)

## Desarrollo

### Instalar dependencias

```bash
pnpm install
```

### Iniciar todos los servicios en modo desarrollo

```bash
pnpm dev
```

### Construir para producción

```bash
pnpm build
```

## Docker

Para ejecutar la aplicación completa con Docker:

```bash
cd docker
docker-compose up -d
```

## Contribuciones

Por favor, utiliza commits convencionales para tus contribuciones:

```
feat(alcance): descripción
fix(alcance): descripción
```

## Licencia

MIT

# Estrategia de API MoneyDiary

MoneyDiary implementa una estrategia API híbrida que aprovecha las fortalezas de REST y GraphQL.

## Principios

1. **REST para escrituras, GraphQL para lecturas complejas**
2. **Capa de servicios compartida para ambos protocolos**
3. **Documentación clara sobre qué usar para cada operación**

## REST API (`/api/v1/*`)

### Casos de uso recomendados:

- Autenticación y gestión de sesiones
- Operaciones de creación, actualización y eliminación (POST, PUT, DELETE)
- Consultas simples con parámetros fijos (GET)
- Operaciones que siguen estándares HTTP para caché, códigos de estado, etc.

### Ejemplos:

- `POST /api/v1/auth/refresh-token`
- `POST /api/v1/banks`
- `PUT /api/v1/accounts/123`
- `DELETE /api/v1/transactions/456`
- `GET /api/v1/user/me`

## GraphQL (`/graphql`)

### Casos de uso recomendados:

- Consultas que relacionan múltiples entidades
- Selección dinámica de campos (evitar over-fetching)
- Consultas con filtros y ordenamiento complejos
- Datos anidados y relacionales

### Ejemplos:

```graphql
# Obtener transacciones con sus categorías y cuentas
query {
  transactions(
    filter: {
      dateRange: { start: "2023-01-01", end: "2023-12-31" }
      categoryIds: [1, 2, 3]
    }
    pagination: { limit: 10, offset: 0 }
    sort: { field: "date", order: DESC }
  ) {
    id
    amount
    description
    date
    category {
      id
      name
      group
    }
    account {
      id
      name
      balance
    }
  }
}
```

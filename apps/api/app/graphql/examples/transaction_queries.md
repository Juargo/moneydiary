# Ejemplos de Queries GraphQL para Transacciones

## 1. Obtener todas las transacciones del usuario autenticado

```graphql
query GetMyTransactions {
  myTransactions {
    transactions {
      id
      amount
      description
      notes
      transactionDate
      accountId
      statusId
      isRecurring
      isPlanned
      kakeboEmotion
    }
    totalCount
    hasNextPage
    hasPreviousPage
  }
}
```

## 2. Obtener transacciones con filtros

```graphql
query GetMyTransactionsFiltered {
  myTransactions(
    filters: {
      accountId: 1
      startDate: "2025-01-01"
      endDate: "2025-12-31"
      minAmount: "100.00"
      maxAmount: "5000.00"
      descriptionContains: "supermercado"
    }
    skip: 0
    limit: 20
  ) {
    transactions {
      id
      amount
      description
      notes
      transactionDate
      accountId
      transferAccountId
      subcategoryId
      envelopeId
      statusId
      externalId
      isRecurring
      isPlanned
      kakeboEmotion
    }
    totalCount
    hasNextPage
    hasPreviousPage
  }
}
```

## 3. Obtener transacciones con paginación

```graphql
query GetMyTransactionsPaginated {
  myTransactions(skip: 20, limit: 10) {
    transactions {
      id
      amount
      description
      transactionDate
      accountId
    }
    totalCount
    hasNextPage
    hasPreviousPage
  }
}
```

## 4. Obtener una transacción específica

```graphql
query GetMyTransaction {
  myTransaction(transactionId: 123) {
    id
    amount
    description
    notes
    transactionDate
    accountId
    transferAccountId
    subcategoryId
    envelopeId
    statusId
    recurringPatternId
    importId
    importRowNumber
    externalId
    isRecurring
    isPlanned
    kakeboEmotion
  }
}
```

## 5. Filtros por fecha y cuenta

```graphql
query GetRecentTransactions {
  myTransactions(
    filters: { accountId: 2, startDate: "2025-07-01" }
    skip: 0
    limit: 50
  ) {
    transactions {
      id
      amount
      description
      transactionDate
      accountId
    }
    totalCount
    hasNextPage
    hasPreviousPage
  }
}
```

## Tipos de datos disponibles

### TransactionFilters (input)

- `accountId`: Int (opcional) - Filtrar por cuenta específica
- `startDate`: Date (opcional) - Fecha de inicio (formato: YYYY-MM-DD)
- `endDate`: Date (opcional) - Fecha de fin (formato: YYYY-MM-DD)
- `subcategoryId`: Int (opcional) - Filtrar por subcategoría
- `minAmount`: String (opcional) - Monto mínimo (formato: "100.00")
- `maxAmount`: String (opcional) - Monto máximo (formato: "5000.00")
- `descriptionContains`: String (opcional) - Texto a buscar en la descripción

### Transaction (output)

- `id`: Int - ID único de la transacción
- `userId`: Int - ID del usuario propietario
- `accountId`: Int - ID de la cuenta
- `transferAccountId`: Int (opcional) - ID de cuenta de transferencia
- `subcategoryId`: Int (opcional) - ID de subcategoría
- `envelopeId`: Int (opcional) - ID de sobre de presupuesto
- `statusId`: Int - ID del estado de la transacción
- `recurringPatternId`: Int (opcional) - ID del patrón de recurrencia
- `importId`: Int (opcional) - ID del import origin
- `importRowNumber`: Int (opcional) - Número de fila del import
- `externalId`: String (opcional) - ID externo
- `amount`: String - Monto (formato decimal como string)
- `description`: String (opcional) - Descripción de la transacción
- `notes`: String (opcional) - Notas adicionales
- `transactionDate`: Date - Fecha de la transacción
- `isRecurring`: Boolean - Si es una transacción recurrente
- `isPlanned`: Boolean - Si es una transacción planificada
- `kakeboEmotion`: String (opcional) - Emoción Kakebo asociada

### TransactionConnection (output)

- `transactions`: [Transaction] - Lista de transacciones
- `totalCount`: Int - Número total de transacciones encontradas
- `hasNextPage`: Boolean - Si hay más resultados disponibles
- `hasPreviousPage`: Boolean - Si hay resultados anteriores

## Autenticación

Todas las queries requieren autenticación. Incluye el token JWT en el header:

```
Authorization: Bearer <tu_jwt_token>
```

## Errores comunes

1. **"Usuario no autenticado"** - El token JWT no es válido o no está presente
2. **"ID de usuario no válido"** - Problema con el token o contexto de usuario
3. **"Transacción no encontrada"** - La transacción solicitada no existe o no pertenece al usuario
4. **"Error obteniendo transacciones"** - Error general del servidor

## Notas importantes

- Los montos se devuelven como strings para mantener la precisión decimal
- Las fechas usan el formato ISO (YYYY-MM-DD)
- La paginación usa `skip` (offset) y `limit` (cantidad máxima)
- Los filtros son opcionales y se pueden combinar
- Solo se retornan las transacciones del usuario autenticado

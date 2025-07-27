# APIs de Patrones de Descripción

Este sistema permite crear patrones que analizan automáticamente las descripciones de las transacciones y las categorizan en subcategorías específicas.

## Comandos SQL de Migración

Ejecuta primero estos comandos SQL en tu base de datos:

```sql
-- Crear tabla para patrones de descripción
CREATE TABLE description_patterns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    pattern VARCHAR NOT NULL,
    pattern_type VARCHAR NOT NULL DEFAULT 'contains' CHECK (pattern_type IN ('contains', 'starts_with', 'ends_with', 'regex', 'exact')),
    subcategory_id INTEGER NOT NULL REFERENCES subcategories(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 0,
    is_case_sensitive BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    auto_apply BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla para registro de coincidencias de patrones (auditoría)
CREATE TABLE pattern_matches (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    pattern_id INTEGER NOT NULL REFERENCES description_patterns(id) ON DELETE CASCADE,
    matched_text VARCHAR,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    was_manual_override BOOLEAN DEFAULT FALSE
);

-- Crear índices para mejor rendimiento
CREATE INDEX idx_description_patterns_user_id ON description_patterns(user_id);
CREATE INDEX idx_description_patterns_active ON description_patterns(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_description_patterns_priority ON description_patterns(user_id, priority DESC, id);
CREATE INDEX idx_pattern_matches_transaction_id ON pattern_matches(transaction_id);
CREATE INDEX idx_pattern_matches_pattern_id ON pattern_matches(pattern_id);
```

## Tipos de Patrones

1. **contains**: Busca si el patrón está contenido en cualquier parte de la descripción
2. **starts_with**: Busca si la descripción comienza con el patrón
3. **ends_with**: Busca si la descripción termina con el patrón
4. **exact**: Busca una coincidencia exacta
5. **regex**: Utiliza expresiones regulares para búsquedas avanzadas

## API REST

### Obtener patrones del usuario

```http
GET /description-patterns?active_only=true&skip=0&limit=100
Authorization: Bearer {token}
```

### Crear un nuevo patrón

```http
POST /description-patterns
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Supermercado",
  "pattern": "JUMBO|LIDER|SANTA ISABEL",
  "pattern_type": "regex",
  "subcategory_id": 123,
  "priority": 10,
  "is_case_sensitive": false,
  "is_active": true,
  "auto_apply": true,
  "notes": "Detecta compras en supermercados principales"
}
```

### Probar patrones contra una descripción

```http
POST /description-patterns/test
Authorization: Bearer {token}
Content-Type: application/json

{
  "description": "COMPRA JUMBO MAIPU",
  "pattern_ids": [1, 2, 3]  // opcional, si no se envía prueba todos
}
```

### Generar sugerencias automáticas

```http
POST /description-patterns/suggestions
Authorization: Bearer {token}
Content-Type: application/json

{
  "limit": 10,
  "min_occurrences": 3
}
```

### Aplicar patrón retroactivamente

```http
POST /description-patterns/{pattern_id}/apply
Authorization: Bearer {token}
Content-Type: application/json

{
  "transaction_ids": [1, 2, 3]  // opcional, si no se envía aplica a todas las transacciones
}
```

## API GraphQL

### Queries

```graphql
# Obtener patrones del usuario
query GetMyPatterns($activeOnly: Boolean, $skip: Int, $limit: Int) {
  myDescriptionPatterns(activeOnly: $activeOnly, skip: $skip, limit: $limit) {
    id
    name
    pattern
    patternType
    subcategory {
      id
      name
      categoryName
    }
    priority
    isActive
    autoApply
    createdAt
  }
}

# Probar patrones
query TestPatterns($input: PatternTestInput!) {
  testDescriptionPatterns(input: $input) {
    description
    bestMatch {
      patternId
      patternName
      matched
      subcategory {
        name
        categoryName
      }
    }
    results {
      patternId
      patternName
      pattern
      matched
      matchedText
    }
  }
}

# Obtener sugerencias
query GetSuggestions($input: PatternSuggestionInput!) {
  suggestDescriptionPatterns(input: $input) {
    suggestions {
      suggestedPattern
      patternType
      descriptionSample
      occurrenceCount
      confidenceScore
    }
  }
}

# Estadísticas
query GetPatternStats {
  descriptionPatternStatistics {
    totalPatterns
    activePatterns
    autoApplyPatterns
    totalMatches
  }
}
```

### Mutations

```graphql
# Crear patrón
mutation CreatePattern($input: DescriptionPatternCreateInput!) {
  createDescriptionPattern(input: $input) {
    id
    name
    pattern
    patternType
    subcategory {
      id
      name
    }
    priority
    isActive
    autoApply
  }
}

# Actualizar patrón
mutation UpdatePattern(
  $patternId: Int!
  $input: DescriptionPatternUpdateInput!
) {
  updateDescriptionPattern(patternId: $patternId, input: $input) {
    id
    name
    pattern
    isActive
  }
}

# Eliminar patrón
mutation DeletePattern($patternId: Int!) {
  deleteDescriptionPattern(patternId: $patternId)
}

# Aplicar patrón retroactivamente
mutation ApplyPattern($patternId: Int!, $transactionIds: [Int]) {
  applyPatternToTransactions(
    patternId: $patternId
    transactionIds: $transactionIds
  )
}
```

## Ejemplos de Uso

### 1. Detectar compras en supermercados

```json
{
  "name": "Supermercados",
  "pattern": "jumbo|lider|santa isabel|tottus",
  "pattern_type": "regex",
  "subcategory_id": 15,
  "priority": 100,
  "is_case_sensitive": false
}
```

### 2. Detectar transferencias

```json
{
  "name": "Transferencias",
  "pattern": "transferencia",
  "pattern_type": "contains",
  "subcategory_id": 8,
  "priority": 90,
  "is_case_sensitive": false
}
```

### 3. Detectar pagos de servicios

```json
{
  "name": "Servicios básicos",
  "pattern": "^(AGUA|LUZ|GAS|TELEFONO)",
  "pattern_type": "regex",
  "subcategory_id": 22,
  "priority": 80,
  "is_case_sensitive": false
}
```

### 4. Detectar Netflix específicamente

```json
{
  "name": "Netflix",
  "pattern": "NETFLIX",
  "pattern_type": "exact",
  "subcategory_id": 45,
  "priority": 95,
  "is_case_sensitive": false
}
```

## Flujo de Aplicación Automática

1. Cuando se crea una nueva transacción, el sistema automáticamente:

   - Busca patrones activos del usuario ordenados por prioridad
   - Evalúa cada patrón contra la descripción de la transacción
   - Aplica el primer patrón que coincida y tenga `auto_apply: true`
   - Registra la coincidencia en `pattern_matches` para auditoría

2. Los patrones se evalúan en orden de prioridad (mayor número = mayor prioridad)

3. Solo se aplica automáticamente un patrón por transacción

## Consideraciones

- Los patrones regex deben seguir la sintaxis de Python/PostgreSQL
- Los patrones con mayor prioridad se evalúan primero
- Las coincidencias se registran para análisis y mejora futura
- Los usuarios pueden activar/desactivar la aplicación automática por patrón
- Se puede aplicar patrones retroactivamente a transacciones existentes

# Sistema de Previsualización de Importación de Transacciones

## Descripción

El sistema de previsualización permite a los usuarios ver y validar las transacciones que van a ser importadas antes de confirmar la inserción en la base de datos. Esto permite:

1. **Previsualizar** las transacciones extraídas del archivo
2. **Validar** los datos y ver errores de importación
3. **Modificar** transacciones individuales si es necesario
4. **Seleccionar** qué transacciones importar
5. **Confirmar** la importación final

## Flujo de Uso

### 1. Generar Previsualización

**Endpoint:** `POST /api/transactions/preview-import`

**Parámetros:**

- `profile_id` (form): ID del perfil de importación
- `file` (file): Archivo CSV o Excel a procesar

**Respuesta:**

```json
{
  "preview_id": "uuid-string",
  "total_records": 100,
  "valid_transactions": 95,
  "invalid_transactions": 5,
  "account_id": 1,
  "account_name": "Cuenta Corriente",
  "profile_name": "Perfil Banco ABC",
  "transactions": [
    {
      "row_number": 1,
      "amount": 100.5,
      "description": "Compra supermercado",
      "transaction_date": "2024-01-15",
      "account_id": 1,
      "account_name": "Cuenta Corriente",
      "is_valid": true,
      "validation_errors": [],
      "raw_data": {
        "col_0": "15/01/2024",
        "col_1": "Compra supermercado",
        "col_2": "-100.50"
      }
    },
    {
      "row_number": 2,
      "amount": null,
      "description": "Transferencia",
      "transaction_date": null,
      "account_id": 1,
      "account_name": "Cuenta Corriente",
      "is_valid": false,
      "validation_errors": [
        "Monto requerido",
        "Fecha de transacción requerida"
      ],
      "raw_data": {
        "col_0": "fecha_invalida",
        "col_1": "Transferencia",
        "col_2": ""
      }
    }
  ],
  "global_errors": []
}
```

### 2. Confirmar Importación

**Endpoint:** `POST /api/transactions/confirm-import`

**Body:**

```json
{
  "preview_id": "uuid-string",
  "selected_transactions": [1, 3, 5], // Opcional: números de fila a importar
  "modifications": {
    // Opcional: modificaciones por fila
    "1": {
      "amount": 105.0,
      "description": "Compra supermercado - MODIFICADO"
    }
  }
}
```

**Respuesta:**

```json
{
  "total_records": 3,
  "successful_imports": 3,
  "failed_imports": 0,
  "errors": []
}
```

## Características del Sistema

### Validaciones Automáticas

El sistema valida automáticamente:

- **Monto requerido** y diferente de cero
- **Fecha de transacción** requerida y válida
- **Descripción** requerida
- **Subcategoría** existente (si se especifica)

### Datos Enriquecidos

Cada transacción en la previsualización incluye:

- Nombre de la cuenta
- Nombre de la subcategoría (si existe)
- Datos originales del archivo para referencia
- Estado de validación y errores específicos

### Cache Temporal

Las previsualizaciones se almacenan temporalmente:

- **Duración:** 1 hora
- **Identificador único:** UUID para cada previsualización
- **Seguridad:** Solo el usuario propietario puede acceder

### Flexibilidad de Importación

Al confirmar, puedes:

- **Importar todas** las transacciones válidas (por defecto)
- **Seleccionar específicas** usando `selected_transactions`
- **Modificar datos** usando `modifications` antes de importar

## Ejemplo de Uso en Frontend

```javascript
// 1. Subir archivo para previsualización
const formData = new FormData();
formData.append("profile_id", "1");
formData.append("file", fileInput.files[0]);

const previewResponse = await fetch("/api/transactions/preview-import", {
  method: "POST",
  body: formData,
  headers: {
    Authorization: `Bearer ${token}`,
  },
});

const preview = await previewResponse.json();

// 2. Mostrar preview al usuario, permitir modificaciones

// 3. Confirmar importación
const confirmRequest = {
  preview_id: preview.preview_id,
  selected_transactions: [1, 2, 3], // Solo estas filas
  modifications: {
    2: {
      amount: 150.0, // Modificar monto de la fila 2
      description: "Descripción corregida",
    },
  },
};

const confirmResponse = await fetch("/api/transactions/confirm-import", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify(confirmRequest),
});

const result = await confirmResponse.json();
console.log(
  `Importadas: ${result.successful_imports}, Fallidas: ${result.failed_imports}`
);
```

## Ventajas

1. **Transparencia:** El usuario ve exactamente qué se va a importar
2. **Control:** Puede seleccionar y modificar transacciones individualmente
3. **Validación:** Errores detectados antes de la importación
4. **Flexibilidad:** Soporte para CSV y Excel con cualquier perfil configurado
5. **Seguridad:** Cache temporal con expiración automática

## Limitaciones

- Cache temporal de 1 hora (configurable)
- Requiere perfiles de importación previamente configurados
- No persiste cambios hasta la confirmación

# 🚀 Sistema de Previsualización de Importación - Frontend

## Descripción

El nuevo sistema de importación de transacciones con previsualización permite a los usuarios ver y validar exactamente qué transacciones van a ser importadas antes de confirmar la operación.

## 🔄 Flujo de Usuario

### 1. Selección de Perfil y Archivo

- El usuario selecciona una cuenta y perfil de importación
- Carga un archivo CSV o Excel
- Hace clic en "Generar Previsualización"

### 2. Previsualización y Validación

- El sistema muestra todas las transacciones extraídas del archivo
- Cada transacción muestra:
  - ✅ Estado (Válida/Error)
  - 📅 Fecha
  - 📝 Descripción
  - 💰 Monto
  - ⚠️ Errores de validación (si los hay)
- Estadísticas en tiempo real (total, válidas, errores, seleccionadas)

### 3. Edición y Selección

- **Editar transacciones**: Corregir datos incorrectos directamente en la tabla
- **Seleccionar transacciones**: Marcar/desmarcar individualmente o en lote
- **Filtrar vista**: Mostrar solo errores para corregirlos rápidamente
- **Validación automática**: Los cambios se validan en tiempo real

### 4. Confirmación Final

- Revisar el resumen de transacciones seleccionadas
- Confirmar importación
- Ver resultados finales

## 🎯 Características Principales

### ✨ Previsualización Completa

```javascript
// El sistema genera un preview completo antes de importar
{
  "preview_id": "uuid-único",
  "total_records": 100,
  "valid_transactions": 95,
  "invalid_transactions": 5,
  "account_name": "Cuenta Corriente",
  "profile_name": "Perfil Banco XYZ",
  "transactions": [...]
}
```

### 🔧 Edición en Línea

- **Editar campos**: Fecha, descripción, monto directamente en la tabla
- **Validación automática**: Los errores se actualizan al guardar cambios
- **Selección inteligente**: Las transacciones corregidas se seleccionan automáticamente

### ⚡ Selección Inteligente

- **Seleccionar todas las válidas**: Un clic para marcar todas las transacciones sin errores
- **Filtro de errores**: Mostrar solo transacciones con problemas
- **Contador dinámico**: Número de transacciones seleccionadas se actualiza en tiempo real

### 🛡️ Validaciones Automáticas

El sistema valida automáticamente:

- ✅ **Monto requerido** y diferente de cero
- ✅ **Fecha válida** y en formato correcto
- ✅ **Descripción presente**
- ✅ **Subcategorías existentes** (si se especifican)

## 🔧 Implementación Técnica

### Componente Principal

```vue
<!-- TransactionImportPreview.vue -->
<TransactionImportPreview client:load />
```

### Estados de la Aplicación

```javascript
// Estados principales
const preview = ref(null); // Datos de previsualización
const selectedTransactions = ref([]); // Transacciones seleccionadas
const modifications = ref({}); // Modificaciones del usuario
const editingRow = ref(null); // Fila en edición
```

### Endpoints Utilizados

```javascript
// 1. Generar previsualización
POST /api/v1/transactions/preview-import
// FormData: profile_id, file

// 2. Confirmar importación
POST /api/v1/transactions/confirm-import
// JSON: { preview_id, selected_transactions, modifications }
```

## 📊 Ventajas vs Sistema Anterior

| Aspecto          | Sistema Anterior     | Nuevo Sistema              |
| ---------------- | -------------------- | -------------------------- |
| **Visibilidad**  | Importación ciega    | Previsualización completa  |
| **Control**      | Todo o nada          | Selección granular         |
| **Errores**      | Descubrir después    | Validación previa          |
| **Correcciones** | No posible           | Edición en línea           |
| **Confianza**    | Baja (incertidumbre) | Alta (transparencia total) |

## 🚀 Casos de Uso

### Caso 1: Archivo con Errores

```
1. Usuario sube CSV con 100 transacciones
2. Sistema encuentra 95 válidas, 5 con errores
3. Usuario ve errores: "Sin fecha", "Monto vacío"
4. Corrige directamente en la tabla
5. Confirma importación de todas las 100
```

### Caso 2: Importación Selectiva

```
1. Usuario sube Excel con transacciones mixtas
2. Quiere importar solo gastos, no ingresos
3. Filtra y deselecciona ingresos manualmente
4. Importa solo las transacciones deseadas
```

### Caso 3: Validación de Datos

```
1. Usuario no está seguro del formato de fechas
2. Ve en preview que algunas fechas están mal
3. Corrige formato antes de importar
4. Evita inconsistencias en la base de datos
```

## 🎨 Interfaz de Usuario

### Estados Visuales

- 🟢 **Verde**: Transacciones válidas
- 🔴 **Rojo**: Transacciones con errores
- 🟡 **Amarillo**: Transacción en edición
- 🔵 **Azul**: Elementos interactivos

### Controles Principales

- **Checkboxes**: Selección individual y masiva
- **Botones de edición**: "Editar", "Guardar", "Cancelar"
- **Filtros**: "Mostrar solo errores"
- **Estadísticas**: Contadores en tiempo real

## 🔄 Integración con Sistema Existente

### Rutas Actualizadas

```astro
<!-- import.astro -->
import TransactionImportPreview from "TransactionImportPreview.vue";
```

### Compatibilidad

- ✅ Funciona con todos los perfiles de importación existentes
- ✅ Soporte completo para CSV y Excel
- ✅ Validaciones compatibles con el modelo de datos actual
- ✅ Sin cambios en la base de datos requeridos

## 🚀 Estado: PRODUCCIÓN LISTA

- ✅ Componente frontend completamente funcional
- ✅ Integración con backend implementada
- ✅ Validaciones automáticas activas
- ✅ Manejo de errores robusto
- ✅ Experiencia de usuario optimizada
- ✅ Responsive design para mobile/desktop

**El sistema está listo para uso inmediato en producción.**

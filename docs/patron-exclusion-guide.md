# 📝 Guía de Patrones de Exclusión y Transferencias Internas

## 🎯 Objetivo

Esta guía te ayuda a configurar patrones para manejar transacciones especiales como transferencias entre tus cuentas, comisiones bancarias y otros movimientos que no representan gastos reales.

## 📋 Categorías Especiales Creadas

### 🔄 **Transferencias**

- **Transferencia Interna**: Para movimientos entre tus propias cuentas
- **Ejemplos**: "TRASPASO A:Yobancoestadocorriente", "TRANSFERENCIA A CUENTA AHORROS"

### ⚙️ **Sistema**

- **Ignorar**: Para transacciones que deben ser completamente ignoradas en reportes
- **Ajuste de Saldo**: Para correcciones bancarias automáticas
- **Comisión Bancaria**: Para fees y comisiones del banco

## 🚀 Cómo Configurar Patrones

### 1. **Para Transferencias Internas**

**Ejemplo de tu caso:**

```
Descripción: "Traspaso A:Yobancoestadocorriente"

Patrón a crear:
- Nombre: "Transferencias a Yobanco"
- Patrón: "TRASPASO.*A:Yobanco"
- Tipo: "regex"
- Categoría: "Transferencias > Transferencia Interna"
- Prioridad: 100 (alta)
- Auto-aplicar: ✅ Sí
```

### 2. **Para Comisiones Bancarias**

```
Ejemplos:
- "COMISION MANEJO CUENTA"
- "COSTO TRANSACCION"
- "RETENCION 4X1000"

Patrón a crear:
- Nombre: "Comisiones Bancarias"
- Patrón: "(COMISION|COSTO|RETENCION)"
- Tipo: "regex"
- Categoría: "Sistema > Comisión Bancaria"
- Prioridad: 90
```

### 3. **Para Ignorar Completamente**

```
Ejemplos:
- "REVERSO DE TRANSACCION"
- "NOTA CREDITO"
- "AJUSTE SISTEMA"

Patrón a crear:
- Nombre: "Movimientos a Ignorar"
- Patrón: "(REVERSO|NOTA CREDITO|AJUSTE)"
- Tipo: "regex"
- Categoría: "Sistema > Ignorar"
- Prioridad: 95
```

## 🎛️ Configuración de Prioridades

**Sistema de Prioridades (mayor número = mayor prioridad):**

1. **100-90**: Patrones de exclusión (transferencias, ignorar)
2. **50-89**: Patrones específicos (restaurantes, supermercados)
3. **10-49**: Patrones generales (transporte, entretenimiento)
4. **1-9**: Patrones de respaldo o muy generales

## 📊 Ventajas de este Sistema

### ✅ **Para Transferencias Internas:**

- **Trazabilidad**: Mantienes registro del flujo de dinero
- **Reportes limpios**: Puedes filtrarlas fácilmente en análisis
- **Balance correcto**: No afectan tus gastos reales

### ✅ **Para Ignorar:**

- **Reportes precisos**: No distorsionan tus estadísticas
- **Análisis limpio**: Solo ves gastos e ingresos reales

### ✅ **Para Comisiones:**

- **Categorización clara**: Identificas costos bancarios
- **Análisis de fees**: Puedes evaluar qué banco es más económico

## 🛠️ Patrones Regex Útiles

### Para Transferencias:

```regex
^(TRASPASO|TRANSFERENCIA|TRASFERENCIA).*A:
```

### Para Comisiones:

```regex
(COMISION|COSTO|MANEJO|CUOTA|FEE|RETENCION)
```

### Para Reversas/Ajustes:

```regex
(REVERSO|REVERSA|DEVOLUCION|AJUSTE|NOTA CREDITO)
```

### Para Nombres de Bancos:

```regex
(BANCOLOMBIA|DAVIVIENDA|BANCO.*BOGOTA|NEQUI|DAVIPLATA)
```

## 📈 Casos de Uso Recomendados

### 🔄 **Transferencias Entre Cuentas**

**Recomendación**: Usa categoría "Transferencias"

- Mantienes visibilidad del flujo
- Puedes analizar patrones de uso de cuentas
- Fácil de filtrar en reportes

### 🚫 **Movimientos Técnicos**

**Recomendación**: Usa categoría "Sistema > Ignorar"

- Reversas de transacciones
- Ajustes automáticos del banco
- Notas crédito por errores

### 💰 **Costos Bancarios**

**Recomendación**: Usa categoría "Sistema > Comisión Bancaria"

- Manejo de cuenta
- Retenciones automáticas
- Costos por transacciones

## 🎯 Ejemplo Completo para tu Caso

**Tu descripción**: `"Traspaso A:Yobancoestadocorriente"`

**Patrón recomendado:**

```
📝 Nombre: "Transferencias Yobanco"
🔍 Patrón: "TRASPASO.*A:Yobanco"
📊 Tipo: "regex"
📁 Categoría: "Transferencias > Transferencia Interna"
⚡ Prioridad: 100
✅ Auto-aplicar: Sí
📋 Notas: "Transferencias entre mis cuentas Yobanco"
```

**Resultado**:

- ✅ La transacción se categoriza como "Transferencia Interna"
- ✅ No afecta tus reportes de gastos
- ✅ Mantienes trazabilidad del movimiento
- ✅ Puedes filtrarla en análisis cuando sea necesario

## 🚀 Próximos Pasos

1. **Crear el patrón** en la interfaz de patrones
2. **Probar** con algunas transacciones de ejemplo
3. **Ajustar** el regex si es necesario
4. **Replicar** para otros tipos de transferencias o bancos

¡Con este sistema tendrás un control total sobre cómo se categorizan tus transacciones especiales!

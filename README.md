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
- `packages/`: Componentes compartidos

## Requisitos

- Node.js 18+
- PNPM 8+
- Python 3.9+
- PostgreSQL 14+
- Docker y Docker Compose (opcional)

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

# Etapa de construcción
FROM node:18-alpine AS build

# Establecer directorio de trabajo
WORKDIR /app

# Instalar pnpm
RUN npm install -g pnpm

# Copiar archivos de dependencias
COPY frontend/package*.json ./
COPY frontend/pnpm-lock.yaml ./

# Instalar dependencias (usando el equivalente de pnpm a npm ci)
RUN pnpm install --frozen-lockfile

# Copiar el resto del código fuente
COPY frontend/ ./

# Construir la aplicación
RUN pnpm run build

# Etapa de producción
FROM nginx:alpine

# Copiar la configuración personalizada de nginx (opcional)
# COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copiar los archivos de la etapa de construcción
COPY --from=build /app/dist /usr/share/nginx/html

# Exponer el puerto 80
EXPOSE 80

# Comando para iniciar nginx
CMD ["nginx", "-g", "daemon off;"]

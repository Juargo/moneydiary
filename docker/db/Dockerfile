
FROM postgres:15

# Configuración de localización para soporte de caracteres
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

# Copiar scripts de inicialización
COPY ./init/ /docker-entrypoint-initdb.d/

# Variables de entorno para configuración
ENV POSTGRES_USER=moneydiary
ENV POSTGRES_PASSWORD=moneydiary_password
ENV POSTGRES_DB=moneydiary

# Puerto por defecto de PostgreSQL
EXPOSE 5432

# Volumen para persistencia de datos
VOLUME /var/lib/postgresql/data
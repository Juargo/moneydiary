# Despliegue en DigitalOcean

Este directorio contiene la configuración necesaria para desplegar MoneyDiary en un servidor de DigitalOcean.

## Requisitos previos

1. Crear un droplet en DigitalOcean con Docker preinstalado
2. Configurar los secrets en GitHub (ver sección de Secrets)

## Estructura de directorios en el servidor

El deploy automáticamente creará la siguiente estructura:

```
~/
├── .env                      # Variables de entorno
├── docker-compose.prod.yml   # Archivo de composición
└── docker/
    ├── data/                 # Datos persistentes del API
    └── nginx/
        ├── conf.d/           # Configuración de Nginx
        ├── certs/            # Certificados SSL
        └── www/              # Archivos estáticos
```

## Configuración SSL

### Opción 1: Generar certificados Let's Encrypt (Recomendado para producción)

Let's Encrypt ofrece certificados SSL gratuitos y automáticos. Para implementarlos:

1. Asegúrate de que tu dominio apunta a la IP del servidor
2. Instala Certbot en el servidor:

```bash
ssh usuario@servidor
apt-get update
apt-get install certbot
```

3. Obtén el certificado (detén primero el Nginx si está en ejecución):

```bash
docker-compose -f docker-compose.prod.yml stop nginx
certbot certonly --standalone -d tudominio.com -d www.tudominio.com
```

4. Copia los certificados generados al directorio de Nginx:

```bash
mkdir -p ~/docker/nginx/certs
cp /etc/letsencrypt/live/tudominio.com/fullchain.pem ~/docker/nginx/certs/cert.pem
cp /etc/letsencrypt/live/tudominio.com/privkey.pem ~/docker/nginx/certs/key.pem
chmod 755 ~/docker/nginx/certs
```

5. Reinicia los servicios:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

6. Configura la renovación automática:

```bash
echo "0 0,12 * * * root docker-compose -f ~/docker-compose.prod.yml stop nginx && certbot renew --quiet && cp /etc/letsencrypt/live/tudominio.com/fullchain.pem ~/docker/nginx/certs/cert.pem && cp /etc/letsencrypt/live/tudominio.com/privkey.pem ~/docker/nginx/certs/key.pem && docker-compose -f ~/docker-compose.prod.yml up -d nginx" | sudo tee -a /etc/crontab > /dev/null
```

### Opción 2: Generar certificados autofirmados (Solo para desarrollo)

Para entornos de desarrollo o pruebas:

```bash
ssh usuario@servidor
cd ~
mkdir -p docker/nginx/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/certs/key.pem \
  -out docker/nginx/certs/cert.pem \
  -subj "/C=US/ST=YourState/L=YourCity/O=YourOrganization/CN=yourdomain.com"
chmod 755 docker/nginx/certs
chmod 644 docker/nginx/certs/cert.pem docker/nginx/certs/key.pem
```

### Opción 3: Añadir soporte Certbot usando Docker

Alternativamente, puedes usar el contenedor de Certbot para gestionar los certificados:

1. Añade un servicio de certbot al docker-compose.prod.yml
2. Ejecuta:

```bash
docker-compose -f docker-compose.prod.yml run --rm certbot
```

## Secrets del Proyecto

Para que el proyecto funcione correctamente, debes configurar los siguientes secrets en tu repositorio de GitHub:

### Secrets para el despliegue en DigitalOcean

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `SSH_PRIVATE_KEY` | Clave SSH privada para acceder al servidor | `-----BEGIN OPENSSH PRIVATE KEY-----\n...\n-----END OPENSSH PRIVATE KEY-----` |
| `SSH_KNOWN_HOSTS` | Resultado del comando `ssh-keyscan IP_DEL_SERVIDOR` | `192.168.1.1 ssh-rsa AAAAB3NzaC1...` |
| `DO_HOST` | Dirección IP del servidor de DigitalOcean | `143.198.123.456` |
| `DO_USER` | Usuario para acceder al servidor | `root` |

### Secrets para la base de datos MySQL

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `MYSQL_HOST` | Host de la base de datos MySQL | `db.example.com` o `localhost` |
| `MYSQL_PORT` | Puerto de MySQL | `3306` |
| `MYSQL_DB` | Nombre de la base de datos | `moneydiary` |
| `MYSQL_USER` | Usuario de MySQL | `moneydiaryuser` |
| `MYSQL_PASSWORD` | Contraseña de MySQL | `secretpassword` |

### Secrets para la configuración SSL y Dominio

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `DOMAIN` | Nombre de dominio para tu aplicación | `moneydiary.com` |
| `SSL_EMAIL` | Email para notificaciones de Let's Encrypt | `admin@moneydiary.com` |

### Secrets para la comunicación entre servicios

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `BACKEND_URL` | URL pública del backend (para el frontend) | `https://api.moneydiary.com` o `http://api:8000` |

### Cómo configurar los secrets en GitHub

1. Ve a tu repositorio en GitHub
2. Haz clic en "Settings" (Configuración)
3. En el panel lateral, haz clic en "Secrets and variables" → "Actions"
4. Haz clic en "New repository secret"
5. Añade cada uno de los secrets mencionados anteriormente

## Verificación de la configuración

Para asegurarte de que todos los secrets necesarios están configurados correctamente, puedes usar la siguiente lista de verificación:

- [ ] SSH_PRIVATE_KEY está configurado
- [ ] SSH_KNOWN_HOSTS está configurado
- [ ] DO_HOST está configurado
- [ ] DO_USER está configurado
- [ ] MYSQL_HOST está configurado
- [ ] MYSQL_PORT está configurado
- [ ] MYSQL_DB está configurado
- [ ] MYSQL_USER está configurado
- [ ] MYSQL_PASSWORD está configurado
- [ ] DOMAIN está configurado (opcional, para SSL)
- [ ] SSL_EMAIL está configurado (opcional, para SSL)
- [ ] BACKEND_URL está configurado

## Despliegue manual

Si necesitas hacer un despliegue manual:

```bash
ssh usuario@servidor
cd ~
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## Logs y monitoreo

Ver logs de los contenedores:

```bash
docker logs moneydiary-api
docker logs moneydiary-frontend
docker logs moneydiary-nginx
```

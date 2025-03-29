# MoneyDiary

## Configuración del Despliegue Automático a Hostinger

### Configuración en GitHub

1. Ve a la configuración de tu repositorio en GitHub (Settings)
2. Navega a "Secrets and variables" > "Actions"
3. Añade los siguientes secretos:
   - `HOSTINGER_FTP_SERVER`: El servidor FTP de Hostinger (ej. ftp.tudominio.com)
   - `HOSTINGER_FTP_USERNAME`: Tu nombre de usuario FTP
   - `HOSTINGER_FTP_PASSWORD`: Tu contraseña FTP
   - `HOSTINGER_FTP_PATH`: La ruta donde se desplegará el frontend (ej. /public_html)
   - `HOSTINGER_API_PATH`: La ruta donde se desplegará el backend (ej. /public_html/api)

### Configuración en Hostinger

1. Accede a tu panel de control de Hostinger
2. Configura el acceso FTP:
   - Crea una cuenta FTP específica para GitHub Actions con permisos limitados
   - Anota el servidor, usuario y contraseña

3. Configuración de PHP para el backend (si es necesario):
   - Habilita la extensión de PHP para ejecutar código Python
   - Configura el archivo .htaccess para redirigir las solicitudes API

4. Estructura de directorios recomendada en Hostinger:
   - `/public_html` - Aplicación frontend
   - `/public_html/api` - API backend

### Verificación

Después de configurar todo, haz un push a la rama principal para activar el despliegue automático.
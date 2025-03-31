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

#### Configuración detallada de los secretos en GitHub

Los secretos son variables cifradas que se almacenan de forma segura en GitHub y solo se exponen a las GitHub Actions durante la ejecución.

**Pasos detallados para configurar secretos:**

1. **Acceder a la configuración de secretos:**
   - Ve a tu repositorio en GitHub
   - Haz clic en "Settings" (pestaña de configuración)
   - En el menú lateral izquierdo, selecciona "Secrets and variables"
   - Haz clic en "Actions"

2. **Crear nuevos secretos:**
   - Haz clic en el botón "New repository secret"
   - Ingresa el nombre del secreto (ej. `HOSTINGER_FTP_SERVER`)
   - Ingresa el valor correspondiente
   - Haz clic en "Add secret" para guardarlo
   - Repite el proceso para cada secreto necesario

3. **Tipos de secretos disponibles:**
   - **Secretos a nivel de repositorio:** Disponibles solo para un repositorio específico
   - **Secretos a nivel de organización:** Disponibles para múltiples repositorios dentro de una organización
   - **Secretos a nivel de entorno:** Disponibles solo cuando se ejecuta un workflow en un entorno específico

4. **Mejores prácticas de seguridad:**
   - No almacenes información sensible directamente en los archivos del repositorio
   - Utiliza secretos separados para cada credencial o información sensible
   - Rota regularmente las credenciales (especialmente contraseñas FTP)
   - Considera usar credenciales con el menor nivel de privilegios necesario
   - Revisa periódicamente los secretos almacenados para eliminar los que ya no sean necesarios

5. **Uso de secretos en los workflows:**
   - Los secretos se acceden usando la sintaxis: `${{ secrets.NOMBRE_DEL_SECRETO }}`
   - Ejemplo en un workflow:
     ```yaml
     - name: Deploy via FTP
       uses: SamKirkland/FTP-Deploy-Action@v4.3.4
       with:
         server: ${{ secrets.HOSTINGER_FTP_SERVER }}
         username: ${{ secrets.HOSTINGER_FTP_USERNAME }}
         password: ${{ secrets.HOSTINGER_FTP_PASSWORD }}
         local-dir: ./dist/
         server-dir: ${{ secrets.HOSTINGER_FTP_PATH }}/
     ```

6. **Limitaciones importantes:**
   - Los valores de los secretos no pueden ser visualizados una vez guardados
   - Los valores de los secretos se enmascaran en los logs de GitHub Actions
   - El tamaño máximo de un secreto es de 64 KB
   - Se pueden almacenar hasta 1,000 secretos por repositorio
   - Los nombres de los secretos solo pueden contener caracteres alfanuméricos y guiones bajos

7. **Verificación de secretos configurados:**
   - Puedes verificar qué secretos están configurados revisando la página de secretos
   - Aunque no puedes ver los valores, puedes actualizar o eliminar secretos existentes

### Configuración en Hostinger

1. Accede a tu panel de control de Hostinger
2. Configura el acceso FTP:
   - Crea una cuenta FTP específica para GitHub Actions con permisos limitados
   - Anota el servidor, usuario y contraseña

3. Configuración para el backend Python:
   - Hostinger cuenta con Python 3.9.21 preinstalado que podemos utilizar directamente
   - Configuración de entorno Python:
     - Accede a tu servidor mediante SSH (si tu plan lo permite)
     - Verifica la disponibilidad de Python con `python3 --version`
     - Crea un entorno virtual (opcional): `python3 -m venv venv`
     - Asegúrate de que los paquetes necesarios estén instalados
   
   - Configuración del .htaccess para Python:
     - Crea un archivo .htaccess en tu directorio API
     - Configura las reglas para redirigir las solicitudes al script Python WSGI
     - Habilita el módulo CGI/WSGI si es necesario desde cPanel

   - Configuración de archivo WSGI para Python (passenger_wsgi.py):
     - Este archivo actúa como punto de entrada para las solicitudes web
     - Define la aplicación WSGI que manejará las peticiones
     - Asegúrate de que tenga permisos de ejecución

4. Estructura de directorios recomendada en Hostinger:
   - `/public_html` - Aplicación frontend
   - `/public_html/api` - API backend Python con configuración WSGI

### Verificación

Después de configurar todo, haz un push a la rama principal para activar el despliegue automático.

### Configuración de Python con WSGI

Crea un archivo passenger_wsgi.py en la carpeta /public_html/api con el siguiente contenido:

```python
import sys
import os

# Añadir el directorio actual al path de Python
INTERP = os.path.expanduser("/usr/bin/python3")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Añadir directorio de la aplicación al path
sys.path.append(os.getcwd())

# Importar la aplicación Flask/FastAPI
from app import app as application

# Para depuración
import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
```

### Configuración de .htaccess para Python

```
# Habilitar el motor de reescritura
RewriteEngine On

# No redirigir para archivos o directorios existentes
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d

# Redirigir todas las solicitudes a passenger_wsgi.py
RewriteRule ^(.*)$ passenger_wsgi.py/$1 [QSA,L]

# Permitir encabezados CORS
Header set Access-Control-Allow-Origin "*"
Header set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header set Access-Control-Allow-Headers "Content-Type, Authorization"
```

# Money Diary

Sistema de gestión de finanzas personales con API backend en Python y frontend en Astro.

## Estructura del Proyecto

```
/
├── backend/                # Backend desarrollado con Python
│   ├── api/                # Código fuente de la API
│   │   ├── main.py         # Punto de entrada principal
│   │   └── ...             # Otros módulos y paquetes
│   └── Dockerfile          # Dockerfile para construir la imagen del backend
├── frontend/               # Frontend desarrollado con Astro
│   ├── src/                # Código fuente del frontend
│   ├── public/             # Archivos estáticos
│   ├── package.json        # Dependencias y scripts
│   └── Dockerfile          # Dockerfile para construir la imagen del frontend
├── docker/                 # Configuración para despliegue en producción
│   ├── docker-compose.prod.yml  # Configuración para producción
│   └── ...                 # Otros archivos de configuración
├── requirement.txt         # Dependencias de Python para el backend
└── .github/                # Configuración de GitHub Actions
    └── workflows/          # Workflows para CI/CD
```

## Desarrollo Local

### Requisitos

- Python 3.9+ para el backend
- Node.js para el frontend
- Docker y Docker Compose (para desarrollo con contenedores)
- Base de datos MySQL

### Configuración del Entorno de Desarrollo

1. Clona el repositorio:
   ```bash
   git clone https://github.com/juargo/moneydiary.git
   cd moneydiary
   ```

2. Configura el backend Python:
   ```bash
   # Crear entorno virtual
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   
   # Instalar dependencias
   pip install -r requirement.txt
   
   # Configurar variables de entorno (opcional)
   cp .env.example .env
   # Edita .env con tus configuraciones
   
   # Ejecutar el backend
   cd backend
   uvicorn api.main:app --reload
   ```

3. Configura el frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Despliegue

El proyecto utiliza GitHub Actions para automatizar el despliegue:

1. **Build and Push Docker Images**: Construye y publica las imágenes Docker del backend Python y frontend en GitHub Container Registry.
2. **Deploy to DigitalOcean**: Despliega las imágenes en un servidor de DigitalOcean utilizando el archivo docker-compose.prod.yml.

Para más detalles sobre el despliegue, consulta el [README de Docker](/docker/README.md).

## Secrets y Variables de Entorno

El proyecto requiere varios secrets para funcionar correctamente en producción. Todos estos secrets deben configurarse en GitHub Actions.

Consulta la [lista completa de secrets](/docker/README.md#secrets-del-proyecto) para obtener más detalles.

## Licencia

[Tipo de licencia]
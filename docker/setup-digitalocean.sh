#!/bin/bash
# Este script configura un Droplet de DigitalOcean para ejecutar Docker

# Actualizar el sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar utilidades básicas
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    unzip \
    certbot

# Instalar Docker si no está instalado
if ! command -v docker &> /dev/null; then
    echo "Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    
    # Configurar para que Docker se inicie en el arranque
    sudo systemctl enable docker
    sudo systemctl start docker
fi

# Instalar Docker Compose si no está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "Instalando Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.17.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Crear directorios para la aplicación
mkdir -p ~/moneydiary/data
mkdir -p ~/moneydiary/nginx/conf.d
mkdir -p ~/moneydiary/nginx/certs
mkdir -p ~/moneydiary/nginx/www

# Configurar firewall (opcional pero recomendado)
echo "Configurando firewall UFW..."
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw allow 8000  # Para el backend si necesita ser accesible directamente

# Habilitar el firewall
echo "y" | sudo ufw enable

# Configurar monitorización básica
echo "Instalando herramientas de monitorización..."
sudo apt-get install -y htop iotop

# Aumentar límites de sistema para mejor rendimiento
echo "Configurando límites de sistema..."
cat << EOF | sudo tee /etc/sysctl.d/99-docker-performance.conf
fs.file-max = 100000
vm.max_map_count = 262144
EOF

sudo sysctl -p /etc/sysctl.d/99-docker-performance.conf

# Información para configurar DNS
echo "============================================="
echo "CONFIGURACIÓN DE DNS PARA TU DOMINIO:"
echo "============================================="
echo "Apunta los siguientes registros A a la IP de este servidor:"
IP_ADDRESS=$(curl -s ifconfig.me)
echo "   moneydiary.com -> $IP_ADDRESS"
echo "   www.moneydiary.com -> $IP_ADDRESS"
echo "   api.moneydiary.com -> $IP_ADDRESS"
echo "============================================="

# Verificar la conectividad con MySQL externo
echo "============================================="
echo "VERIFICACIÓN DE CONECTIVIDAD CON MYSQL EXTERNO"
echo "============================================="
echo "Para verificar la conectividad al servidor MySQL externo:"

# Instalar cliente MySQL para pruebas
sudo apt-get install -y mysql-client

echo "Ejecuta el siguiente comando para probar la conexión:"
echo "mysql -h \$MYSQL_HOST -P \$MYSQL_PORT -u \$MYSQL_USER -p\$MYSQL_PASSWORD -e 'SELECT 1;'"
echo

# Agregar recomendaciones de seguridad para MySQL externo
echo "============================================="
echo "RECOMENDACIONES DE SEGURIDAD PARA MYSQL EXTERNO:"
echo "============================================="
echo "1. Asegúrate de que el servidor MySQL permita conexiones solo desde IPs específicas"
echo "2. Usa usuario y contraseña seguros"
echo "3. Considera usar una VPN o túnel SSH para conexiones a la base de datos"
echo "4. Habilita SSL/TLS para la conexión MySQL si está disponible"
echo "5. Realiza backups regulares de la base de datos externa"
echo "============================================="

# Backup automático (opcional)
echo "Configurando backup automático de volúmenes de Docker..."
cat << 'EOF' | sudo tee /usr/local/bin/docker-backup.sh
#!/bin/bash
BACKUP_DIR=/var/backups/docker
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
mkdir -p $BACKUP_DIR

# Backups de volúmenes importantes
docker run --rm -v mysql_data:/source -v $BACKUP_DIR:/backup alpine tar -czf /backup/mysql-data-$TIMESTAMP.tar.gz -C /source .

# Mantener solo los últimos 7 backups
find $BACKUP_DIR -name "mysql-data-*.tar.gz" -type f -mtime +7 -delete
EOF

sudo chmod +x /usr/local/bin/docker-backup.sh

# Agregar el backup a crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/docker-backup.sh") | crontab -

echo "============================================="
echo "CONFIGURACIÓN COMPLETADA"
echo "============================================="
echo "Para configurar SSL, ejecuta:"
echo "cd ~/moneydiary && ./setup-ssl.sh"
echo 
echo "Para iniciar la aplicación:"
echo "cd ~/moneydiary && docker-compose up -d"
echo "============================================="

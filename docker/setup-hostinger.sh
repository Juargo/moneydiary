#!/bin/bash
# Este script configura un servidor de Hostinger para ejecutar Docker

# Actualizar el sistema
sudo apt-get update && sudo apt-get upgrade -y

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

# Crear directorios necesarios
mkdir -p ~/moneydiary-api/data

# Mostrar información para configuración de Nginx
echo "============================================="
echo "Para configurar Nginx como proxy inverso:"
echo "============================================="
echo "Crea un archivo de configuración en /etc/nginx/sites-available/moneydiary.conf con:"
echo "
server {
    listen 80;
    server_name api.tudominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
"

echo "Luego actívalo con:"
echo "sudo ln -s /etc/nginx/sites-available/moneydiary.conf /etc/nginx/sites-enabled/"
echo "sudo nginx -t"
echo "sudo systemctl restart nginx"
echo "============================================="

# Probar conectividad al servidor MySQL externo
echo "============================================="
echo "Probando conectividad con el servidor MySQL externo:"
echo "============================================="
echo "Asegúrate de que el servidor MySQL externo permite conexiones desde este host."
echo "Puedes probar la conectividad con:"
echo "mysql -h \$MYSQL_HOST -P \$MYSQL_PORT -u \$MYSQL_USER -p\$MYSQL_PASSWORD"
echo "============================================="

# Añadir información sobre la seguridad
echo "============================================="
echo "IMPORTANTE - Seguridad de la base de datos:"
echo "============================================="
echo "1. Verifica que el firewall del servidor MySQL permita conexiones desde este host."
echo "2. Si usas un servidor MySQL en la nube, asegúrate de que la dirección IP del"
echo "   servidor Hostinger esté en la lista blanca de conexiones."
echo "3. Considera usar SSL/TLS para conexiones seguras a tu base de datos."
echo "============================================="

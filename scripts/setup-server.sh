#!/bin/bash

# Server Setup Script for Keelo.ai
# Run this on a fresh Ubuntu 22.04 server

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

DOMAIN=${1:-keelo.ai}
EMAIL=${2:-admin@keelo.ai}

print_status "Setting up server for $DOMAIN"

# Step 1: Update system
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y

# Step 2: Install required packages
print_status "Installing required packages..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    ufw \
    fail2ban \
    nginx \
    certbot \
    python3-certbot-nginx \
    htop \
    git

# Step 3: Install Docker
print_status "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Step 4: Configure firewall
print_status "Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Step 5: Configure fail2ban
print_status "Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
EOF
systemctl restart fail2ban

# Step 6: Create deployment directory
print_status "Creating deployment directory..."
mkdir -p /opt/keelo
mkdir -p /opt/keelo/nginx/ssl
mkdir -p /opt/keelo/backup
chown -R $SUDO_USER:$SUDO_USER /opt/keelo

# Step 7: Setup SSL with Let's Encrypt
print_status "Setting up SSL certificate..."
certbot certonly --nginx \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    -d $DOMAIN \
    -d www.$DOMAIN \
    -d api.$DOMAIN

# Copy certificates to Docker volume location
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/keelo/nginx/ssl/$DOMAIN.crt
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/keelo/nginx/ssl/$DOMAIN.key

# Step 8: Setup automatic SSL renewal
print_status "Setting up SSL auto-renewal..."
cat > /etc/systemd/system/certbot-renewal.service << EOF
[Unit]
Description=Certbot Renewal
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/certbot renew --quiet --deploy-hook "cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/keelo/nginx/ssl/$DOMAIN.crt && cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/keelo/nginx/ssl/$DOMAIN.key && docker-compose -f /opt/keelo/docker-compose.yml restart nginx"
EOF

cat > /etc/systemd/system/certbot-renewal.timer << EOF
[Unit]
Description=Run certbot renewal twice daily

[Timer]
OnCalendar=*-*-* 00,12:00:00
RandomizedDelaySec=3600
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable certbot-renewal.timer
systemctl start certbot-renewal.timer

# Step 9: Setup backup script
print_status "Setting up backup script..."
cat > /opt/keelo/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/keelo/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose -f /opt/keelo/docker-compose.yml exec -T postgres pg_dump -U postgres keelo > $BACKUP_DIR/keelo_db_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "keelo_db_*.sql" -mtime +7 -delete

# Optional: Upload to S3
# aws s3 cp $BACKUP_DIR/keelo_db_$DATE.sql s3://your-backup-bucket/
EOF
chmod +x /opt/keelo/backup.sh

# Setup cron for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/keelo/backup.sh") | crontab -

# Step 10: Setup monitoring
print_status "Setting up monitoring..."
docker run -d \
    --name=netdata \
    -p 19999:19999 \
    -v /etc/passwd:/host/etc/passwd:ro \
    -v /etc/group:/host/etc/group:ro \
    -v /proc:/host/proc:ro \
    -v /sys:/host/sys:ro \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    --cap-add SYS_PTRACE \
    --security-opt apparmor=unconfined \
    netdata/netdata

# Step 11: System optimizations
print_status "Applying system optimizations..."
cat >> /etc/sysctl.conf << EOF

# Network optimizations for web server
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30
net.ipv4.ip_local_port_range = 1024 65535

# Security
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
EOF
sysctl -p

# Step 12: Create deployment user
print_status "Creating deployment user..."
useradd -m -s /bin/bash deploy || true
usermod -aG docker deploy
echo "deploy ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/docker-compose" >> /etc/sudoers

print_status "Server setup complete!"
print_status "Next steps:"
echo "1. Copy your .env.production file to /opt/keelo/.env"
echo "2. Copy your docker-compose.prod.yml to /opt/keelo/docker-compose.yml"
echo "3. Deploy your application using the deploy.sh script"
echo ""
print_status "Monitoring available at: http://$DOMAIN:19999"
print_status "Don't forget to:"
echo "- Configure DNS A records for $DOMAIN, www.$DOMAIN, and api.$DOMAIN"
echo "- Set up your environment variables in .env.production"
echo "- Configure GitHub secrets for CI/CD"
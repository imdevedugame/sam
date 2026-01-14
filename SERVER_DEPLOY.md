# 🖥️ Deploy ke VPS/Server Sendiri

## 📋 Prerequisites

Server Anda harus punya:
- ✅ Ubuntu/Debian Linux (18.04+)
- ✅ Root access
- ✅ Port 80 terbuka untuk web traffic
- ✅ Minimal 512MB RAM

---

## 🚀 Quick Deploy (Otomatis)

### Langkah 1: Jalankan Script Deploy

```bash
# Anda sudah di /var/www/sam, jalankan:
chmod +x deploy.sh
./deploy.sh
```

Script akan otomatis:
1. ✅ Install Python 3.11
2. ✅ Setup virtual environment
3. ✅ Install dependencies
4. ✅ Configure systemd service
5. ✅ Setup Nginx reverse proxy
6. ✅ Start aplikasi

---

## 📝 Manual Deploy (Jika Script Error)

### 1. Install Dependencies

```bash
# Update system
apt-get update
apt-get upgrade -y

# Install Python dan tools
apt-get install -y python3.11 python3.11-venv python3-pip
apt-get install -y nginx supervisor
```

### 2. Setup Virtual Environment

```bash
cd /var/www/sam

# Create venv
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt

# Deactivate
deactivate
```

### 3. Test App Manual

```bash
# Test run (untuk cek kalau ada error)
source venv/bin/activate
python app.py

# Buka browser: http://YOUR_SERVER_IP:5001
# Kalau berhasil, tekan Ctrl+C untuk stop
```

### 4. Create Systemd Service

```bash
nano /etc/systemd/system/distributed-flask.service
```

Paste ini:

```ini
[Unit]
Description=Distributed Flask Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/sam
Environment="PATH=/var/www/sam/venv/bin"
Environment="CONSISTENCY_MODE=eventual"
Environment="REPLICATION_DELAY=3"
Environment="QUORUM_SIZE=2"
Environment="PORT=5001"
ExecStart=/var/www/sam/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5001 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save (Ctrl+X, Y, Enter)

### 5. Configure Nginx

```bash
nano /etc/nginx/sites-available/distributed-flask
```

Paste ini:

```nginx
server {
    listen 80;
    server_name _;  # Ganti dengan domain Anda jika punya

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Save dan enable:

```bash
# Enable site
ln -s /etc/nginx/sites-available/distributed-flask /etc/nginx/sites-enabled/

# Remove default site
rm /etc/nginx/sites-enabled/default

# Test config
nginx -t

# Restart Nginx
systemctl restart nginx
```

### 6. Set Permissions

```bash
chown -R www-data:www-data /var/www/sam
chmod -R 755 /var/www/sam
```

### 7. Start Services

```bash
# Reload systemd
systemctl daemon-reload

# Enable auto-start
systemctl enable distributed-flask

# Start service
systemctl start distributed-flask

# Check status
systemctl status distributed-flask
```

---

## ✅ Verifikasi Deploy

### Check Service Status

```bash
# Check app status
systemctl status distributed-flask

# Check Nginx status
systemctl status nginx

# Check logs
journalctl -u distributed-flask -f
```

### Test Endpoints

```bash
# Test API
curl http://localhost/

# Test write
curl -X POST http://localhost/write \
  -H "Content-Type: application/json" \
  -d '{"value": 100}'

# Test read
curl http://localhost/read/node1
```

### Access dari Browser

```
# Ganti YOUR_SERVER_IP dengan IP server Anda
http://YOUR_SERVER_IP/
http://YOUR_SERVER_IP/dashboard
http://YOUR_SERVER_IP/health
```

---

## 🔧 Management Commands

### Start/Stop/Restart

```bash
# Start
systemctl start distributed-flask

# Stop
systemctl stop distributed-flask

# Restart
systemctl restart distributed-flask

# Status
systemctl status distributed-flask
```

### View Logs

```bash
# Real-time logs
journalctl -u distributed-flask -f

# Last 100 lines
journalctl -u distributed-flask -n 100

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Update Code

```bash
# Pull latest changes
cd /var/www/sam
git pull origin main

# Update dependencies (jika ada perubahan)
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Restart service
systemctl restart distributed-flask
```

---

## 🔐 Security & Production Tips

### 1. Setup Firewall (UFW)

```bash
# Install UFW
apt-get install ufw

# Allow SSH (PENTING! Jangan sampai terkunci)
ufw allow 22/tcp

# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS (jika pakai SSL)
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### 2. Setup SSL dengan Let's Encrypt (Optional)

```bash
# Install Certbot
apt-get install certbot python3-certbot-nginx

# Get certificate (ganti yourdomain.com)
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (sudah otomatis)
certbot renew --dry-run
```

### 3. Monitoring dengan PM2 (Alternative)

```bash
# Install PM2
npm install -g pm2

# Start app dengan PM2
cd /var/www/sam
pm2 start "venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5001 app:app" --name distributed-flask

# Auto-start on reboot
pm2 startup
pm2 save

# Monitor
pm2 monit
```

### 4. Setup Monitoring & Alerts

```bash
# Install htop untuk monitoring
apt-get install htop

# Check resource usage
htop

# Check disk space
df -h

# Check memory
free -m
```

---

## 🔧 Environment Variables

Edit di service file:

```bash
nano /etc/systemd/system/distributed-flask.service
```

Tambahkan environment variables:

```ini
Environment="CONSISTENCY_MODE=strong"
Environment="REPLICATION_DELAY=5"
Environment="QUORUM_SIZE=2"
Environment="SIMULATE_FAILURES=false"
```

Lalu restart:

```bash
systemctl daemon-reload
systemctl restart distributed-flask
```

---

## 🐛 Troubleshooting

### Service tidak start

```bash
# Check detailed logs
journalctl -u distributed-flask -n 50 --no-pager

# Check Python errors
source venv/bin/activate
python app.py
```

### Port sudah digunakan

```bash
# Check apa yang pakai port 5001
lsof -i :5001

# Kill process
kill -9 <PID>
```

### Permission denied

```bash
# Fix permissions
chown -R www-data:www-data /var/www/sam
chmod -R 755 /var/www/sam
```

### Nginx tidak bisa connect ke app

```bash
# Check app running
systemctl status distributed-flask

# Check Nginx config
nginx -t

# Restart both
systemctl restart distributed-flask
systemctl restart nginx
```

### Out of memory

```bash
# Check memory
free -m

# Reduce Gunicorn workers di service file
# Ganti --workers 3 jadi --workers 2
nano /etc/systemd/system/distributed-flask.service

systemctl daemon-reload
systemctl restart distributed-flask
```

---

## 📊 Performance Tuning

### Optimize Gunicorn Workers

```bash
# Formula: (2 x CPU cores) + 1
# Check CPU cores:
nproc

# Update workers di service file
nano /etc/systemd/system/distributed-flask.service

# Ganti --workers 3 dengan jumlah optimal
```

### Enable Gzip di Nginx

Edit nginx config:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

---

## 📝 Checklist Deployment

- [ ] Script deploy.sh berhasil dijalankan
- [ ] Service distributed-flask running
- [ ] Nginx running dan configured
- [ ] Firewall configured (UFW)
- [ ] Test API endpoints dari browser
- [ ] Dashboard dapat diakses
- [ ] Logs tidak ada error
- [ ] Auto-start enabled
- [ ] (Optional) SSL certificate installed
- [ ] (Optional) Monitoring setup

---

## 🎓 Quick Reference

```bash
# Status check
systemctl status distributed-flask nginx

# Logs
journalctl -u distributed-flask -f

# Restart
systemctl restart distributed-flask

# Update code
cd /var/www/sam && git pull && systemctl restart distributed-flask

# Access
http://YOUR_SERVER_IP/dashboard
```

---

**Selamat! Aplikasi Anda sudah production-ready! 🎉**

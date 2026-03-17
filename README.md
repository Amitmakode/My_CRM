# 🗂️ My CRM

A Django-based Customer Relationship Management system to manage contacts, leads, and sales pipelines.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Framework-Django-green)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Local Setup](#local-setup)
- [Development to Production](#development-to-production)
- [Production Deployment (AWS EC2)](#production-deployment-aws-ec2)
- [Common Errors & Fixes](#common-errors--fixes)
- [Contact](#contact)

---

## ✨ Features

- Contact & lead management
- Sales pipeline tracking
- Admin dashboard
- Secure user authentication

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, Django |
| Server | Gunicorn + Nginx |
| Database | PostgreSQL |
| Hosting | AWS EC2 |

---

## 💻 Local Setup

```bash
git clone https://github.com/Amitmakode/My_CRM.git
cd My_CRM
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

---

## 🔄 Development to Production

Before deploying to production, follow these steps carefully.

### 1. Update settings.py

Open `crm/settings.py` and change the following:

```python
# ❌ Development (change this)
DEBUG = True
ALLOWED_HOSTS = []

# ✅ Production (to this)
DEBUG = False
ALLOWED_HOSTS = ['YOUR_EC2_PUBLIC_IP']
```

### 2. Add Security Settings

In the same `settings.py` file, add these lines:

```python
# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
```

### 3. Add Whitenoise for Static Files

Install whitenoise:

```bash
pip install whitenoise
```

In `settings.py`, add whitenoise to `MIDDLEWARE`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← add this line
    ...
]
```

Also add at the bottom of `settings.py`:

```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 4. Collect Static Files

```bash
python manage.py collectstatic
```

### 5. Update requirements.txt

Make sure these are in your `requirements.txt`:

```
gunicorn
whitenoise
```

To update it run:

```bash
pip freeze > requirements.txt
```

### 6. Restart Gunicorn

After all changes, restart Gunicorn:

```bash
sudo systemctl restart gunicorn
```

---

## 🚀 Production Deployment (AWS EC2)

### 1. Security Group — Open these ports

| Port | Purpose |
|------|---------|
| 22 | SSH |
| 80 | HTTP (Nginx) |
| 8000 | Django / Gunicorn (testing) |
| 5432 | PostgreSQL |

---

### 2. Install Python 3.11

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential libssl-dev libffi-dev zlib1g-dev wget

cd /usr/src
sudo wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
sudo tar xzf Python-3.11.9.tgz
cd Python-3.11.9
sudo ./configure --enable-optimizations
sudo make altinstall

python3.11 --version   # verify
```

---

### 3. Clone & Setup Project

```bash
git clone https://github.com/Amitmakode/My_CRM.git
cd My_CRM
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

---

### 4. Configure Gunicorn

Create the service file:

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Paste:

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/My_CRM
UMask=007
ExecStart=/root/My_CRM/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/root/My_CRM/gunicorn.sock \
          crm.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable & start:

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn   # should show active (running)
```

---

### 5. Configure Nginx

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/mycrm
```

Paste:

```nginx
server {
    listen 80;
    server_name YOUR_EC2_PUBLIC_IP;

    location /static/ {
        root /root/My_CRM;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/root/My_CRM/gunicorn.sock;
    }
}
```

Enable & restart:

```bash
sudo ln -s /etc/nginx/sites-available/mycrm /etc/nginx/sites-enabled
sudo nginx -t        # should show: syntax is ok
sudo systemctl restart nginx
```

---

### 6. Update Django ALLOWED_HOSTS

```bash
nano crm/settings.py
```

```python
ALLOWED_HOSTS = ['YOUR_EC2_PUBLIC_IP']
```

Restart Gunicorn:

```bash
sudo systemctl restart gunicorn
```

Visit: `http://YOUR_EC2_PUBLIC_IP`

---

## 🔧 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `502 Bad Gateway` | Gunicorn not running or socket missing | `sudo systemctl restart gunicorn` |
| `400 Bad Request` | IP not in `ALLOWED_HOSTS` | Add your IP to `ALLOWED_HOSTS` in `settings.py` |
| Socket permission denied | `/root` not accessible by Nginx | `sudo chmod 755 /root && sudo chmod -R 755 /root/My_CRM` |
| Static files not loading | `collectstatic` not run | Run `python manage.py collectstatic` |

**Useful debug commands:**

```bash
sudo systemctl status gunicorn
journalctl -u gunicorn -n 50 --no-pager
sudo tail -50 /var/log/nginx/error.log
curl --unix-socket /root/My_CRM/gunicorn.sock localhost
```

---

## 📬 Contact

**Amit Makode** — [@Amitmakode](https://github.com/Amitmakode)

> ⭐ Star this repo if you found it helpful!
















# 🚀 Panduan Deploy Gratis - Distributed Flask App

## 🌟 Platform Gratis Terbaik (2026)

| Platform | Free Tier | Kelebihan | Kemudahan |
|----------|-----------|-----------|-----------|
| **Railway.app** | $5 credit/bulan | Paling mudah, auto-deploy dari Git | ⭐⭐⭐⭐⭐ |
| **Render.com** | 750 jam/bulan | Reliable, dokumentasi bagus | ⭐⭐⭐⭐⭐ |
| **Fly.io** | 3 VMs gratis | Performance bagus, global deployment | ⭐⭐⭐⭐ |
| **PythonAnywhere** | 1 app gratis | Khusus Python, mudah setup | ⭐⭐⭐⭐ |

---

## 🎯 REKOMENDASI: Railway.app (PALING MUDAH!)

### ✅ Kenapa Railway?
- ✨ Deploy dalam 2 menit
- 🔄 Auto-deploy dari GitHub
- 💰 $5 credit gratis/bulan (cukup untuk app kecil)
- 📊 Dashboard monitoring built-in
- 🌐 Free custom domain

### 📋 Langkah Deploy ke Railway

#### 1. Persiapan
```bash
# Pastikan Git sudah initialized
git init
git add .
git commit -m "Initial commit"
```

#### 2. Push ke GitHub
```bash
# Buat repo baru di GitHub, lalu:
git remote add origin https://github.com/username/repo-name.git
git branch -M main
git push -u origin main
```

#### 3. Deploy ke Railway
1. Buka https://railway.app
2. Klik **"Start a New Project"**
3. Login dengan GitHub
4. Pilih **"Deploy from GitHub repo"**
5. Pilih repository Anda
6. Railway otomatis detect Python dan deploy! ✅

#### 4. Set Environment Variables (Opsional)
- Buka project di Railway dashboard
- Klik tab **"Variables"**
- Tambahkan:
  ```
  CONSISTENCY_MODE=eventual
  REPLICATION_DELAY=3
  QUORUM_SIZE=2
  ```

#### 5. Akses App
- Railway akan generate URL otomatis: `https://your-app.railway.app`
- Dashboard: `https://your-app.railway.app/dashboard`

---

## 🎨 Opsi 2: Render.com

### Langkah Deploy ke Render

#### 1. Push ke GitHub (sama seperti Railway)

#### 2. Deploy
1. Buka https://render.com
2. Klik **"New +"** → **"Web Service"**
3. Connect GitHub repository
4. Konfigurasi:
   - **Name**: distributed-flask-app
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
5. Klik **"Create Web Service"**

#### 3. Environment Variables
- Scroll ke **"Environment"** section
- Add environment variables seperti di Railway

#### 4. Deploy
- Render otomatis build dan deploy
- URL: `https://your-app.onrender.com`

⚠️ **Catatan**: Free tier Render akan sleep setelah 15 menit tidak ada traffic. First request setelah sleep butuh ~30 detik untuk wake up.

---

## ✈️ Opsi 3: Fly.io (Advanced)

### Langkah Deploy ke Fly.io

#### 1. Install Fly CLI
```bash
# macOS
brew install flyctl

# Atau download dari https://fly.io/docs/hands-on/install-flyctl/
```

#### 2. Login
```bash
flyctl auth login
```

#### 3. Launch App
```bash
# Di direktori project
flyctl launch

# Ikuti prompts:
# - App name: distributed-flask-app (atau custom)
# - Region: Singapore atau terdekat
# - PostgreSQL: No
# - Redis: No
```

#### 4. Deploy
```bash
flyctl deploy
```

#### 5. Set Environment Variables
```bash
flyctl secrets set CONSISTENCY_MODE=eventual
flyctl secrets set REPLICATION_DELAY=3
flyctl secrets set QUORUM_SIZE=2
```

#### 6. Akses App
```bash
flyctl open
# Atau: https://your-app.fly.dev
```

---

## 🐍 Opsi 4: PythonAnywhere (Khusus Python)

### Langkah Deploy ke PythonAnywhere

#### 1. Buat Akun
- Daftar di https://www.pythonanywhere.com
- Pilih **"Beginner Account"** (gratis)

#### 2. Upload File
**Cara 1: Via Git**
```bash
# Di PythonAnywhere Bash console
git clone https://github.com/username/repo-name.git
cd repo-name
```

**Cara 2: Upload Manual**
- Gunakan "Files" tab
- Upload semua file project

#### 3. Setup Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.11 myenv
pip install -r requirements.txt
```

#### 4. Configure Web App
1. Klik tab **"Web"**
2. **"Add a new web app"**
3. Pilih **"Manual configuration"** → Python 3.11
4. Set:
   - **Source code**: `/home/username/repo-name`
   - **Working directory**: `/home/username/repo-name`
   - **WSGI file**: Edit sesuai instruksi

#### 5. Edit WSGI Configuration
```python
import sys
path = '/home/username/repo-name'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

#### 6. Reload Web App
- Klik **"Reload"**
- Akses: `https://username.pythonanywhere.com`

---

## 📝 File-file yang Sudah Disiapkan

✅ **Procfile** - Untuk Railway/Render
✅ **runtime.txt** - Python version specification
✅ **Dockerfile** - Untuk Fly.io atau container deployment
✅ **.dockerignore** - Ignore files saat build Docker
✅ **railway.toml** - Railway configuration
✅ **render.yaml** - Render configuration (Blueprint)

---

## 🔧 Modifikasi untuk Production

### Update app.py untuk Production
Tambahkan di bagian bawah `app.py`:

```python
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
```

### Tambahkan Gunicorn (Production Server)
Update `requirements.txt`:
```
flask
flask-cors
gunicorn
```

Update `Procfile`:
```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

---

## 🎯 Perbandingan Cepat

### Untuk Demo/Presentasi: **Railway.app** ⭐
- Paling cepat dan mudah
- Auto-deploy dari Git
- Free custom domain

### Untuk Long-term Project: **Render.com** ⭐
- Lebih stabil untuk free tier
- 750 jam/bulan cukup generous
- Dokumentasi lengkap

### Untuk Belajar DevOps: **Fly.io** ⭐
- Control lebih banyak
- Multi-region deployment
- Docker-based (skill tambahan)

### Untuk Simplicity: **PythonAnywhere** ⭐
- Tidak perlu Docker/Git
- Upload langsung via web
- Cocok untuk pemula

---

## 🧪 Testing Setelah Deploy

```bash
# Test API endpoint
curl https://your-app.railway.app/

# Test write
curl -X POST https://your-app.railway.app/write \
  -H "Content-Type: application/json" \
  -d '{"value": 100}'

# Test read
curl https://your-app.railway.app/read/node1

# Akses dashboard
# Buka: https://your-app.railway.app/dashboard
```

---

## ⚠️ Troubleshooting

### App tidak mau start
- Check logs di platform dashboard
- Pastikan `requirements.txt` lengkap
- Verify Python version di `runtime.txt`

### Port binding error
- Pastikan app.py menggunakan `PORT` environment variable
- Free tier biasanya assign port otomatis

### CORS error di dashboard
- Pastikan `flask-cors` terinstall
- Check `CORS(app)` di app.py

### Aplikasi sleep/lambat
- Normal di free tier (Render)
- Upgrade ke paid tier untuk always-on
- Atau gunakan uptime monitoring (UptimeRobot)

---

## 🎓 Tips Presentasi

1. **Live Demo dari URL Deploy**
   - Lebih impressive daripada localhost
   - Bisa diakses oleh dosen/penguji langsung

2. **Screenshot Deployment Process**
   - Ambil screenshot saat deploy
   - Tunjukkan logs dan metrics

3. **Custom Domain (Opsional)**
   - Railway/Render support custom domain gratis
   - Lebih profesional: `distributed-system.yourdomain.com`

4. **Monitoring Dashboard**
   - Tunjukkan Railway/Render dashboard
   - Metrics, logs, deployment history

---

## 📌 Checklist Deploy

- [ ] Push code ke GitHub
- [ ] Pilih platform (Railway recommended)
- [ ] Deploy dan verify URL works
- [ ] Test semua endpoint
- [ ] Set environment variables
- [ ] Test dashboard di browser
- [ ] Bookmark URL untuk presentasi
- [ ] Take screenshots untuk dokumentasi

---

**Selamat Deploy! 🚀**

Rekomendasi: Mulai dengan **Railway.app** karena paling mudah dan cepat!

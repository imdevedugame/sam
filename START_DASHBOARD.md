# 🌐 Web Dashboard - Cara Penggunaan

## 📋 Persiapan

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan Flask Server
```bash
python app.py
```

Server akan berjalan di `http://localhost:5001`

## 🚀 Akses Dashboard

### Buka salah satu URL berikut di browser:

1. **Langsung buka file HTML:**
   - Klik kanan pada `dashboard.html` → Open with → Browser

2. **Atau via Flask server:**
   ```
   http://localhost:5001/dashboard
   ```

## 🎯 Fitur Dashboard

### ✍️ Write Operations
- Masukkan nilai yang ingin ditulis
- Klik tombol **Write** untuk menulis data
- Sistem akan menulis sesuai consistency mode yang dipilih

### 📖 Read Operations  
- Pilih node yang ingin dibaca (node1/node2/node3)
- **Read** - pembacaan biasa dari node yang dipilih
- **Quorum Read** - pembacaan dengan read repair otomatis

### 🖥️ Nodes Status
- Menampilkan status real-time dari semua nodes
- Menunjukkan value, vector clock, dan timestamp tiap node
- Tombol **Toggle Status** untuk simulasi node failure

### 📊 Metrics
- Total writes/reads
- Conflicts resolved
- Read repairs
- Average latency
- Success rate

### 📝 Activity Log
- Log aktivitas real-time
- Menampilkan hasil operasi write/read
- Auto-scroll untuk log terbaru

### ⚙️ System Controls
- **Reset System** - reset semua nodes dan metrics
- **Refresh All** - refresh manual semua data
- **Auto-refresh** - otomatis refresh setiap 3 detik

## 🧪 Testing dengan Dashboard

### Test 1: Strong Consistency
```bash
# Jalankan dengan strong consistency
CONSISTENCY_MODE=strong python app.py
```
1. Buka dashboard
2. Write nilai (misal: 100)
3. Lihat semua node ter-update sekaligus
4. Read dari node manapun hasilnya sama

### Test 2: Eventual Consistency
```bash
CONSISTENCY_MODE=eventual python app.py
```
1. Write nilai (misal: 200)
2. Langsung read dari node2/node3
3. Tunggu beberapa detik (delay replikasi)
4. Read lagi, nilai sudah tersinkronisasi

### Test 3: Node Failure
1. Toggle status node2 menjadi unhealthy
2. Write nilai baru
3. Lihat sistem tetap berjalan (quorum masih terpenuhi)
4. Toggle kembali node2 menjadi healthy

### Test 4: Read Repair
1. Set CONSISTENCY_MODE=eventual
2. Write nilai, tungil replikasi
3. Toggle node2 jadi unhealthy saat replikasi
4. Gunakan **Quorum Read** - sistem akan repair node yang stale

## 🎨 Tampilan Dashboard

- **Modern UI** dengan gradient background
- **Real-time updates** setiap 3 detik
- **Color-coded status** (hijau = healthy, merah = unhealthy)
- **Responsive metrics** dan visualisasi
- **Activity log** untuk tracking operasi

## 📸 Screenshot untuk Laporan

Ambil screenshot dari:
1. Dashboard dengan semua nodes healthy
2. Hasil write operation dengan latency
3. Metrics menunjukkan conflicts resolved
4. Node failure simulation
5. Read repair dalam action

## ⚠️ Troubleshooting

### Dashboard tidak bisa connect ke API
- Pastikan Flask server berjalan di port 5001
- Check console browser untuk error CORS
- Pastikan `flask-cors` sudah terinstall

### Auto-refresh tidak berjalan
- Refresh halaman browser
- Check console untuk JavaScript errors

### Metrics tidak update
- Klik tombol **Refresh All**
- Restart Flask server
- Clear browser cache

## 🎓 Untuk Presentasi/Demo

1. **Preparation:**
   - Jalankan server dengan consistency mode yang ingin ditunjukkan
   - Buka dashboard di browser
   - Reset system untuk starting fresh

2. **Demo Flow:**
   - Jelaskan consistency mode yang aktif
   - Demo write operation → tunjukkan latency
   - Demo read dari berbagai node
   - Toggle node status untuk simulasi failure
   - Tunjukkan metrics dan success rate

3. **Highlight Features:**
   - Vector clocks untuk conflict detection
   - Read repair mechanism
   - Quorum-based writes
   - Real-time monitoring

## 📌 Tips

- Gunakan 2 browser window: 1 untuk dashboard, 1 untuk Postman/API testing
- Test dengan berbagai consistency modes untuk melihat perbedaan
- Perhatikan latency differences antara strong vs eventual
- Dokumentasikan hasil testing dengan screenshots

---

**Good luck dengan presentasi! 🚀**

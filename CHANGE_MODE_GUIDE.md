# 🔄 Cara Ganti Consistency Mode

## 📋 Ada 2 Cara:

---

## 🎨 Cara 1: Via Dashboard (PALING MUDAH!)

### Langkah-langkah:

1. **Buka Dashboard**
   ```
   http://localhost:5001/dashboard
   ```

2. **Klik Tombol "Change Mode"** di header (di samping consistency mode badge)

3. **Pilih Mode yang Diinginkan:**
   - ⚡ **STRONG** - Quorum-based writes (2/3 nodes), konsistensi tertinggi
   - 🔄 **EVENTUAL** - Async replication, performa seimbang
   - ⚡ **WEAK** - Primary only, tercepat

4. **Mode Langsung Berubah!** ✅
   - Tidak perlu restart server
   - Langsung aktif untuk write berikutnya

### Screenshot:
```
┌─────────────────────────────────────┐
│ Consistency Mode: EVENTUAL          │
│              [Change Mode] <----- KLIK INI
└─────────────────────────────────────┘

Modal muncul:
┌─────────────────────────────────────┐
│ 🔄 Change Consistency Mode          │
│                                     │
│ ⚡ STRONG Consistency               │
│   Quorum-based writes...            │
│                                     │
│ 🔄 EVENTUAL Consistency <-- KLIK   │
│   Async replication...              │
│                                     │
│ ⚡ WEAK Consistency                 │
│   Primary node only...              │
│                                     │
│              [Cancel]               │
└─────────────────────────────────────┘
```

---

## 🔧 Cara 2: Via API (Manual Testing)

### GET - Cek Mode Saat Ini

```bash
curl http://localhost:5001/config/consistency
```

Response:
```json
{
  "consistency_mode": "eventual",
  "available_modes": ["strong", "weak", "eventual"],
  "config": {
    "quorum_size": 2,
    "replication_delay_sec": 3
  }
}
```

### POST - Ganti Mode

```bash
# Ganti ke STRONG
curl -X POST http://localhost:5001/config/consistency \
  -H "Content-Type: application/json" \
  -d '{"mode": "strong"}'

# Ganti ke EVENTUAL
curl -X POST http://localhost:5001/config/consistency \
  -H "Content-Type: application/json" \
  -d '{"mode": "eventual"}'

# Ganti ke WEAK
curl -X POST http://localhost:5001/config/consistency \
  -H "Content-Type: application/json" \
  -d '{"mode": "weak"}'
```

Response:
```json
{
  "success": true,
  "previous_mode": "eventual",
  "current_mode": "strong",
  "message": "Consistency mode changed to STRONG"
}
```

---

## 🧪 Testing Perbedaan Mode

### Test 1: STRONG Consistency

```bash
# 1. Set mode ke strong (via dashboard atau API)
curl -X POST http://localhost:5001/config/consistency \
  -d '{"mode": "strong"}'

# 2. Write value
curl -X POST http://localhost:5001/write \
  -H "Content-Type: application/json" \
  -d '{"value": 100}'

# 3. Langsung read dari semua node - hasilnya sama!
curl http://localhost:5001/read/node1
curl http://localhost:5001/read/node2
curl http://localhost:5001/read/node3
```

**Expected:** Semua node langsung punya value 100 (quorum write)

### Test 2: EVENTUAL Consistency

```bash
# 1. Set mode ke eventual
curl -X POST http://localhost:5001/config/consistency \
  -d '{"mode": "eventual"}'

# 2. Write value
curl -X POST http://localhost:5001/write \
  -H "Content-Type: application/json" \
  -d '{"value": 200}'

# 3. Langsung read - node2/node3 mungkin masih value lama
curl http://localhost:5001/read/node1  # 200 (langsung)
curl http://localhost:5001/read/node2  # masih 100 (belum tereplikasi)

# 4. Tunggu 3 detik, read lagi
sleep 3
curl http://localhost:5001/read/node2  # sekarang 200 (sudah tereplikasi)
```

**Expected:** Node primary update langsung, replicas delay 3 detik

### Test 3: WEAK Consistency

```bash
# 1. Set mode ke weak
curl -X POST http://localhost:5001/config/consistency \
  -d '{"mode": "weak"}'

# 2. Write value
curl -X POST http://localhost:5001/write \
  -H "Content-Type: application/json" \
  -d '{"value": 300}'

# 3. Read - hanya node1 yang update
curl http://localhost:5001/read/node1  # 300
curl http://localhost:5001/read/node2  # masih value lama
curl http://localhost:5001/read/node3  # masih value lama
```

**Expected:** Hanya primary (node1) yang update, tidak ada replikasi

---

## 📊 Perbandingan Mode

| Mode | Write Latency | Read Consistency | Use Case |
|------|--------------|------------------|----------|
| **STRONG** | Tinggi (~10-50ms) | 100% konsisten | Banking, critical data |
| **EVENTUAL** | Sedang (~5-20ms) | Eventually consistent | Social media, caching |
| **WEAK** | Rendah (~2-10ms) | Tidak konsisten | Logging, analytics |

---

## 🎯 Tips Presentasi/Demo

### Skenario Demo yang Impressive:

1. **Start dengan EVENTUAL**
   - Show di dashboard: mode badge berwarna biru
   - Write value 100
   - Tunjukkan delay replikasi di nodes

2. **Switch ke STRONG**
   - Klik "Change Mode" → pilih STRONG
   - Badge berubah hijau
   - Write value 200
   - Tunjukkan semua nodes langsung sync!

3. **Switch ke WEAK**
   - Klik "Change Mode" → pilih WEAK
   - Badge berubah kuning
   - Write value 300
   - Tunjukkan hanya node1 yang update

4. **Tunjukkan Metrics**
   - Compare latency antar mode
   - Show conflicts resolved (eventual mode)

### Visual di Dashboard:

- **Mode badge berubah warna** otomatis:
  - 🟢 STRONG = Hijau
  - 🔵 EVENTUAL = Biru
  - 🟡 WEAK = Kuning

- **Activity log** mencatat perubahan mode
- **Metrics** menunjukkan perbedaan latency

---

## ⚠️ Important Notes

### Runtime vs Environment Variable

- **Dashboard/API:** Ganti mode saat runtime (tidak perlu restart)
- **Server Restart:** Mode kembali ke default dari environment variable
- **Production:** Set env var untuk default mode saat start

### Untuk Production/Server:

Set default mode di environment variable:

```bash
# Strong consistency
export CONSISTENCY_MODE=strong
python app.py

# Atau di systemd service file:
Environment="CONSISTENCY_MODE=strong"
```

Tapi tetap bisa diganti via dashboard saat runtime!

---

## 🐛 Troubleshooting

### Mode tidak berubah di dashboard
- Refresh page (F5)
- Check activity log untuk error
- Check server logs: `journalctl -u distributed-flask -f`

### API error saat ganti mode
- Pastikan server running
- Check mode valid: strong/weak/eventual (lowercase)
- Check CORS jika dari browser lain

---

**Sekarang coba ganti mode via dashboard! 🚀**

Buka: http://localhost:5001/dashboard
Klik: **Change Mode** → Pilih mode → Done! ✅

# 📋 Panduan Testing Distributed Flask App

## Prasyarat

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Jalankan server:
```bash
# Gunakan port 5001 jika port 5000 terpakai
python3 app.py
# atau dengan custom port:
python3 -c "from app import app; app.run(host='0.0.0.0', port=5001)"
```

---

## 🎯 Metode Testing

### **Metode 1: Manual dengan cURL**

#### 1. Cek Info Aplikasi
```bash
curl http://localhost:5001/
```

#### 2. Health Check
```bash
curl http://localhost:5001/health
```

#### 3. Lihat Status Semua Node
```bash
curl http://localhost:5001/nodes
```

#### 4. Write Data
```bash
curl -X POST http://localhost:5001/write \
  -H "Content-Type: application/json" \
  -d '{"value": 100}'
```

#### 5. Read dari Node Tertentu
```bash
# Read biasa
curl http://localhost:5001/read/node1

# Quorum read (dengan read repair)
curl "http://localhost:5001/read/node1?quorum=true"
```

#### 6. Toggle Status Node (Simulasi Failure)
```bash
# Matikan node
curl -X POST http://localhost:5001/node/node2/status

# Hidupkan kembali (toggle lagi)
curl -X POST http://localhost:5001/node/node2/status
```

#### 7. Lihat Metrics
```bash
curl http://localhost:5001/metrics
```

#### 8. Reset Semua Node
```bash
curl -X POST http://localhost:5001/reset
```

---

### **Metode 2: Automated Testing dengan Bash Script**

Jalankan script testing otomatis:

```bash
chmod +x test_app.sh
./test_app.sh
```

Script ini akan:
- Test semua endpoint secara berurutan
- Simulasi node failure
- Verifikasi consistency
- Cek metrics
- Reset system

---

### **Metode 3: Python Test Script**

Jalankan test suite Python yang lebih comprehensive:

```bash
chmod +x test_consistency.py
python3 test_consistency.py
```

Test suite ini mencakup:
- ✅ Basic operations
- ✅ Strong consistency testing
- ✅ Node failure scenarios
- ✅ Quorum read & read repair
- ✅ Concurrent writes

---

## 🧪 Skenario Testing

### Skenario 1: Test Strong Consistency
```bash
# 1. Set mode ke strong (default)
export CONSISTENCY_MODE=strong

# 2. Jalankan server
python3 app.py

# 3. Write data
curl -X POST http://localhost:5001/write \
  -H "Content-Type: application/json" \
  -d '{"value": 100}'

# 4. Cek semua node - harus sama
curl http://localhost:5001/nodes
```

**Expected:** Semua node memiliki nilai yang sama (100)

---

### Skenario 2: Test Eventual Consistency
```bash
# 1. Set mode ke eventual
export CONSISTENCY_MODE=eventual
export REPLICATION_DELAY=3

# 2. Jalankan server
python3 -c "from app import app; app.run(host='0.0.0.0', port=5001)"

# 3. Write data
curl -X POST http://localhost:5001/write \
  -H "Content-Type: application/json" \
  -d '{"value": 200}'

# 4. Langsung cek node2 (sebelum replikasi selesai)
curl http://localhost:5001/read/node2

# 5. Tunggu 3 detik, cek lagi
sleep 3
curl http://localhost:5001/read/node2
```

**Expected:** 
- Awalnya node2 belum ter-update
- Setelah 3 detik, node2 sudah ter-replicate

---

### Skenario 3: Test Node Failure
```bash
# 1. Write data awal
curl -X POST http://localhost:5001/write \
  -H "Content-Type: application/json" \
  -d '{"value": 100}'

# 2. Matikan node2
curl -X POST http://localhost:5001/node/node2/status

# 3. Cek health
curl http://localhost:5001/health

# 4. Write data baru (dengan node2 down)
curl -X POST http://localhost:5001/write \
  -H "Content-Type: application/json" \
  -d '{"value": 200}'

# 5. Hidupkan kembali node2
curl -X POST http://localhost:5001/node/node2/status

# 6. Cek status nodes
curl http://localhost:5001/nodes
```

**Expected:** 
- Quorum masih terpenuhi (2 dari 3 node)
- Write tetap sukses
- Node2 kembali healthy setelah di-toggle

---

### Skenario 4: Test Quorum Read & Read Repair
```bash
# 1. Write data
curl -X POST http://localhost:5001/write \
  -H "Content-Type: application/json" \
  -d '{"value": 500}'

# 2. Quorum read (trigger read repair jika ada inconsistency)
curl "http://localhost:5001/read/node1?quorum=true"

# 3. Cek metrics untuk read_repairs
curl http://localhost:5001/metrics
```

---

### Skenario 5: Stress Test (Multiple Writes)
```bash
# Rapid fire writes
for i in {1..10}; do
  curl -X POST http://localhost:5001/write \
    -H "Content-Type: application/json" \
    -d "{\"value\": $((i * 100))}"
  echo ""
done

# Cek final state
curl http://localhost:5001/nodes

# Cek metrics
curl http://localhost:5001/metrics
```

---

## 📊 Apa yang Harus Dicek

### ✅ Checklist Testing

- [ ] **Health Check**: Semua node healthy di awal
- [ ] **Write Success**: Write berhasil dengan response sukses
- [ ] **Read Consistency**: Semua node punya nilai yang konsisten (strong mode)
- [ ] **Node Failure**: System tetap berjalan dengan quorum
- [ ] **Read Repair**: Read repair bekerja saat ada inconsistency
- [ ] **Metrics Tracking**: Metrics ter-record dengan benar
- [ ] **Reset Function**: Reset berhasil mengembalikan ke state awal
- [ ] **Vector Clock**: Vector clock terupdate dengan benar
- [ ] **Latency**: Latency tercatat di metrics

---

## 🔍 Monitoring Logs

Server Flask akan menampilkan log realtime:

```
2026-01-12 10:50:00 - INFO - Write successful to node1
2026-01-12 10:50:00 - INFO - Write successful to node2
2026-01-12 10:50:00 - INFO - Strong write completed: 2/2 nodes
2026-01-12 10:50:03 - INFO - Replicated to node2
2026-01-12 10:50:03 - INFO - Replicated to node3
```

Perhatikan:
- Write success/failure
- Replication events
- Conflict resolution
- Read repairs
- Node status changes

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Gunakan port lain
python3 -c "from app import app; app.run(host='0.0.0.0', port=5001)"
```

### Python Not Found
```bash
# Gunakan python3
python3 app.py
```

### Missing Dependencies
```bash
pip install flask
```

---

## 📈 Melihat Hasil Testing

Setelah testing, cek:

1. **Metrics Endpoint**
```bash
curl http://localhost:5001/metrics | python3 -m json.tool
```

2. **Final Node States**
```bash
curl http://localhost:5001/nodes | python3 -m json.tool
```

3. **Health Status**
```bash
curl http://localhost:5001/health | python3 -m json.tool
```

---

## 💡 Tips Testing

1. **Reset sebelum test baru**: `curl -X POST http://localhost:5001/reset`
2. **Gunakan `| python3 -m json.tool`** untuk format JSON yang rapi
3. **Monitor server logs** di terminal untuk debugging
4. **Test dengan berbagai mode consistency** (strong, weak, eventual)
5. **Simulasi berbagai failure scenario** untuk resilience testing

---

## 🎓 Latihan

Coba skenario berikut:

1. **Challenge 1**: Matikan 2 dari 3 node, apakah write masih bisa?
2. **Challenge 2**: Write 100 kali berturut-turut, cek consistency
3. **Challenge 3**: Toggle node status berulang kali saat write
4. **Challenge 4**: Bandingkan latency antara simple read vs quorum read

Selamat testing! 🚀

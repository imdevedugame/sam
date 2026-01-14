# 📦 Cara Import & Gunakan File JSON Testing

## 🎯 File JSON yang Tersedia

1. **postman_collection.json** - Collection lengkap untuk Postman
2. **insomnia_collection.json** - Collection untuk Insomnia REST Client
3. **sample_test_data.json** - Data testing dan skenario test

---

## 📥 Cara Import ke Postman

### Step-by-Step:

1. **Buka Postman** (download dari [postman.com](https://www.postman.com/downloads/))

2. **Import Collection**
   - Klik tombol **"Import"** di kiri atas
   - Pilih **"Upload Files"**
   - Pilih file `postman_collection.json`
   - Klik **"Import"**

3. **Set Environment**
   - Collection sudah include environment variable
   - Base URL default: `http://localhost:5001`
   - Bisa edit di **Variables** tab

4. **Mulai Testing**
   - Expand folder di collection
   - Pilih request yang mau ditest
   - Klik **"Send"**

### 🎬 Quick Start Postman:

```
1. Import → postman_collection.json
2. Folder "1. Info & Health" → "Get App Info" → Send
3. Folder "2. Write Operations" → "Write Value 100" → Send
4. Folder "3. Read Operations" → "Read from Node1" → Send
```

---

## 📥 Cara Import ke Insomnia

### Step-by-Step:

1. **Buka Insomnia** (download dari [insomnia.rest](https://insomnia.rest/download))

2. **Import Collection**
   - Klik **"Create"** → **"Import From"** → **"File"**
   - Pilih file `insomnia_collection.json`
   - Klik **"Import"**

3. **Set Base URL**
   - Base URL sudah diset ke `http://localhost:5001`
   - Bisa edit di Environment settings

4. **Mulai Testing**
   - Pilih request dari sidebar
   - Klik **"Send"**

---

## 🧪 Menggunakan Sample Test Data

File `sample_test_data.json` berisi:

### 1. Test Scenarios
```json
{
  "test_scenarios": {
    "basic_write_tests": [...],
    "error_cases": [...],
    "consistency_tests": [...],
    "load_tests": {...}
  }
}
```

### 2. Sample Values untuk Testing
```json
{
  "sample_values": {
    "integers": [1, 10, 100, 1000],
    "negative": [-1, -100, -1000],
    "edge_cases": [0, 2147483647]
  }
}
```

### Cara Pakai:
1. Buka `sample_test_data.json`
2. Copy value dari section yang dibutuhkan
3. Paste ke request body di Postman/Insomnia
4. Send request

---

## 🚀 Quick Testing Guide

### Test 1: Basic Operations
```
1. Send: GET /health
   Expected: Status 200, all nodes healthy

2. Send: POST /write dengan body {"value": 100}
   Expected: Status 200, success: true

3. Send: GET /read/node1
   Expected: Status 200, value: 100
```

### Test 2: Node Failure Scenario
```
1. POST /reset (reset system)
2. POST /write → {"value": 200}
3. POST /node/node2/status (disable node2)
4. GET /health (check status)
5. POST /write → {"value": 300} (write dengan node down)
6. POST /node/node2/status (enable node2 lagi)
7. GET /nodes (verify final state)
```

### Test 3: Consistency Check
```
1. POST /reset
2. POST /write → {"value": 500}
3. GET /read/node1
4. GET /read/node2
5. GET /read/node3
   Expected: Semua node return value 500
```

---

## 📊 Menggunakan Test Scenarios di Postman

Collection Postman sudah include folder **"6. Test Scenarios"** dengan:

1. **Strong Consistency Test**
   - Jalankan semua request berurutan
   - Verifikasi consistency di semua node

2. **Node Failure Test**
   - Simulasi node failure
   - Test recovery mechanism

### Cara Jalankan Scenario:

**Manual:**
```
Expand folder scenario → Run request satu per satu
```

**Otomatis dengan Collection Runner:**
```
1. Klik kanan pada folder scenario
2. Pilih "Run collection"
3. Klik "Run [nama folder]"
4. Lihat hasil test di summary
```

---

## 🔧 Customize Variables

### Di Postman:

1. Klik tab **"Variables"** di collection
2. Edit nilai:
   - `base_url`: Default `http://localhost:5001`
   - `custom_value`: Default `999`

3. Gunakan variable di request:
   ```
   URL: {{base_url}}/write
   Body: {"value": {{custom_value}}}
   ```

### Di Insomnia:

1. Klik **"Manage Environments"**
2. Edit **"Base Environment"**
3. Ubah `base_url` sesuai kebutuhan

---

## 📝 Tips Testing

### 1. Gunakan Tests di Postman

Tambahkan test script di tab **"Tests"**:

```javascript
// Test status code
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Test response body
pm.test("Write successful", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.success).to.eql(true);
});

// Test response time
pm.test("Response time < 200ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(200);
});
```

### 2. Chain Requests

Save response value untuk request berikutnya:

```javascript
// Di request pertama (Tests tab)
var jsonData = pm.response.json();
pm.environment.set("last_value", jsonData.written_value);

// Di request kedua, gunakan {{last_value}}
```

### 3. Collection Variables

Gunakan untuk data yang sering berubah:
```
{{base_url}}
{{custom_value}}
{{node_name}}
```

---

## 🎯 Skenario Testing Recommended

### Skenario 1: Happy Path
```
✅ Reset → Write → Read → Verify
```

### Skenario 2: Error Handling
```
✅ Write tanpa value (expect error 400)
✅ Read dari node invalid (expect error 404)
```

### Skenario 3: Consistency
```
✅ Write → Read all nodes → Verify same value
```

### Skenario 4: Failure & Recovery
```
✅ Disable node → Write → Enable → Verify
```

### Skenario 5: Performance
```
✅ Sequential writes (10x)
✅ Measure latency
✅ Check metrics
```

---

## 🐛 Troubleshooting

### Connection Refused
```
❌ Error: connect ECONNREFUSED
✅ Fix: Pastikan server running di port 5001
   → python3 -c "from app import app; app.run(host='0.0.0.0', port=5001)"
```

### Wrong Port
```
❌ Error: Port 5000 in use
✅ Fix: Update base_url ke port 5001
   → Edit variable: base_url = http://localhost:5001
```

### Invalid JSON
```
❌ Error: Unexpected token
✅ Fix: Cek format JSON di body
   → Must be: {"value": 100} bukan {value: 100}
```

---

## 📦 Export Results

### Di Postman:
```
1. Run Collection Runner
2. Setelah selesai → Click "Export Results"
3. Save sebagai JSON/CSV
```

### Di Insomnia:
```
1. Response → Click "Preview"
2. Copy → Save to file
```

---

## 🎓 Best Practices

1. **Always Reset Before Test**
   ```
   POST /reset sebelum mulai test baru
   ```

2. **Check Health First**
   ```
   GET /health untuk ensure all nodes ready
   ```

3. **Verify After Write**
   ```
   Setelah write, read untuk verify
   ```

4. **Use Metrics**
   ```
   GET /metrics untuk track performance
   ```

5. **Document Results**
   ```
   Save response, export collection runner results
   ```

---

## 🔗 Resources

- **Postman Documentation**: https://learning.postman.com/
- **Insomnia Documentation**: https://docs.insomnia.rest/
- **Flask Documentation**: https://flask.palletsprojects.com/

---

Selamat testing! 🚀

Jika ada masalah, cek [TESTING_GUIDE.md](TESTING_GUIDE.md) untuk panduan manual testing.

#!/bin/bash

# Script Testing untuk Distributed Flask App
# Port: 5001 (sesuaikan jika berbeda)

BASE_URL="http://localhost:5001"

echo "=========================================="
echo "TESTING DISTRIBUTED FLASK APP"
echo "=========================================="
echo ""

# 1. Test endpoint utama
echo "1. Testing endpoint utama (GET /)..."
curl -s "$BASE_URL/" | python3 -m json.tool
echo -e "\n"

# 2. Test health check
echo "2. Testing health check..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo -e "\n"

# 3. Test nodes status
echo "3. Testing nodes status..."
curl -s "$BASE_URL/nodes" | python3 -m json.tool
echo -e "\n"

# 4. Test WRITE dengan strong consistency
echo "4. Testing WRITE (Strong Consistency)..."
curl -s -X POST "$BASE_URL/write" \
  -H "Content-Type: application/json" \
  -d '{"value": 100}' | python3 -m json.tool
echo -e "\n"

# 5. Test READ dari berbagai node
echo "5. Testing READ dari node1..."
curl -s "$BASE_URL/read/node1" | python3 -m json.tool
echo -e "\n"

echo "6. Testing READ dari node2..."
curl -s "$BASE_URL/read/node2" | python3 -m json.tool
echo -e "\n"

echo "7. Testing READ dari node3..."
curl -s "$BASE_URL/read/node3" | python3 -m json.tool
echo -e "\n"

# 8. Test WRITE lagi dengan nilai berbeda
echo "8. Testing WRITE dengan nilai 250..."
curl -s -X POST "$BASE_URL/write" \
  -H "Content-Type: application/json" \
  -d '{"value": 250}' | python3 -m json.tool
echo -e "\n"

# 9. Test Quorum Read
echo "9. Testing QUORUM READ dari node1..."
curl -s "$BASE_URL/read/node1?quorum=true" | python3 -m json.tool
echo -e "\n"

# 10. Test matikan node (simulasi failure)
echo "10. Testing TOGGLE node2 status (matikan)..."
curl -s -X POST "$BASE_URL/node/node2/status" | python3 -m json.tool
echo -e "\n"

# 11. Test health setelah node down
echo "11. Testing health check setelah node2 down..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo -e "\n"

# 12. Test write setelah node down
echo "12. Testing WRITE setelah node2 down..."
curl -s -X POST "$BASE_URL/write" \
  -H "Content-Type: application/json" \
  -d '{"value": 300}' | python3 -m json.tool
echo -e "\n"

# 13. Test hidupkan kembali node
echo "13. Testing TOGGLE node2 status (hidupkan kembali)..."
curl -s -X POST "$BASE_URL/node/node2/status" | python3 -m json.tool
echo -e "\n"

# 14. Test metrics
echo "14. Testing METRICS..."
curl -s "$BASE_URL/metrics" | python3 -m json.tool
echo -e "\n"

# 15. Test reset
echo "15. Testing RESET semua node..."
curl -s -X POST "$BASE_URL/reset" | python3 -m json.tool
echo -e "\n"

# 16. Verifikasi reset
echo "16. Verifikasi nodes setelah reset..."
curl -s "$BASE_URL/nodes" | python3 -m json.tool
echo -e "\n"

echo "=========================================="
echo "TESTING SELESAI!"
echo "=========================================="

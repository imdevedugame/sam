#!/usr/bin/env python3
"""
Script Testing untuk berbagai mode consistency
"""

import requests
import time
import os
import subprocess
import signal
import sys

BASE_URL = "http://localhost:5001"

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_endpoint(method, endpoint, data=None, params=None):
    """Helper untuk testing endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_basic_operations():
    """Test operasi dasar"""
    print_header("TEST OPERASI DASAR")
    
    # 1. Info app
    test_endpoint("GET", "/")
    
    # 2. Health check
    test_endpoint("GET", "/health")
    
    # 3. Node status
    test_endpoint("GET", "/nodes")
    
    # 4. Write data
    test_endpoint("POST", "/write", {"value": 42})
    
    # 5. Read dari semua node
    for node in ["node1", "node2", "node3"]:
        test_endpoint("GET", f"/read/{node}")
    
    # 6. Metrics
    test_endpoint("GET", "/metrics")

def test_strong_consistency():
    """Test strong consistency mode"""
    print_header("TEST STRONG CONSISTENCY")
    
    # Reset dulu
    test_endpoint("POST", "/reset")
    time.sleep(1)
    
    print("\n>>> Write dengan strong consistency...")
    test_endpoint("POST", "/write", {"value": 100})
    
    time.sleep(0.5)
    
    print("\n>>> Cek semua node harus punya nilai sama...")
    nodes = test_endpoint("GET", "/nodes")
    if nodes:
        values = [nodes["nodes"][n]["value"] for n in nodes["nodes"]]
        print(f"Values: {values}")
        if len(set(values)) == 1:
            print("✓ Semua node konsisten!")
        else:
            print("✗ Inconsistency detected!")

def test_node_failure():
    """Test dengan node failure"""
    print_header("TEST NODE FAILURE")
    
    # Reset
    test_endpoint("POST", "/reset")
    time.sleep(1)
    
    # Write normal
    print("\n>>> Write dengan semua node sehat...")
    test_endpoint("POST", "/write", {"value": 200})
    
    # Matikan satu node
    print("\n>>> Matikan node2...")
    test_endpoint("POST", "/node/node2/status")
    
    # Check health
    test_endpoint("GET", "/health")
    
    # Write dengan node down
    print("\n>>> Write dengan node2 down...")
    test_endpoint("POST", "/write", {"value": 300})
    
    # Hidupkan kembali
    print("\n>>> Hidupkan kembali node2...")
    test_endpoint("POST", "/node/node2/status")
    
    # Check final state
    time.sleep(1)
    test_endpoint("GET", "/nodes")

def test_quorum_read():
    """Test quorum read dan read repair"""
    print_header("TEST QUORUM READ & READ REPAIR")
    
    # Reset
    test_endpoint("POST", "/reset")
    time.sleep(1)
    
    # Write data
    print("\n>>> Write data awal...")
    test_endpoint("POST", "/write", {"value": 500})
    
    time.sleep(1)
    
    # Normal read
    print("\n>>> Normal read dari node1...")
    test_endpoint("GET", "/read/node1")
    
    # Quorum read
    print("\n>>> Quorum read dari node1...")
    test_endpoint("GET", "/read/node1", params={"quorum": "true"})
    
    # Check metrics untuk read repairs
    metrics = test_endpoint("GET", "/metrics")

def test_concurrent_writes():
    """Test concurrent writes"""
    print_header("TEST CONCURRENT WRITES")
    
    # Reset
    test_endpoint("POST", "/reset")
    time.sleep(1)
    
    print("\n>>> Melakukan 5 write berturut-turut...")
    for i in range(1, 6):
        result = test_endpoint("POST", "/write", {"value": i * 100})
        time.sleep(0.2)
    
    time.sleep(2)  # Tunggu replication
    
    # Check final state
    print("\n>>> Check final state semua node...")
    test_endpoint("GET", "/nodes")
    
    # Check metrics
    test_endpoint("GET", "/metrics")

def run_all_tests():
    """Jalankan semua test"""
    try:
        print("\n🚀 Memulai testing Distributed Flask App...")
        print(f"Base URL: {BASE_URL}")
        
        # Cek apakah server running
        try:
            requests.get(BASE_URL, timeout=2)
        except:
            print("\n❌ Server tidak berjalan!")
            print("Jalankan server dulu dengan: python3 app.py")
            return
        
        test_basic_operations()
        test_strong_consistency()
        test_node_failure()
        test_quorum_read()
        test_concurrent_writes()
        
        print_header("✅ SEMUA TEST SELESAI!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing dibatalkan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    run_all_tests()

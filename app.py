from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import time
import threading
import logging
from datetime import datetime
from collections import defaultdict
from threading import Lock
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for dashboard

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration (runtime-changeable)
class Config:
    CONSISTENCY_MODE = os.getenv("CONSISTENCY_MODE", "eventual")
    REPLICATION_DELAY = int(os.getenv("REPLICATION_DELAY", "3"))
    QUORUM_SIZE = int(os.getenv("QUORUM_SIZE", "2"))

config = Config()
CONSISTENCY_MODE = config.CONSISTENCY_MODE
REPLICATION_DELAY = config.REPLICATION_DELAY
QUORUM_SIZE = config.QUORUM_SIZE
SIMULATE_FAILURES = os.getenv("SIMULATE_FAILURES", "false").lower() == "true"
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.05"))  # 5% default

# Thread safety (RLock allows re-entrant locking)
node_lock = threading.RLock()
metrics_lock = threading.RLock()

# Enhanced node structure with versioning and timestamps
nodes = {
    "node1": {
        "value": 0, 
        "vector_clock": {"node1": 0, "node2": 0, "node3": 0},
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "last_heartbeat": time.time()
    },
    "node2": {
        "value": 0,
        "vector_clock": {"node1": 0, "node2": 0, "node3": 0},
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "last_heartbeat": time.time()
    },
    "node3": {
        "value": 0,
        "vector_clock": {"node1": 0, "node2": 0, "node3": 0},
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "last_heartbeat": time.time()
    }
}

# Metrics tracking
metrics = {
    "total_writes": 0,
    "total_reads": 0,
    "failed_writes": 0,
    "failed_reads": 0,
    "conflicts_resolved": 0,
    "read_repairs": 0,
    "write_latencies": [],
    "read_latencies": []
}

# Helper functions
def increment_vector_clock(node_name):
    """Increment vector clock for a specific node"""
    with node_lock:
        nodes[node_name]["vector_clock"][node_name] += 1

def compare_vector_clocks(vc1, vc2):
    """
    Compare two vector clocks
    Returns: 'before', 'after', 'concurrent', or 'equal'
    """
    vc1_keys = set(vc1.keys())
    vc2_keys = set(vc2.keys())
    all_keys = vc1_keys.union(vc2_keys)
    
    vc1_greater = False
    vc2_greater = False
    
    for key in all_keys:
        v1 = vc1.get(key, 0)
        v2 = vc2.get(key, 0)
        
        if v1 > v2:
            vc1_greater = True
        elif v2 > v1:
            vc2_greater = True
    
    if not vc1_greater and not vc2_greater:
        return 'equal'
    elif vc1_greater and not vc2_greater:
        return 'after'
    elif vc2_greater and not vc1_greater:
        return 'before'
    else:
        return 'concurrent'

def resolve_conflict(node_data_list):
    """
    Resolve conflicts using Last-Write-Wins (LWW) strategy
    """
    latest = max(node_data_list, key=lambda x: x['timestamp'])
    logger.info(f"Conflict resolved using LWW: {latest['value']}")
    with metrics_lock:
        metrics["conflicts_resolved"] += 1
    return latest

def simulate_node_failure():
    """Randomly simulate node failures for testing (disabled by default)"""
    if not SIMULATE_FAILURES:
        return False  # Simulation disabled
    if random.random() < FAILURE_RATE:
        return True
    return False

def get_healthy_nodes():
    """Get list of healthy nodes"""
    with node_lock:
        return [name for name, data in nodes.items() if data["status"] == "healthy"]

def record_latency(latency_list, latency):
    """Record latency metrics"""
    with metrics_lock:
        latency_list.append(latency)
        if len(latency_list) > 100:  # Keep last 100 measurements
            latency_list.pop(0)

def strong_write(value):
    """
    Strong consistency with quorum-based writes
    Writes to a quorum of nodes (default: 2 out of 3)
    """
    start_time = time.time()
    healthy_nodes = get_healthy_nodes()
    
    if len(healthy_nodes) < QUORUM_SIZE:
        logger.error(f"Not enough healthy nodes for quorum. Need {QUORUM_SIZE}, have {len(healthy_nodes)}")
        return False, f"Quorum not met: {len(healthy_nodes)}/{QUORUM_SIZE}"
    
    successful_writes = 0
    timestamp = datetime.now().isoformat()
    
    with node_lock:
        for node_name in healthy_nodes[:QUORUM_SIZE]:
            try:
                # Simulate occasional failures
                if not simulate_node_failure():
                    increment_vector_clock(node_name)
                    nodes[node_name]["value"] = value
                    nodes[node_name]["timestamp"] = timestamp
                    nodes[node_name]["last_heartbeat"] = time.time()
                    successful_writes += 1
                    logger.info(f"Write successful to {node_name}")
                else:
                    nodes[node_name]["status"] = "unhealthy"
                    logger.warning(f"Write failed to {node_name}")
            except Exception as e:
                logger.error(f"Error writing to {node_name}: {str(e)}")
    
    latency = time.time() - start_time
    record_latency(metrics["write_latencies"], latency)
    
    if successful_writes >= QUORUM_SIZE:
        logger.info(f"Strong write completed: {successful_writes}/{QUORUM_SIZE} nodes")
        return True, None
    else:
        return False, f"Write failed: {successful_writes}/{QUORUM_SIZE}"

def weak_write(value):
    """
    Weak consistency - writes to primary node only
    """
    start_time = time.time()
    timestamp = datetime.now().isoformat()
    
    with node_lock:
        try:
            increment_vector_clock("node1")
            nodes["node1"]["value"] = value
            nodes["node1"]["timestamp"] = timestamp
            nodes["node1"]["last_heartbeat"] = time.time()
            logger.info("Weak write to node1 successful")
            
            latency = time.time() - start_time
            record_latency(metrics["write_latencies"], latency)
            return True, None
        except Exception as e:
            logger.error(f"Weak write failed: {str(e)}")
            return False, str(e)

def eventual_write(value):
    """
    Eventual consistency with async replication and conflict detection
    """
    start_time = time.time()
    timestamp = datetime.now().isoformat()
    
    # Write to primary node first
    with node_lock:
        increment_vector_clock("node1")
        nodes["node1"]["value"] = value
        nodes["node1"]["timestamp"] = timestamp
        nodes["node1"]["last_heartbeat"] = time.time()
        primary_vector_clock = nodes["node1"]["vector_clock"].copy()
    
    latency = time.time() - start_time
    record_latency(metrics["write_latencies"], latency)
    logger.info(f"Eventual write to primary node1: {value}")

    def replicate():
        """Async replication with conflict detection"""
        time.sleep(REPLICATION_DELAY)
        
        with node_lock:
            for node_name in ["node2", "node3"]:
                try:
                    if nodes[node_name]["status"] == "healthy":
                        # Check for conflicts
                        comparison = compare_vector_clocks(
                            primary_vector_clock, 
                            nodes[node_name]["vector_clock"]
                        )
                        
                        if comparison == 'concurrent':
                            logger.warning(f"Conflict detected on {node_name}, resolving...")
                            # Use LWW for conflict resolution
                            if timestamp > nodes[node_name]["timestamp"]:
                                nodes[node_name]["value"] = value
                                nodes[node_name]["timestamp"] = timestamp
                                nodes[node_name]["vector_clock"] = primary_vector_clock.copy()
                        else:
                            nodes[node_name]["value"] = value
                            nodes[node_name]["timestamp"] = timestamp
                            nodes[node_name]["vector_clock"] = primary_vector_clock.copy()
                        
                        nodes[node_name]["last_heartbeat"] = time.time()
                        logger.info(f"Replicated to {node_name}")
                except Exception as e:
                    logger.error(f"Replication to {node_name} failed: {str(e)}")
                    nodes[node_name]["status"] = "unhealthy"

    threading.Thread(target=replicate, daemon=True).start()
    return True, None

def quorum_read(node_name):
    """
    Read with read repair mechanism
    """
    start_time = time.time()
    healthy_nodes = get_healthy_nodes()
    
    if len(healthy_nodes) < QUORUM_SIZE:
        logger.warning(f"Not enough healthy nodes for quorum read")
        return None
    
    # Read from quorum
    reads = []
    with node_lock:
        for name in healthy_nodes[:QUORUM_SIZE]:
            reads.append({
                'node': name,
                'value': nodes[name]["value"],
                'vector_clock': nodes[name]["vector_clock"].copy(),
                'timestamp': nodes[name]["timestamp"]
            })
    
    # Check for inconsistencies
    if len(set(r['value'] for r in reads)) > 1:
        logger.warning("Inconsistency detected during read, performing read repair")
        latest = resolve_conflict(reads)
        
        # Read repair - update stale replicas
        with node_lock:
            for name in healthy_nodes:
                if nodes[name]["value"] != latest["value"]:
                    nodes[name]["value"] = latest["value"]
                    nodes[name]["timestamp"] = latest["timestamp"]
                    nodes[name]["vector_clock"] = latest["vector_clock"].copy()
                    logger.info(f"Read repair performed on {name}")
                    with metrics_lock:
                        metrics["read_repairs"] += 1
    
    latency = time.time() - start_time
    record_latency(metrics["read_latencies"], latency)
    
    # Return value from requested node
    with node_lock:
        return nodes[node_name]["value"]


@app.route("/api/store", methods=["POST"])
def store_data():
    """Enhanced data storage endpoint with error handling and metrics"""
    start_time = time.time()
    
    try:
        data = request.json
        if not data or "value" not in data:
            return jsonify({"error": "Missing 'value' in request"}), 400
        
        value = data.get("value")
        
        with metrics_lock:
            metrics["total_writes"] += 1
        
        success = False
        error_msg = None
        
        if config.CONSISTENCY_MODE == "strong":
            success, error_msg = strong_write(value)
            mode = "STRONG CONSISTENCY (Quorum-based)"
        elif config.CONSISTENCY_MODE == "weak":
            success, error_msg = weak_write(value)
            mode = "WEAK CONSISTENCY (Primary only)"
        else:
            success, error_msg = eventual_write(value)
            mode = "EVENTUAL CONSISTENCY (Async replication)"
        
        if not success:
            with metrics_lock:
                metrics["failed_writes"] += 1
            return jsonify({
                "error": error_msg,
                "mode": mode
            }), 500
        
        # Get current node states
        with node_lock:
            nodes_snapshot = {
                name: {
                    "value": node_data["value"],
                    "vector_clock": node_data["vector_clock"],
                    "timestamp": node_data["timestamp"],
                    "status": node_data["status"]
                }
                for name, node_data in nodes.items()
            }
        
        return jsonify({
            "success": True,
            "mode": mode,
            "written_value": value,
            "nodes": nodes_snapshot,
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        })
        
    except Exception as e:
        logger.error(f"Write error: {str(e)}")
        with metrics_lock:
            metrics["failed_writes"] += 1
        return jsonify({"error": str(e)}), 500

@app.route("/api/retrieve/<node>", methods=["GET"])
def retrieve_data(node):
    """Enhanced data retrieval endpoint with quorum read option"""
    start_time = time.time()
    
    try:
        with metrics_lock:
            metrics["total_reads"] += 1
        
        if node not in nodes:
            return jsonify({"error": f"Node '{node}' not found"}), 404
        
        # Check if quorum read is requested
        use_quorum = request.args.get("quorum", "false").lower() == "true"
        
        if use_quorum:
            value = quorum_read(node)
            read_type = "quorum_read"
        else:
            with node_lock:
                value = nodes[node]["value"]
                vector_clock = nodes[node]["vector_clock"]
                timestamp = nodes[node]["timestamp"]
                status = nodes[node]["status"]
            read_type = "simple_read"
        
        latency = time.time() - start_time
        
        response = {
            "node": node,
            "value": value,
            "read_type": read_type,
            "latency_ms": round(latency * 1000, 2)
        }
        
        if not use_quorum:
            response.update({
                "vector_clock": vector_clock,
                "timestamp": timestamp,
                "status": status
            })
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Read error: {str(e)}")
        with metrics_lock:
            metrics["failed_reads"] += 1
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    """Redirect to monitor"""
    return send_file('dashboard.html')

@app.route("/api/info")
def system_info():
    """Main info endpoint"""
    return jsonify({
        "app": "Distributed Data Replication System",
        "consistency_mode": config.CONSISTENCY_MODE,
        "config": {
            "quorum_size": config.QUORUM_SIZE,
            "replication_delay_sec": config.REPLICATION_DELAY,
            "simulate_failures": SIMULATE_FAILURES,
            "failure_rate": FAILURE_RATE if SIMULATE_FAILURES else 0
        },
        "endpoints": {
            "monitor": "GET /monitor - Web monitoring dashboard",
            "store": "POST /api/store - Store data (body: {value: <val>})",
            "retrieve": "GET /api/retrieve/<node>?quorum=true - Retrieve from node",
            "status": "GET /api/system/status - System health status",
            "stats": "GET /api/analytics - System analytics",
            "cluster": "GET /api/cluster/members - All cluster members",
            "restart": "POST /api/system/restart - Restart all nodes",
            "toggle": "POST /api/cluster/<node>/toggle - Toggle node status"
        }
    })

@app.route("/monitor")
def monitor():
    """Serve the web monitoring dashboard"""
    return send_file('dashboard.html')

@app.route("/api/system/status", methods=["GET"])
def system_status():
    """System health status endpoint"""
    with node_lock:
        healthy_count = sum(1 for n in nodes.values() if n["status"] == "healthy")
        node_health = {
            name: {
                "status": data["status"],
                "last_heartbeat": time.time() - data["last_heartbeat"],
                "value": data["value"]
            }
            for name, data in nodes.items()
        }
    
    overall_health = "healthy" if healthy_count >= QUORUM_SIZE else "degraded"
    
    return jsonify({
        "status": overall_health,
        "healthy_nodes": healthy_count,
        "total_nodes": len(nodes),
        "quorum_met": healthy_count >= QUORUM_SIZE,
        "nodes": node_health
    })

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Get system analytics and metrics"""
    with metrics_lock:
        avg_write_latency = sum(metrics["write_latencies"]) / len(metrics["write_latencies"]) if metrics["write_latencies"] else 0
        avg_read_latency = sum(metrics["read_latencies"]) / len(metrics["read_latencies"]) if metrics["read_latencies"] else 0
        
        metrics_snapshot = {
            "total_writes": metrics["total_writes"],
            "total_reads": metrics["total_reads"],
            "failed_writes": metrics["failed_writes"],
            "failed_reads": metrics["failed_reads"],
            "conflicts_resolved": metrics["conflicts_resolved"],
            "read_repairs": metrics["read_repairs"],
            "avg_write_latency_ms": round(avg_write_latency * 1000, 2),
            "avg_read_latency_ms": round(avg_read_latency * 1000, 2),
            "success_rate": {
                "writes": round((metrics["total_writes"] - metrics["failed_writes"]) / metrics["total_writes"] * 100, 2) if metrics["total_writes"] > 0 else 100,
                "reads": round((metrics["total_reads"] - metrics["failed_reads"]) / metrics["total_reads"] * 100, 2) if metrics["total_reads"] > 0 else 100
            }
        }
    
    return jsonify(metrics_snapshot)

@app.route("/api/cluster/members", methods=["GET"])
def get_cluster_members():
    """Get all cluster member states"""
    with node_lock:
        nodes_info = {
            name: {
                "value": data["value"],
                "vector_clock": data["vector_clock"],
                "timestamp": data["timestamp"],
                "status": data["status"],
                "last_heartbeat_sec_ago": round(time.time() - data["last_heartbeat"], 2)
            }
            for name, data in nodes.items()
        }
    
    return jsonify({"nodes": nodes_info})

@app.route("/api/system/restart", methods=["POST"])
def restart_system():
    """Restart all nodes to initial state"""
    with node_lock:
        for name in nodes:
            nodes[name]["value"] = 0
            nodes[name]["vector_clock"] = {"node1": 0, "node2": 0, "node3": 0}
            nodes[name]["timestamp"] = datetime.now().isoformat()
            nodes[name]["status"] = "healthy"
            nodes[name]["last_heartbeat"] = time.time()
    
    with metrics_lock:
        metrics["total_writes"] = 0
        metrics["total_reads"] = 0
        metrics["failed_writes"] = 0
        metrics["failed_reads"] = 0
        metrics["conflicts_resolved"] = 0
        metrics["read_repairs"] = 0
        metrics["write_latencies"] = []
        metrics["read_latencies"] = []
    
    logger.info("System reset completed")
    return jsonify({"message": "All nodes and metrics reset"})

@app.route("/api/cluster/<node>/toggle", methods=["POST"])
def toggle_member_status(node):
    """Toggle cluster member status between healthy and unhealthy"""
    if node not in nodes:
        return jsonify({"error": f"Node '{node}' not found"}), 404
    
    with node_lock:
        current_status = nodes[node]["status"]
        new_status = "unhealthy" if current_status == "healthy" else "healthy"
        nodes[node]["status"] = new_status
        nodes[node]["last_heartbeat"] = time.time()
    
    logger.info(f"Node {node} status changed: {current_status} -> {new_status}")
    
    return jsonify({
        "node": node,
        "previous_status": current_status,
        "new_status": new_status
    })

@app.route("/api/settings/mode", methods=["GET", "POST"])
def consistency_settings():
    """Get or set consistency mode settings"""
    if request.method == "POST":
        data = request.json
        mode = data.get("mode", "").lower()
        
        if mode not in ["strong", "weak", "eventual"]:
            return jsonify({"error": "Invalid mode. Use: strong, weak, or eventual"}), 400
        
        old_mode = config.CONSISTENCY_MODE
        config.CONSISTENCY_MODE = mode
        
        logger.info(f"Consistency mode changed: {old_mode} -> {mode}")
        
        return jsonify({
            "success": True,
            "previous_mode": old_mode,
            "current_mode": config.CONSISTENCY_MODE,
            "message": f"Consistency mode changed to {mode.upper()}"
        })
    else:
        return jsonify({
            "consistency_mode": config.CONSISTENCY_MODE,
            "available_modes": ["strong", "weak", "eventual"],
            "config": {
                "quorum_size": config.QUORUM_SIZE,
                "replication_delay_sec": config.REPLICATION_DELAY
            }
        })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)

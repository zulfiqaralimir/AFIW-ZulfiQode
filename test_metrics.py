"""
Quick test script to generate metrics for Prometheus scraping
Run this while FastAPI is running to generate some test data
"""
import requests
import time

base_url = "http://127.0.0.1:8000"

print("Generating test metrics...")

# Make several requests to generate metrics
for i in range(5):
    try:
        # Health check
        resp = requests.get(f"{base_url}/health")
        print(f"✓ Health check {i+1}: {resp.status_code}")
        
        # Metrics endpoint
        resp = requests.get(f"{base_url}/metrics")
        print(f"✓ Metrics check {i+1}: {resp.status_code}")
        
        time.sleep(2)
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Make sure FastAPI is running on http://127.0.0.1:8000")

print("\nDone! Check Prometheus at http://localhost:9090")
print("Query: http_requests_total")


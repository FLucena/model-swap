#!/usr/bin/env python3
"""
Memory monitoring script for ModelSwap
"""
import psutil
import time
import requests
import json

def monitor_memory():
    """Monitor memory usage of the current process"""
    process = psutil.Process()
    
    print("Memory Monitoring for ModelSwap")
    print("=" * 40)
    
    while True:
        try:
            # Get current memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = process.memory_percent()
            
            # Try to get health endpoint if server is running
            try:
                response = requests.get('http://localhost:5000/health', timeout=2)
                if response.status_code == 200:
                    health_data = response.json()
                    server_memory = health_data.get('memory_usage_mb', 'N/A')
                    server_percent = health_data.get('memory_percent', 'N/A')
                    print(f"Local: {memory_mb:.2f} MB ({memory_percent:.1f}%) | Server: {server_memory} MB ({server_percent}%)")
                else:
                    print(f"Local: {memory_mb:.2f} MB ({memory_percent:.1f}%) | Server: Not responding")
            except requests.exceptions.RequestException:
                print(f"Local: {memory_mb:.2f} MB ({memory_percent:.1f}%) | Server: Not available")
            
            time.sleep(5)  # Check every 5 seconds
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_memory() 
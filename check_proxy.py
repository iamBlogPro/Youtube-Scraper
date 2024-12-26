import requests
import sys
import time
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def log_message(message, file=None):
    """Log message to both stdout and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    
    # Print to stdout
    print(full_message, flush=True)
    
    # Write to file if provided
    if file:
        file.write(full_message + "\n")
        file.flush()

def check_proxy(proxy_string, log_file=None):
    """Test if proxy works and can access YouTube"""
    ip, port, username, password = proxy_string.strip().split(':')
    
    proxy = {
        'http': f'http://{username}:{password}@{ip}:{port}',
        'https': f'http://{username}:{password}@{ip}:{port}'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    log_message(f"\nTesting proxy: {ip}:{port}", log_file)
    
    try:
        # Test 1: Basic connectivity with httpbin
        log_message("1. Testing basic connectivity...", log_file)
        r = requests.get(
            'http://httpbin.org/ip', 
            proxies=proxy, 
            headers=headers, 
            timeout=10, 
            verify=False
        )
        log_message(f"[SUCCESS] Proxy is online! Response: {r.text.strip()}", log_file)
        
        # Test 2: YouTube accessibility
        log_message("2. Testing YouTube access...", log_file)
        r = requests.get(
            'https://www.youtube.com', 
            proxies=proxy, 
            headers=headers, 
            timeout=10, 
            verify=False
        )
        log_message(f"[SUCCESS] YouTube accessible! Status code: {r.status_code}", log_file)
        
        return True
        
    except requests.exceptions.ProxyError as e:
        log_message(f"[ERROR] Proxy Error: {str(e)}", log_file)
    except requests.exceptions.SSLError as e:
        log_message(f"[ERROR] SSL Error: {str(e)}", log_file)
    except requests.exceptions.ConnectionError as e:
        log_message(f"[ERROR] Connection Error: {str(e)}", log_file)
    except requests.exceptions.Timeout as e:
        log_message(f"[ERROR] Timeout Error: {str(e)}", log_file)
    except Exception as e:
        log_message(f"[ERROR] Unexpected Error: {type(e).__name__}: {str(e)}", log_file)
    
    return False

if __name__ == "__main__":
    # Open log file with UTF-8 encoding
    with open('proxy_test.log', 'a', encoding='utf-8') as log_file:
        log_message("Starting proxy tests...", log_file)
        
        proxies = [
            "216.185.47.238:51523:fabwebsites:Fyf5Y3e6nU",
            "64.113.1.19:51523:fabwebsites:Fyf5Y3e6nU"
        ]
        
        for i, proxy in enumerate(proxies, 1):
            log_message(f"\nTesting Proxy #{i}", log_file)
            log_message("=" * 50, log_file)
            success = check_proxy(proxy, log_file)
            log_message(f"\nProxy #{i} {'WORKING' if success else 'FAILED'}", log_file)
            log_message("-" * 50, log_file)
            
        log_message("\nAll tests complete!", log_file) 
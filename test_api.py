"""
YouTube First Result API - Test Module
Created by BlogPro (hello@wordsigma.com)
Copyright (c) 2024 BlogPro. All rights reserved.
"""

import requests
import json
import time

def test_search():
    base_url = "http://127.0.0.1:8000"
    
    # Test cases
    keywords = [
        "python tutorial",
        "cute cats",
        "cooking recipe"
    ]
    
    for keyword in keywords:
        print(f"\nTesting search for: {keyword}")
        try:
            # Properly format the request body
            payload = {
                "keyword": keyword
            }
            
            response = requests.post(
                f"{base_url}/search",
                json=payload,  # Use json parameter to properly format request
                headers={
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            print("Response:")
            print(json.dumps(response.json(), indent=2))
            
            # Add delay between requests
            time.sleep(2)
            
        except requests.exceptions.ConnectionError:
            print(f"Connection error. Make sure the server is running on {base_url}")
        except requests.exceptions.Timeout:
            print("Request timed out")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_search() 
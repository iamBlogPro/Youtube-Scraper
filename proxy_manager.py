"""
YouTube First Result API - Proxy Management Module
Created by BlogPro (hello@wordsigma.com)
Copyright (c) 2024 BlogPro. All rights reserved.
"""

from typing import Dict, List
import random
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ProxyError(Exception):
    """Exception raised for proxy-related errors"""
    pass

class ProxyManager:
    def __init__(self):
        self.proxy_failures: Dict[str, int] = {}
        self.max_failures = 5
        self.proxies_file = 'proxies.txt'
        self.current_proxies: List[str] = []
        logger.debug("ProxyManager initialized")
        
    def load_proxies(self) -> List[str]:
        """Load proxies from text file"""
        if not os.path.exists(self.proxies_file):
            logger.warning(f"Proxies file not found: {self.proxies_file}")
            return []
        
        with open(self.proxies_file, 'r') as f:
            proxies = [line.strip() for line in f 
                      if line.strip() and not line.startswith('#')]
            logger.debug(f"Loaded {len(proxies)} proxies from file")
            self.current_proxies = proxies
            return proxies

    def format_proxy_url(self, proxy_line: str) -> str:
        """Format proxy string into URL format"""
        try:
            if '@' in proxy_line:  # Already formatted
                return f"http://{proxy_line}"
            
            parts = proxy_line.split(':')
            if len(parts) == 4:  # ip:port:username:password
                ip, port, username, password = parts
                return f"http://{username}:{password}@{ip}:{port}"
            elif len(parts) == 2:  # ip:port
                ip, port = parts
                return f"http://{ip}:{port}"
            else:
                raise ProxyError(f"Invalid proxy format: {proxy_line}")
                
        except Exception as e:
            logger.error(f"Error formatting proxy {proxy_line}: {str(e)}")
            raise ProxyError(f"Invalid proxy format: {proxy_line}")

    def get_proxy(self) -> str:
        """Get a random working proxy"""
        proxies = self.load_proxies()
        if not proxies:
            raise ProxyError("No proxies available")
        
        # Filter out failed proxies
        working_proxies = [p for p in proxies 
                          if self.proxy_failures.get(p, 0) < self.max_failures]
        
        if not working_proxies:
            # Reset failures if all proxies are failed
            logger.warning("All proxies failed, resetting failure counts")
            self.proxy_failures.clear()
            working_proxies = proxies
        
        proxy = random.choice(working_proxies)
        formatted_proxy = self.format_proxy_url(proxy)
        logger.debug(f"Selected proxy: {proxy.split(':')[0]}:****")
        return formatted_proxy

    def record_failure(self, proxy_url: str) -> None:
        """Record a proxy failure"""
        # Convert URL format back to storage format
        try:
            if '@' in proxy_url:
                proxy = proxy_url.split('@')[1].split(':')[0]
                for p in self.current_proxies:
                    if proxy in p:
                        proxy = p
                        break
            else:
                proxy = proxy_url.replace('http://', '')
            
            self.proxy_failures[proxy] = self.proxy_failures.get(proxy, 0) + 1
            failures = self.proxy_failures[proxy]
            logger.warning(f"Proxy {proxy.split(':')[0]} failed {failures} times")
            
            if failures >= self.max_failures:
                logger.error(f"Proxy {proxy.split(':')[0]} exceeded max failures")
        except Exception as e:
            logger.error(f"Error recording proxy failure: {str(e)}")

    def clear_failures(self, proxy_url: str) -> None:
        """Clear failure count for a proxy after successful use"""
        try:
            if '@' in proxy_url:
                proxy = proxy_url.split('@')[1].split(':')[0]
                for p in self.current_proxies:
                    if proxy in p:
                        proxy = p
                        break
            else:
                proxy = proxy_url.replace('http://', '')
                
            if proxy in self.proxy_failures:
                del self.proxy_failures[proxy]
                logger.debug(f"Cleared failures for proxy {proxy.split(':')[0]}")
        except Exception as e:
            logger.error(f"Error clearing proxy failures: {str(e)}")

    def list_proxies(self) -> List[Dict]:
        """List all proxies with their status"""
        proxies = self.load_proxies()
        return [
            {
                'proxy': proxy,
                'failures': self.proxy_failures.get(proxy, 0),
                'status': 'banned' if self.proxy_failures.get(proxy, 0) >= self.max_failures else 'active'
            }
            for proxy in proxies
        ] 
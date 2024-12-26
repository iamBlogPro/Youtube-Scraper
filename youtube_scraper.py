"""
YouTube First Result API - Scraper Module
Created by BlogPro (hello@wordsigma.com)
Copyright (c) 2024 BlogPro. All rights reserved.
"""

import re
import logging
import requests
import json
from bs4 import BeautifulSoup
from typing import Optional
from proxy_manager import ProxyManager, ProxyError
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class YouTubeScraperError(Exception):
    """Base exception for YouTube scraper errors"""
    pass

class VideoNotFoundError(YouTubeScraperError):
    """Exception raised when no video is found for the search term"""
    pass

class YouTubeScraper:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        logger.debug("YouTubeScraper initialized")

    def _make_request(self, url: str, proxy: str) -> str:
        """
        Make HTTP request with proxy
        Args:
            url (str): URL to request
            proxy (str): Proxy to use
        Returns:
            str: Response text
        Raises:
            requests.RequestException: If request fails
        """
        try:
            logger.debug(f"Making request to {url}")
            logger.debug(f"Using proxy: {proxy.split('@')[1] if '@' in proxy else proxy}")
            
            response = self.session.get(
                url,
                headers=self.headers,
                proxies={'http': proxy, 'https': proxy},
                timeout=10,
                verify=False
            )
            
            logger.debug(f"Response status code: {response.status_code}")
            response.raise_for_status()
            
            if len(response.text) < 1000:
                logger.error(f"Response too short ({len(response.text)} chars), might be blocked")
                raise YouTubeScraperError("Response too short, might be blocked")
                
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise YouTubeScraperError(f"Request failed: {str(e)}")

    def _extract_video_id(self, html: str) -> str:
        """Extract video ID from HTML using multiple methods"""
        # Method 1: Try finding videoRenderer in script tags
        script_pattern = r'"videoRenderer":{"videoId":"([^"]+)"'
        script_match = re.search(script_pattern, html)
        if script_match:
            return script_match.group(1)

        # Method 2: Try finding in ytInitialData
        data_pattern = r'var ytInitialData = ({.*?});</script>'
        data_match = re.search(data_pattern, html, re.DOTALL)
        if data_match:
            try:
                data = json.loads(data_match.group(1))
                contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
                for content in contents:
                    items = content.get('itemSectionRenderer', {}).get('contents', [])
                    for item in items:
                        if 'videoRenderer' in item:
                            return item['videoRenderer']['videoId']
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.warning(f"Failed to parse ytInitialData: {str(e)}")

        # Method 3: Try finding video links
        soup = BeautifulSoup(html, "lxml")
        for link in soup.find_all('a', href=True):
            match = re.search(r'/watch\?v=([^&]+)', link['href'])
            if match:
                return match.group(1)

        raise VideoNotFoundError("Could not find any video IDs in the response")

    def get_first_video_id(self, search_term: str) -> str:
        """
        Get the first video ID for a search term
        Args:
            search_term (str): YouTube search query
        Returns:
            str: YouTube video ID
        Raises:
            VideoNotFoundError: If no video is found
            ProxyError: If all proxies fail
            YouTubeScraperError: If scraping fails after all retries
        """
        url = f"https://www.youtube.com/results?search_query={search_term}"
        attempts = 0
        max_attempts = 10
        last_error = None
        
        while attempts < max_attempts:
            try:
                proxy = self.proxy_manager.get_proxy()
                html = self._make_request(url, proxy)
                video_id = self._extract_video_id(html)
                self.proxy_manager.clear_failures(proxy)  # Clear failures on success
                return video_id
                
            except (YouTubeScraperError, VideoNotFoundError) as e:
                last_error = e
                attempts += 1
                logger.warning(f"Attempt {attempts} failed: {str(e)}")
                self.proxy_manager.record_failure(proxy)
                
                if attempts < max_attempts:
                    time.sleep(1)  # Add small delay between retries
                    continue
                    
        raise YouTubeScraperError(f"Max retry attempts reached: {str(last_error)}") 
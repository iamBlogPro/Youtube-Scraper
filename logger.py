"""
YouTube First Result API - Logging Module
Created by BlogPro (hello@wordsigma.com)
Copyright (c) 2024 BlogPro. All rights reserved.
"""

import logging
import time
from datetime import datetime
from typing import Optional
import json
import os

class APILogger:
    def __init__(self):
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Set up file handler for detailed logs
        self.detailed_logger = logging.getLogger('detailed_logger')
        self.detailed_logger.setLevel(logging.INFO)
        
        # Create a file handler that creates a new file each day
        detailed_handler = logging.FileHandler(
            f'logs/detailed_{datetime.now().strftime("%Y-%m-%d")}.log'
        )
        detailed_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(message)s')
        )
        self.detailed_logger.addHandler(detailed_handler)

        # Add credits to log file header
        if not os.path.exists(f'logs/detailed_{datetime.now().strftime("%Y-%m-%d")}.log'):
            self.detailed_logger.info(
                "YouTube First Result API Logger - Created by BlogPro (hello@wordsigma.com)"
            )

    def log_request(self, keyword: str, video_id: Optional[str], duration: float, error: Optional[str] = None):
        """
        Log API request details
        Args:
            keyword: Search keyword
            video_id: YouTube video ID (if found)
            duration: Time taken to process request in seconds
            error: Error message if request failed
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'keyword': keyword,
            'video_id': video_id,
            'duration_seconds': round(duration, 3),
            'status': 'success' if video_id else 'error',
            'error': error
        }
        
        self.detailed_logger.info(json.dumps(log_entry))

# Global logger instance
api_logger = APILogger() 
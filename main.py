"""
YouTube First Result API
Created by BlogPro (hello@wordsigma.com)
Copyright (c) 2024 BlogPro. All rights reserved.
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any
import time
from youtube_scraper import YouTubeScraper, YouTubeScraperError, VideoNotFoundError
from logger import api_logger
import os
import logging
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube First Result API",
    description="""
    A FastAPI-based service that returns the first YouTube video ID for a given search term.
    
    ## Features
    * Get first YouTube video ID for any search term
    * Proxy rotation with failure tracking
    * Comprehensive error handling
    * Request/response logging
    
    ## Usage Notes
    - Recommended 2-second delay between requests
    - Proxies are banned after 5 failures
    - All responses include request duration

    ## Credits
    Created by BlogPro (hello@wordsigma.com)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    contact={
        "name": "BlogPro",
        "email": "hello@wordsigma.com"
    }
)

# Simple redirect for ReDoc
@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return RedirectResponse(url="/docs")

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def oauth2_redirect():
    raise HTTPException(status_code=404, detail="Not Found")

class SearchRequest(BaseModel):
    keyword: str = Field(
        ...,
        description="YouTube search term",
        example="python programming",
        min_length=1,
        max_length=100
    )

    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "python programming"
            }
        }

class SearchResponse(BaseModel):
    video_id: str = Field(
        ...,
        description="YouTube video ID",
        example="dQw4w9WgXcQ"
    )
    duration_seconds: float = Field(
        ...,
        description="Time taken to process request",
        example=1.234
    )

class ErrorResponse(BaseModel):
    error: str = Field(
        ...,
        description="Error type",
        example="Video not found"
    )
    detail: str = Field(
        ...,
        description="Detailed error message",
        example="No videos found for search term"
    )
    duration_seconds: float = Field(
        ...,
        description="Time taken to process request",
        example=1.234
    )

@app.middleware("http")
async def log_requests(request, call_next):
    logger.debug(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code}")
    return response

@app.post(
    "/search",
    response_model=SearchResponse,
    responses={
        200: {
            "description": "Successfully found video ID",
            "content": {
                "application/json": {
                    "example": {
                        "video_id": "dQw4w9WgXcQ",
                        "duration_seconds": 1.234
                    }
                }
            }
        },
        404: {
            "description": "Video not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "Video not found",
                        "detail": "No videos found for search term",
                        "duration_seconds": 1.234
                    }
                }
            }
        },
        500: {
            "description": "Server error",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "Scraping error",
                        "detail": "Max retry attempts reached",
                        "duration_seconds": 1.234
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation error",
                        "detail": "Invalid request format",
                        "duration_seconds": 0.001
                    }
                }
            }
        }
    },
    summary="Get first YouTube video ID",
    description="""
    Returns the first YouTube video ID for a given search term.
    
    - Uses proxy rotation for reliability
    - Handles rate limiting and proxy failures
    - Returns detailed error messages
    
    Example:
    ```python
    import requests
    response = requests.post(
        "http://localhost:8000/search",
        json={"keyword": "python tutorial"}
    )
    print(response.json()["video_id"])
    ```
    """
)
async def search_youtube(request: SearchRequest):
    """
    Search YouTube and return the first video ID for the given keyword.
    Uses rotating proxies from proxies.txt file.
    """
    start_time = time.time()
    try:
        scraper = YouTubeScraper()
        video_id = scraper.get_first_video_id(request.keyword)
        duration = time.time() - start_time
        
        # Log successful request
        api_logger.log_request(request.keyword, video_id, duration)
        
        return SearchResponse(video_id=video_id, duration_seconds=duration)
    
    except VideoNotFoundError as e:
        duration = time.time() - start_time
        api_logger.log_request(request.keyword, None, duration, str(e))
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Video not found",
                "detail": str(e),
                "duration_seconds": duration
            }
        )
    except YouTubeScraperError as e:
        duration = time.time() - start_time
        api_logger.log_request(request.keyword, None, duration, str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Scraping error",
                "detail": str(e),
                "duration_seconds": duration
            }
        )
    except Exception as e:
        duration = time.time() - start_time
        api_logger.log_request(request.keyword, None, duration, str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": str(e),
                "duration_seconds": duration
            }
        )

# Get port from environment variable or use default
PORT = int(os.getenv('API_PORT', 8000))

if __name__ == "__main__":
    import uvicorn
    
    # Try ports 8000 through 8010
    for port in range(8000, 8011):
        try:
            print(f"Attempting to start server on port {port}...")
            uvicorn.run(app, host="127.0.0.1", port=port)
            break
        except OSError as e:
            if e.errno == 10048:
                print(f"Port {port} is already in use, trying next port...")
                continue
            else:
                raise
        except Exception as e:
            print(f"Failed to start server: {str(e)}")
            break 
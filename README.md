# YouTube First Result API

A FastAPI-based service that returns the first YouTube video ID for a given search term. Features proxy rotation for reliability and error handling.

### 🛡️ Created by BlogPro (hello@wordsigma.com)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)

## Overview

This API scrapes YouTube search results using rotating proxies to reliably return the first video ID for any search term. Perfect for applications needing quick YouTube video lookups without the complexity of the official API.

## Features

- 🔍 Get first YouTube video ID for any search term
- 🔄 Smart proxy rotation with failure tracking
- 🛡️ Built-in rate limiting and proxy banning
- 📝 Comprehensive error handling
- 📊 Detailed request logging with timing

## Prerequisites

- Python 3.8+
- Working HTTP/HTTPS proxies
- pip (Python package manager)

## Dependencies

```
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
python-dotenv==1.0.0
pydantic==2.5.2
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/iamBlogPro/Youtube-Scraper.git
cd Youtube-Scraper
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure proxies in `proxies.txt`:
```
# Format: ip:port:username:password
123.45.67.89:8080:username:password
98.76.54.32:8080:username:password
```

## Usage

1. Start the server:
```bash
python main.py
```

2. The API will be available at `http://localhost:8000`

3. Access the interactive API documentation at `http://localhost:8000/docs`

### API Endpoint

`POST /search`

Request body:
```json
{
    "keyword": "your search term"
}
```

Successful Response (200):
```json
{
    "video_id": "dQw4w9WgXcQ",
    "duration_seconds": 1.234
}
```

### Code Examples

#### Python
```python
import requests

def search_youtube(keyword):
    response = requests.post(
        "http://localhost:8000/search",
        json={"keyword": keyword},
        headers={"Content-Type": "application/json"}
    )
    return response.json()

# Example usage
result = search_youtube("python tutorial")
print(f"Video ID: {result['video_id']}")
```

#### JavaScript/Node.js
```javascript
const axios = require('axios');

async function searchYoutube(keyword) {
    try {
        const response = await axios.post('http://localhost:8000/search', {
            keyword: keyword
        }, {
            headers: { 'Content-Type': 'application/json' }
        });
        return response.data;
    } catch (error) {
        console.error('Error:', error.response.data);
        throw error;
    }
}

// Example usage
searchYoutube('python tutorial')
    .then(result => console.log('Video ID:', result.video_id))
    .catch(error => console.error('Error:', error));
```

#### cURL
```bash
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"keyword":"python tutorial"}'
```

## Error Handling

The API uses standard HTTP status codes:

- `200`: Success - Video ID found
- `404`: Video not found
- `500`: Server error (proxy failures, scraping errors)
- `422`: Invalid request format

Error Response Format:
```json
{
    "error": "error type",
    "detail": "detailed error message",
    "duration_seconds": 1.234
}
```

## Configuration

### Proxy Settings
- Add proxies to `proxies.txt`
- Format: `ip:port:username:password`
- Proxies are rotated randomly
- Failed proxies are banned after 5 failures
- Banned proxies reset when all proxies fail

### Rate Limiting
- 2-second delay recommended between requests
- Proxy failures tracked individually
- Automatic proxy rotation on failure

## Logging

Logs are stored in `logs/detailed_YYYY-MM-DD.log`:
```json
{
    "timestamp": "2023-12-26T15:30:45.123456",
    "keyword": "python programming",
    "video_id": "dQw4w9WgXcQ",
    "duration_seconds": 1.234,
    "status": "success",
    "error": null
}
```

## Development

### Testing
```bash
# Test API endpoints
python test_api.py

# Verify proxy configuration
python check_proxy.py
```

### Project Structure
```
youtube-first-api/
├── main.py              # FastAPI application
├── youtube_scraper.py   # YouTube scraping logic
├── proxy_manager.py     # Proxy rotation handling
├── logger.py           # Logging configuration
├── requirements.txt    # Python dependencies
├── proxies.txt        # Proxy list
└── logs/              # Log files
```

## Best Practices

1. Implement proper error handling
2. Respect rate limits (2s between requests)
3. Monitor proxy performance
4. Keep proxy list updated
5. Check logs regularly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

Copyright (c) 2024 BlogPro (hello@wordsigma.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software. 
"""Firecrawl agent for scraping product data once daily."""

import logging
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

CACHE_FILE = Path("product_data_cache.json")
CACHE_DURATION = timedelta(days=1)

def load_cached_data():
    """Load cached product data if fresh."""
    if not CACHE_FILE.exists():
        return None
    
    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)
    
    cached_time = datetime.fromisoformat(cache['timestamp'])
    if datetime.now() - cached_time < CACHE_DURATION:
        logger.info("Using cached product data")
        return cache['data']
    
    return None

def save_cached_data(data):
    """Save product data to cache."""
    cache = {
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)
    logger.info("Saved product data to cache")

def scrape_product_data():
    """Scrape product data from all URLs once daily."""
    cached = load_cached_data()
    if cached:
        return cached
    
    logger.info("Scraping fresh product data...")
    
    urls = [
        "https://consumerai.info",
        "https://disputeai.xyz",
        "https://fdwa.site",
        "https://linktr.ee/omniai"
    ]
    
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    product_data = {}
    
    for url in urls:
        try:
            result = app.scrape(url, formats=['markdown'])
            product_data[url] = {
                'content': result.get('markdown', ''),
                'title': result.get('metadata', {}).get('title', ''),
                'description': result.get('metadata', {}).get('description', '')
            }
            logger.info(f"Scraped {url}")
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            product_data[url] = {'content': '', 'title': '', 'description': ''}
    
    save_cached_data(product_data)
    return product_data

def get_product_context():
    """Get product context for AI agent."""
    data = scrape_product_data()
    
    context = "PRODUCT KNOWLEDGE (scraped from our sites):\n\n"
    for url, info in data.items():
        context += f"URL: {url}\n"
        context += f"Title: {info['title']}\n"
        context += f"Description: {info['description']}\n"
        context += f"Content Preview: {info['content'][:500]}...\n\n"
    
    return context

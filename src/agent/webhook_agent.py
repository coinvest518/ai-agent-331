"""Webhook agent for sending video to Make.com automation."""

import logging
import os
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def send_video_to_webhook(video_path: str, title: str, description: str) -> dict:
    """Send video file to Make.com webhook.
    
    Args:
        video_path: Local path to video file.
        title: Video title.
        description: Video description.
        
    Returns:
        Webhook response.
    """
    webhook_url = os.getenv("MAKE_WEBHOOK_URL")
    
    if not webhook_url:
        logger.error("MAKE_WEBHOOK_URL not set in environment")
        return {"success": False, "error": "Webhook URL not configured"}
    
    logger.info(f"---SENDING VIDEO TO MAKE.COM WEBHOOK---")
    
    # Validate file exists
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return {"success": False, "error": "Video file not found"}
    
    file_size = os.path.getsize(video_path)
    logger.info(f"Video file: {video_path} ({file_size} bytes)")
    
    try:
        # Send video path and metadata (Make.com will need to access the file separately)
        payload = {
            'title': title,
            'description': description,
            'filename': os.path.basename(video_path),
            'video_path': os.path.abspath(video_path),
            'file_size_bytes': file_size,
            'status': 'video_ready'
        }
        
        response = requests.post(
            webhook_url, 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        response.raise_for_status()
        
        logger.info(f"Webhook response: {response.status_code} - {response.text[:200]}")
        
        # Try to parse JSON, fallback to text
        try:
            response_data = response.json() if response.text else {}
        except:
            response_data = {"text": response.text}
        
        return {"success": True, "status_code": response.status_code, "response": response_data}
            
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
        return {"success": False, "error": str(e)}

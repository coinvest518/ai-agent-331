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
        # Upload video to file.io for temporary public URL
        logger.info("Uploading video to file.io for public URL...")
        video_url = None
        
        try:
            with open(video_path, 'rb') as video_file:
                upload_response = requests.post(
                    'https://file.io',
                    files={'file': video_file},
                    timeout=120
                )
            
            logger.info(f"File.io response status: {upload_response.status_code}")
            logger.info(f"File.io response text: {upload_response.text[:200]}")
            
            if upload_response.status_code == 200 and upload_response.text:
                upload_data = upload_response.json()
                video_url = upload_data.get('link')
                logger.info(f"Video uploaded to: {video_url}")
            else:
                logger.warning(f"File.io upload failed: {upload_response.status_code}")
        except Exception as upload_error:
            logger.error(f"File upload error: {upload_error}")
        
        # Send video URL and metadata
        payload = {
            'title': title,
            'description': description,
            'filename': os.path.basename(video_path),
            'video_url': video_url or 'upload_failed',
            'file_size_bytes': file_size,
            'status': 'video_ready'
        }
        
        response = requests.post(
            webhook_url, 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        logger.info(f"Webhook response: {response.status_code}")
        
        # Make.com webhooks often return empty responses - this is OK
        if response.status_code in [200, 201, 202]:
            logger.info("Webhook sent successfully")
            return {"success": True, "status_code": response.status_code}
        else:
            logger.warning(f"Webhook returned status {response.status_code}: {response.text[:200]}")
            return {"success": False, "status_code": response.status_code, "error": response.text[:200]}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook request failed: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
        return {"success": False, "error": str(e)}

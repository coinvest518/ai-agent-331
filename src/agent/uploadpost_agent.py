"""UploadPost agent for multi-platform video uploads."""

import logging
import os
from upload_post import UploadPostClient
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def upload_video_multiplatform(video_path: str, title: str, description: str, platforms: list = ["youtube"]) -> dict:
    """Upload video to multiple platforms using UploadPost.
    
    Args:
        video_path: Local path to video file.
        title: Video title.
        description: Video description.
        platforms: List of platforms (youtube, tiktok, instagram).
        
    Returns:
        Upload result.
    """
    logger.info(f"---UPLOADING VIDEO TO {platforms}---")
    
    # Validate file exists
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return {"success": False, "error": "Video file not found"}
    
    file_size = os.path.getsize(video_path)
    logger.info(f"Video file: {video_path} ({file_size} bytes)")
    
    try:
        client = UploadPostClient(api_key=os.getenv("UPLOADPOST_API_KEY"))
        
        response = client.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            user=os.getenv("UPLOADPOST_USER"),
            platforms=platforms
        )
        
        logger.info(f"Upload response: {response}")
        return {"success": True, "response": response}
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return {"success": False, "error": str(e)}

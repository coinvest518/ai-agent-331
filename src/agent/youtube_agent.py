"""YouTube agent for uploading videos and getting channel analytics."""

import logging
import os
from composio import Composio
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize Composio client
composio_client = Composio(
    api_key=os.getenv("COMPOSIO_API_KEY"),
    entity_id=os.getenv("YOUTUBE_ENTITY_ID", "default")
)


def upload_video_to_youtube(video_path: str, title: str, description: str) -> dict:
    """Upload video to YouTube.
    
    Args:
        video_path: Local path to video file.
        title: Video title.
        description: Video description.
        
    Returns:
        Upload result with video ID.
    """
    logger.info("---UPLOADING VIDEO TO YOUTUBE---")
    
    import time
    import os
    
    # Verify file exists and is valid MP4
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return {"success": False, "error": "Video file not found"}
    
    file_size = os.path.getsize(video_path)
    logger.info(f"Video file size: {file_size} bytes")
    
    if file_size == 0:
        logger.error("Video file is empty")
        return {"success": False, "error": "Video file is empty"}
    
    # Wait for video file to stabilize
    logger.info("Waiting 10 seconds for video file to stabilize...")
    time.sleep(10)
    
    try:
        result = composio_client.tools.execute(
            "YOUTUBE_UPLOAD_VIDEO",
            {
                "videoFilePath": video_path,
                "title": title,
                "description": description,
                "privacyStatus": "unlisted",
                "categoryId": "22",
                "tags": ["SantaSpot", "Holidays", "Family", "Christmas", "AI"]
            },
            connected_account_id=os.getenv("YOUTUBE_ACCOUNT_ID")
        )
        
        logger.info(f"Upload response: {result}")
        
        if result.get("successful"):
            video_data = result.get("data", {})
            video_id = video_data.get("id") or video_data.get("response_data", {}).get("id")
            logger.info(f"Video uploaded successfully! ID: {video_id}")
            return {"success": True, "video_id": video_id, "data": video_data}
        else:
            error = result.get("error", "Unknown error")
            logger.error(f"Upload failed: {error}")
            return {"success": False, "error": error}
            
    except Exception as e:
        logger.error(f"YouTube upload exception: {e}")
        return {"success": False, "error": str(e)}


def get_channel_id_by_handle(handle: str) -> dict:
    """Get YouTube channel ID from handle.
    
    Args:
        handle: YouTube channel handle (e.g., @MHEMEDIA).
        
    Returns:
        Channel ID.
    """
    logger.info(f"---GETTING CHANNEL ID FOR {handle}---")
    
    try:
        result = composio_client.tools.execute(
            "YOUTUBE_GET_CHANNEL_ID_BY_HANDLE",
            {"channel_handle": handle},
            connected_account_id=os.getenv("YOUTUBE_ACCOUNT_ID")
        )
        
        if result.get("successful"):
            data = result.get("data", {})
            channel_id = data.get("items", [{}])[0].get("id")
            logger.info(f"Channel ID: {channel_id}")
            return {"success": True, "channel_id": channel_id}
        else:
            error = result.get("error", "Unknown error")
            logger.error(f"Failed: {error}")
            return {"success": False, "error": error}
    except Exception as e:
        logger.error(f"Exception: {e}")
        return {"success": False, "error": str(e)}


def get_channel_statistics(channel_id: str = None, handle: str = "@MHEMEDIA") -> dict:
    """Get YouTube channel statistics.
    
    Args:
        channel_id: YouTube channel ID.
        
    Returns:
        Channel statistics including subscriber count, view count, video count.
    """
    logger.info("---GETTING YOUTUBE CHANNEL STATISTICS---")
    
    try:
        # Get channel ID from handle if not provided
        if not channel_id:
            handle_result = get_channel_id_by_handle(handle)
            if not handle_result.get("success"):
                return handle_result
            channel_id = handle_result.get("channel_id")
        
        result = composio_client.tools.execute(
            "YOUTUBE_GET_CHANNEL_STATISTICS",
            {"id": channel_id, "part": "statistics"},
            connected_account_id=os.getenv("YOUTUBE_ACCOUNT_ID")
        )
        
        if result.get("successful"):
            data = result.get("data", {})
            stats = data.get("items", [{}])[0].get("statistics", {})
            
            logger.info(f"Channel Stats - Subscribers: {stats.get('subscriberCount')}, Views: {stats.get('viewCount')}, Videos: {stats.get('videoCount')}")
            return {"success": True, "statistics": stats}
        else:
            error = result.get("error", "Unknown error")
            logger.error(f"Failed to get statistics: {error}")
            return {"success": False, "error": error}
            
    except Exception as e:
        logger.error(f"YouTube statistics exception: {e}")
        return {"success": False, "error": str(e)}


def get_channel_activities(channel_id: str = None, handle: str = "@MHEMEDIA", max_results: int = 10) -> dict:
    """Get recent channel activities.
    
    Args:
        channel_id: YouTube channel ID (optional).
        handle: YouTube channel handle (default: @MHEMEDIA).
        max_results: Maximum number of activities to return.
        
    Returns:
        Recent channel activities.
    """
    logger.info("---GETTING YOUTUBE CHANNEL ACTIVITIES---")
    
    try:
        # Get channel ID from handle if not provided
        if not channel_id:
            handle_result = get_channel_id_by_handle(handle)
            if not handle_result.get("success"):
                return handle_result
            channel_id = handle_result.get("channel_id")
        
        result = composio_client.tools.execute(
            "YOUTUBE_GET_CHANNEL_ACTIVITIES",
            {
                "channelId": channel_id,
                "maxResults": max_results,
                "part": "snippet,contentDetails"
            },
            connected_account_id=os.getenv("YOUTUBE_ACCOUNT_ID")
        )
        
        if result.get("successful"):
            data = result.get("data", {})
            activities = data.get("items", [])
            logger.info(f"Retrieved {len(activities)} activities")
            return {"success": True, "activities": activities}
        else:
            error = result.get("error", "Unknown error")
            logger.error(f"Failed to get activities: {error}")
            return {"success": False, "error": error}
            
    except Exception as e:
        logger.error(f"YouTube activities exception: {e}")
        return {"success": False, "error": str(e)}

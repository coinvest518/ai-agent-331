"""Google Drive agent for uploading videos using Composio."""

import logging
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()
logger = logging.getLogger(__name__)

composio_client = Composio(
    api_key=os.getenv("COMPOSIO_API_KEY"),
    entity_id=os.getenv("GOOGLEDRIVE_ENTITY_ID")
)


def upload_video_to_drive(video_path: str, title: str, description: str) -> dict:
    """Upload video to Google Drive using Composio.
    
    Args:
        video_path: Local path to video file.
        title: Video title.
        description: Video description.
        
    Returns:
        Upload response.
    """
    logger.info("---UPLOADING VIDEO TO GOOGLE DRIVE---")
    
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return {"success": False, "error": "Video file not found"}
    
    file_size = os.path.getsize(video_path)
    logger.info(f"Video file: {video_path} ({file_size} bytes)")
    
    try:
        # Find "AI Video" folder
        logger.info("Finding AI Video folder...")
        folder_result = composio_client.tools.execute(
            "GOOGLEDRIVE_FIND_FOLDER",
            {"name_exact": "AI Video"},
            connected_account_id=os.getenv("GOOGLEDRIVE_CONNECTION_ID")
        )
        
        folder_id = None
        if folder_result.get("successful"):
            files = folder_result.get("data", {}).get("files", [])
            if files:
                folder_id = files[0]["id"]
                logger.info(f"Found folder ID: {folder_id}")
        
        # Upload to Google Drive
        logger.info("Uploading to Google Drive...")
        upload_params = {"file_to_upload": video_path, "folder_to_upload_to": folder_id}
        
        result = composio_client.tools.execute(
            "GOOGLEDRIVE_UPLOAD_FILE",
            upload_params,
            connected_account_id=os.getenv("GOOGLEDRIVE_CONNECTION_ID")
        )
        
        if result.get("successful"):
            file_data = result.get("data", {})
            logger.info(f"Video uploaded successfully! File ID: {file_data.get('id')}")
            return {"success": True, "response": file_data}
        else:
            logger.error(f"Drive upload failed: {result.get('error')}")
            return {"success": False, "error": result.get("error")}
            
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return {"success": False, "error": str(e)}

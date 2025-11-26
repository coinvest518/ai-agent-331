"""Test webhook agent with existing video."""

import os
from pathlib import Path
from dotenv import load_dotenv
from src.agent.webhook_agent import send_video_to_webhook

load_dotenv()

def test_webhook():
    """Test sending video to Make.com webhook."""
    
    # Find a video in temp_videos folder
    temp_dir = Path("temp_videos")
    videos = list(temp_dir.glob("*.mp4"))
    
    if not videos:
        print("No videos found in temp_videos folder")
        return
    
    video_path = str(videos[0])
    print(f"Testing with video: {video_path}")
    
    result = send_video_to_webhook(
        video_path=video_path,
        title="Test Video from Santa's Spot",
        description="This is a test video sent to Make.com webhook for automation testing."
    )
    
    print(f"\nResult: {result}")

if __name__ == "__main__":
    test_webhook()

"""Simple test for Google Drive upload."""

from src.agent.googledrive_agent import upload_video_to_drive

# Test with existing video file
video_path = "temp_videos/santa_spot_reel_1764168083.mp4"
title = "Test Holiday Video"
description = "Testing Google Drive upload"

print("Testing Google Drive upload...")
result = upload_video_to_drive(video_path, title, description)
print(f"Result: {result}")

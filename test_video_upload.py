"""Test video upload to YouTube."""

from src.agent.youtube_agent import upload_video_to_youtube
from pathlib import Path

def test_video_upload():
    """Test uploading a video to YouTube."""
    print("\n=== Testing YouTube Video Upload ===")
    
    # Find a generated video in temp_videos folder
    temp_dir = Path("temp_videos")
    if not temp_dir.exists():
        print("No temp_videos folder found. Generate a video first.")
        return
    
    videos = list(temp_dir.glob("*.mp4"))
    if not videos:
        print("No videos found in temp_videos folder.")
        return
    
    video_path = str(videos[0])
    print(f"Uploading: {video_path}")
    
    result = upload_video_to_youtube(
        video_path=video_path,
        title="Santa's Spot - Holiday Magic Awaits!",
        description="Experience the joy of the holidays with Santa's Spot! Plan magical moments with your family.\n\nVisit https://santaspot.xyz for more!"
    )
    
    if result.get("success"):
        print(f"SUCCESS! Video ID: {result.get('video_id')}")
    else:
        print(f"FAILED: {result.get('error')}")

if __name__ == "__main__":
    test_video_upload()

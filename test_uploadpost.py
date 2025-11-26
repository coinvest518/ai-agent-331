"""Test UploadPost video upload."""

from src.agent.uploadpost_agent import upload_video_multiplatform
from pathlib import Path

def test_uploadpost():
    """Test uploading video with UploadPost."""
    print("\n=== Testing UploadPost Video Upload ===")
    
    temp_dir = Path("temp_videos")
    videos = list(temp_dir.glob("*.mp4"))
    
    if not videos:
        print("No videos found. Generate one first.")
        return
    
    video_path = str(videos[0])
    print(f"Uploading: {video_path}")
    
    result = upload_video_multiplatform(
        video_path=video_path,
        title="Santa's Spot - Holiday Magic",
        description="Experience the joy of the holidays! Visit https://santaspot.xyz",
        platforms=["youtube"]
    )
    
    if result.get("success"):
        print(f"SUCCESS! Response: {result.get('response')}")
    else:
        print(f"FAILED: {result.get('error')}")

if __name__ == "__main__":
    test_uploadpost()

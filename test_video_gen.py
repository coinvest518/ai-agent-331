"""Test video generation only."""

from src.agent.video_agent import generate_video_from_tweet

def test_video_generation():
    """Test generating a video from tweet text."""
    print("\n=== Testing Video Generation ===")
    
    tweet_text = "Holiday magic awaits with Santa's Spot! Plan magical moments together. https://santaspot.xyz"
    
    print(f"Generating video for: {tweet_text}")
    
    video_path = generate_video_from_tweet(tweet_text)
    
    if video_path:
        print(f"SUCCESS! Video saved to: {video_path}")
    else:
        print("FAILED: Video generation failed")

if __name__ == "__main__":
    test_video_generation()

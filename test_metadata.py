"""Test YouTube metadata generation."""

from src.agent.youtube_metadata_agent import generate_youtube_metadata

def test_metadata():
    """Test AI-generated YouTube metadata."""
    print("\n=== Testing YouTube Metadata Generation ===")
    
    tweet_text = "Holiday magic awaits with Santa's Spot! Plan magical moments together. https://santaspot.xyz"
    
    metadata = generate_youtube_metadata(tweet_text)
    
    print(f"\nTITLE: {metadata['title']}")
    print(f"\nDESCRIPTION LENGTH: {len(metadata['description'])} characters")
    print("\nDESCRIPTION PREVIEW (first 300 chars):")
    print(metadata['description'][:300])

if __name__ == "__main__":
    test_metadata()

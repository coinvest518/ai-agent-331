"""Test YouTube agent functionality."""

from src.agent.youtube_agent import get_channel_statistics, get_channel_activities

def test_youtube_analytics():
    """Test YouTube channel analytics."""
    print("\n=== Testing YouTube Channel Statistics ===")
    
    # Get channel statistics
    stats_result = get_channel_statistics()
    if stats_result.get("success"):
        stats = stats_result.get("statistics", {})
        print(f"Subscribers: {stats.get('subscriberCount', 'N/A')}")
        print(f"Total Views: {stats.get('viewCount', 'N/A')}")
        print(f"Total Videos: {stats.get('videoCount', 'N/A')}")
    else:
        print(f"Failed: {stats_result.get('error')}")
    
    print("\n=== Testing YouTube Channel Activities ===")
    
    # Get recent activities
    activities_result = get_channel_activities(max_results=5)
    if activities_result.get("success"):
        activities = activities_result.get("activities", [])
        print(f"Retrieved {len(activities)} recent activities")
        for i, activity in enumerate(activities[:3], 1):
            snippet = activity.get("snippet", {})
            print(f"  {i}. {snippet.get('type')}: {snippet.get('title', 'N/A')}")
    else:
        print(f"Failed: {activities_result.get('error')}")

if __name__ == "__main__":
    test_youtube_analytics()

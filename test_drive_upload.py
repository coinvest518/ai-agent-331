"""Test Google Drive upload functionality."""

import asyncio
from src.agent.graph import graph, State

async def test_drive_upload():
    """Test posting a tweet which generates and uploads video to Google Drive."""
    
    state = State(
        query="post a new tweet: Create magical holiday memories with your family!"
    )
    
    print("Testing tweet post with video generation and Google Drive upload...")
    print(f"Query: {state.query}")
    
    result = await graph.ainvoke(state)
    
    print("=== RESULT ===")
    print(result.get("analysis", "No analysis returned"))

if __name__ == "__main__":
    asyncio.run(test_drive_upload())

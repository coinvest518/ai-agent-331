"""Test the new marketing agent."""

import asyncio
import sys
from src.agent.graph import graph, State
from src.agent.marketing_prompt import get_marketing_prompt

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

def test_prompt():
    """Display the marketing prompt."""
    print("="*80)
    print("MARKETING AGENT PROMPT")
    print("="*80)
    print(get_marketing_prompt())
    print("="*80)

async def test_post():
    """Test posting with new marketing agent."""
    state = State(
        query="post a new tweet: yo just found this AI tool that fixes credit automatically"
    )
    
    print("\nTesting marketing agent post...")
    result = await graph.ainvoke(state)
    print(f"\nResult: {result.get('analysis', 'No result')}")

if __name__ == "__main__":
    # Show the prompt
    test_prompt()
    
    # Test a post
    print("\n\nPress Enter to test a post (or Ctrl+C to skip)...")
    try:
        input()
        asyncio.run(test_post())
    except KeyboardInterrupt:
        print("\nSkipped post test")

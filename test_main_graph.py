#!/usr/bin/env python3
"""Test the main AI agent graph."""

import asyncio
from src.agent.graph import graph, State

async def test_main_graph():
    """Test the main LangGraph agent."""
    
    queries = [
        "search for tweets about holidays",
        "lookup tweet 1234567890", 
        "retweet 1234567890",
        "post a new tweet: Discover the joy of family holidays with Santa's Spot! Plan magical moments together.",
        "create a poll: What's your favorite holiday tradition? Baking cookies, Decorating tree, Gift shopping, Family gatherings"
    ]
    
    print("[MAIN GRAPH TEST] Testing your AI agent...")
    print("="*50)
    
    for query in queries:
        print(f"\n[QUERY] {query}")
        print("-" * 30)
        
        try:
            # Create state
            state = State(query=query)
            
            # Run the graph
            result = await graph.ainvoke(state)
            
            # Show result
            print(result.get("analysis", "No analysis returned"))
            
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(test_main_graph())
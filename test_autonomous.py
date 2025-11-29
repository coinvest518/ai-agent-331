"""Test autonomous posting."""

import asyncio
from src.agent.graph import graph, State

async def test():
    state = State(query="post a new tweet: yo this AI credit repair tool is actually fire")
    print("Testing autonomous post...")
    result = await graph.ainvoke(state)
    print(f"\nResult: {result.get('analysis', 'No result')}")

asyncio.run(test())

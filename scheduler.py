"""Scheduler to run Twitter agent every 1 hour 17 minutes."""

import asyncio
import time
from datetime import datetime
from src.agent.graph import graph, State

async def run_agent():
    """Run the Twitter agent."""
    print(f"\n[{datetime.now()}] Running Twitter agent...")
    
    queries = [
        "post a new tweet: Discover the joy of family holidays with Santa's Spot! Plan magical moments together.",
        "post a new tweet: What's your favorite holiday tradition?",
        "post a new tweet: Make this holiday season unforgettable with Santa's Spot!",
    ]
    
    import random
    query = random.choice(queries)
    
    try:
        result = await graph.ainvoke(State(query=query))
        print(f"[{datetime.now()}] Agent completed successfully")
        print(f"Analysis: {result.get('analysis', 'N/A')[:200]}...")
    except Exception as e:
        print(f"[{datetime.now()}] Agent failed: {e}")

def main():
    """Run agent every 1 hour 17 minutes."""
    interval = (1 * 60 * 60) + (17 * 60)  # 1 hour 17 minutes in seconds
    
    print(f"Starting scheduler - will run every {interval // 60} minutes")
    
    while True:
        asyncio.run(run_agent())
        print(f"[{datetime.now()}] Sleeping for {interval // 60} minutes...")
        time.sleep(interval)

if __name__ == "__main__":
    main()

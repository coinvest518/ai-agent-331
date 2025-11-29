"""Autonomous AI marketing agent scheduler."""

import asyncio
import time
import random
from datetime import datetime
from src.agent.graph import graph, State

async def run_agent():
    """Run the AI marketing agent autonomously."""
    print(f"\n[{datetime.now()}] AI Agent running autonomously...")
    
    # UGC-style post ideas that rotate
    post_ideas = [
        "yo check out this AI credit repair tool - been using it and it actually works",
        "real talk - if bad credit is holding you back, this AI can help fix it",
        "just automated my entire credit dispute process with AI and saved so much time",
        "ngl this AI tool for credit repair is fire - way cheaper than those services",
        "been building AI agents and this credit repair one is my favorite",
        "if you're tired of paying for credit repair, check this AI tool out",
        "this AI literally writes dispute letters for you - game changer",
        "yo anyone else using AI for credit repair? this tool is insane",
        "just helped someone boost their credit score 100 points with this AI",
        "real question - why pay $100/month for credit repair when AI does it free?",
    ]
    
    query = f"post a new tweet: {random.choice(post_ideas)}"
    
    try:
        result = await graph.ainvoke(State(query=query))
        print(f"[{datetime.now()}] ✅ Posted successfully")
        print(f"Result: {result.get('analysis', 'N/A')[:200]}...")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Failed: {e}")

def main():
    """Run agent every 1 hour 17 minutes autonomously."""
    interval = (1 * 60 * 60) + (17 * 60)
    
    print("🤖 AI Marketing Agent - Running Autonomously")
    print(f"📅 Posts every {interval // 60} minutes")
    print("🔥 UGC-style content rotation enabled\n")
    
    while True:
        asyncio.run(run_agent())
        print(f"[{datetime.now()}] 😴 Sleeping for {interval // 60} minutes...\n")
        time.sleep(interval)

if __name__ == "__main__":
    main()

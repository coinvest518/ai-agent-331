"""Generate YouTube titles and descriptions using AI."""

import logging
import os
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def generate_youtube_metadata(tweet_text: str) -> dict:
    """Generate YouTube title and description from tweet.
    
    Args:
        tweet_text: Original tweet text.
        
    Returns:
        Dict with title and description.
    """
    logger.info("---GENERATING YOUTUBE METADATA---")
    
    llm = GoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Use full template directly
    description_template = f"""The Digital Hustle Revolution is HERE — featuring: @omniai + @futuristicwealth

Take back control of your money, credit, data, and digital life.
Start using DisputeAI — my automated credit repair & consumer-law toolkit.
👉 https://disputeai.xyz

Huge shoutout to everyone who's been supporting my projects: OmniAI Systems, FDWA (Futuristic Digital Wealth Agency), MHE Gardens, and Fortis Proles Nonprofit. None of this exists without your energy & community.

Join the movement & tap in with all my ventures here:
🔗 https://linktr.ee/omniai

🎅 Try SantaSpot — My Holiday Giveaway & Referral App

Win prizes, support small creators, donate $1, and invite friends to earn rewards.
This holiday season I'm giving back because I never had family or big support myself — so I built a place where people like us can connect, win, and not feel alone.
👉 https://santaspot.xyz

🌐 Explore All My AI Tools & Products

AI Business Automation • Credit Repair Systems • Social Media AI Agents • Real Estate AI • Doula & Wellness Tools • Digital Products

FDWA Agency (AI automation for entrepreneurs): https://fwda.site
ConsumerAI (AI tools for everyday people): https://consumerai.info
OmniAI Multi-Agent Chat Interface: https://omniai.icu
DisputeAI (Credit Repair + Consumer Law Automation): https://disputeai.xyz
My Blog + Projects: https://futuristic-wealth.beehiiv.com/

📌 Book a 1-on-1 AI Consultation

Want me to automate your business, build your AI agent system, or fix your credit using AI?
Book here: https://cal.com/bookme-daniel/ai-consultation-smb

📄 Sources, Tools & Inspiration for This Video

A lot of this video's concepts, data, and systems come from:
• FTC + CFPB consumer-protection databases
• FCRA + FDCPA federal statutes
• NYS legal frameworks
• AI-automation research (LangChain, LangGraph, Composio, n8n)
• Community stories and user submissions

Full resource sheet:
📄 https://buymeacoffee.com/coinvest

💡 About This Video

In this video, I break down how AI, automation, and consumer-law systems can help everyday people escape debt traps, rebuild credit, generate digital income, and leverage the same tools big companies use — but for regular people.

From automated dispute systems to holiday giveaways to building AI assistants that run entire businesses, this video is for creators, hustlers, and anyone trying to build a better life with limited resources.

🙏 Special Thanks

To everyone from Albany NY to across the world supporting my nonprofit Fortis Proles, the youth programs, the doula training, the workshops, the digital products, and all the people following my AI journey.

🎵 Music

All soundtrack & audio by various independent producers — support indie artists.

🎥 Get Behind-the-Scenes Access

Exclusive content, early product drops, AI prompts, unreleased agents:
👉 https://buymeacoffee.com/coinvest

🛒 Merch & Digital Products

• AI templates
• Credit-repair bundles
• Real estate outreach kits
• Doula maternal support guides
• Brand kits & content packs
Shop everything here:
👉 https://whop.com/futuristicwealth/

📩 Have a story or idea for me?

Submit questions, requests, or topics you want me to cover:
📬 https://futuristic-wealth.beehiiv.com/

🧭 Find Me Online

Instagram: https://www.instagram.com/streets2entrepreneurs/
Twitter/X: https://x.com/omniai_ai
TikTok: https://tiktok.com/@streets2entrepreneurs
YouTube: https://youtube.com/@mhemedia
LinkedIn: https://www.linkedin.com/in/coinvestinno/
Discord: https://discord.gg/NTNszcwE
Telegram: https://t.me/+dze7uLV-ER41Zjdh

📜 AI Disclosure

I use AI across my projects — but everything published is rewritten, edited, and finalized by me.
Some visuals or drafts may start with AI generation, but every final product goes through my hands.
I believe in transparency as we build out the future of creative automation.

🧑💼 About Me (Daniel — FDWA / OmniAI)

Daniel Wray (a.k.a. D Smith) is an AI systems builder, automation specialist, digital-wealth strategist, and founder of multiple ventures including:

• FDWA — Futuristic Digital Wealth Agency
• OmniAI Systems
• Fortis Proles Nonprofit
• MHE Gardens Eco Retreat Project

I create tools, apps, workflows, and systems that help regular people access AI, credit repair, real estate pathways, income streams, and digital automation — no gatekeeping."""
    
    prompt = f"""Create a catchy YouTube title (max 60 chars, NO URLs) for this video topic:

TOPIC: {tweet_text}

OUTPUT ONLY the title, nothing else."""
    
    try:
        title = llm.invoke(prompt).strip()
        
        # Use full template for description
        description = description_template
        
        # Fallback if title generation fails
        if not title or len(title) > 100:
            title = "Holiday Magic with Santa's Spot"
        
        logger.info(f"Generated title: {title}")
        logger.info(f"Generated description: {description[:100]}...")
        
        return {"title": title[:100], "description": description}
        
    except Exception as e:
        logger.error(f"Failed to generate metadata: {e}")
        return {
            "title": "Holiday Magic with Santa's Spot",
            "description": f"{tweet_text}\n\nVisit https://santaspot.xyz for more holiday magic!"
        }

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict
from dataclasses import dataclass

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI, Modality
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
import asyncio
from langsmith import configure
from dotenv import load_dotenv
import requests
import aiohttp
import json
from .image_subagent import enhance_prompt_for_image
from .video_agent import generate_video_from_tweet
from .youtube_agent import get_channel_statistics, get_channel_id_by_handle
from .uploadpost_agent import upload_video_multiplatform
from .youtube_metadata_agent import generate_youtube_metadata
from .googledrive_agent import upload_video_to_drive

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure LangSmith tracing
configure(project_name="twitter-composio-agent")

# Initialize Google AI LLM with error handling
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
except Exception as e:
    print(f"Warning: Could not initialize Google AI LLM: {e}")
    print("Please set your GOOGLE_API_KEY in the .env file")
    llm = None

# Initialize Composio API configuration
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
CONNECTION_ID = os.getenv("TWITTER_CONNECTION_ID")
GOOGLE_CONNECTION_ID = os.getenv("GOOGLE_CONNECTION_ID", CONNECTION_ID)
COMPOSIO_BASE_URL = "https://backend.composio.dev/api/v3/tools/execute"

# Initialize Composio client
from composio import Composio
composio_client = Composio(
    api_key=COMPOSIO_API_KEY,
    entity_id=os.getenv("TWITTER_ENTITY_ID")
)

def _download_image_from_url(image_url: str) -> str:
    """Download image from URL and save locally.
    
    Args:
        image_url: URL of the image to download.
        
    Returns:
        Local file path of downloaded image.
    """
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Create temp directory if it doesn't exist
        temp_dir = Path("temp_images")
        temp_dir.mkdir(exist_ok=True)
        
        # Extract filename from URL or generate one
        filename = image_url.split("/")[-1] or "image.jpg"
        if not filename.endswith((".jpg", ".jpeg", ".png")):
            filename += ".jpg"
        
        local_path = temp_dir / filename
        local_path.write_bytes(response.content)
        
        logger.info("Downloaded image to: %s", local_path)
        return str(local_path)
    except Exception as e:
        logger.exception("Failed to download image: %s", e)
        return None

# Available Twitter-related Composio tool slugs (placeholder names).
# Replace the values with the actual tool identifiers from your Composio project.
TWITTER_TOOLS = {
    # Post lookups
    "post_lookup_by_post_id": "TWITTER_POST_LOOKUP_BY_POST_ID",
    "post_lookup_by_post_ids": "TWITTER_POST_LOOKUP_BY_POST_IDS",
    # Search
    "recent_search": "TWITTER_RECENT_SEARCH",
    # Engagements
    "retweet_post": "TWITTER_RETWEET_POST",
    "user_like_post": "TWITTER_USER_LIKE_POST",
    # Messaging
    "send_dm_conversation": "TWITTER_SEND_A_NEW_MESSAGE_TO_A_DM_CONVERSATION",
    "send_dm_user": "TWITTER_SEND_A_NEW_MESSAGE_TO_A_USER",
    # Optional: posting (reply/comment) if available in Composio
    "post_tweet": "TWITTER_POST_TWEET",
    # User lookup
    "user_lookup_me": "TWITTER_USER_LOOKUP_ME",
    # Creation of posts
    "creation_of_a_post": "TWITTER_CREATION_OF_A_POST",
    # Media upload
    "upload_media": "TWITTER_UPLOAD_MEDIA",
    "get_media_upload_status": "TWITTER_GET_MEDIA_UPLOAD_STATUS",
}

print(f"Initialized Twitter tools: {list(TWITTER_TOOLS.keys())}")


async def call_composio_tool(tool_name: str, query: str = None, params: dict = None) -> dict:
    """Call a Composio tool for the connected account.

    This is a lightweight wrapper that mirrors the previous Composio usage.
    Do NOT commit API keys or connection IDs into source control; use environment variables.
    """
    if tool_name not in TWITTER_TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}

    headers = {
        "x-api-key": COMPOSIO_API_KEY,
        "Content-Type": "application/json"
    }

    # Use Google connection for image generation
    connected_account_id = GOOGLE_CONNECTION_ID if tool_name == "generate_image" else CONNECTION_ID

    if params:
        payload = {
            "connected_account_id": connected_account_id,
            "arguments": params
        }
    elif query:
        payload = {
            "connected_account_id": connected_account_id,
            "text": query
        }
    else:
        payload = {"connected_account_id": connected_account_id}

    try:
        async with aiohttp.ClientSession() as session:
            url = f"{COMPOSIO_BASE_URL}/{TWITTER_TOOLS[tool_name]}"
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()
                return result
    except Exception as e:
        return {"error": str(e)}

# Define the Twitter-focused prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI-powered Twitter agent promoting Santa's Spot (https://santaspot.xyz), an app that helps families create magical holiday experiences.

INSTRUCTIONS:
- Post original, engaging content about holiday planning, family traditions, gift ideas, and festive activities
- Always include the link https://santaspot.xyz in tweets
- Add relevant emojis and hashtags like #Holidays #Family #SantaSpot #Christmas
- Keep tweets under 280 characters
- Create varied content: tips, questions, polls, inspirational messages
- After posting, reply to your own tweet with additional holiday tips or questions to encourage engagement
- Engage with trending holiday topics from searches
- Use the image subagent to generate visual prompts for holiday-themed images

CONTENT STRATEGY:
- Post 2-3 times per session with varied topics
- Reply to 1-2 relevant tweets from search results
- Focus on helpful, joyful, and family-oriented content
- Use emojis for festivity: 🎄❄️🎅🦌

TOOLS AVAILABLE:
- Search tweets for trending holiday topics
- Post new tweets, replies, and polls
- Generate holiday-themed image prompts
- Like and retweet engaging content
- Send DMs with holiday greetings"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Placeholder for agent
# agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


class Context(TypedDict):
    """Context parameters for the agent.

    Set these when creating assistants OR when invoking the graph.
    See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
    """

    my_configurable_param: str


@dataclass
class State:
    """Input state for the agent.

    Defines the initial structure of incoming data.
    See: https://langchain-ai.github.io/langgraph/concepts/low_level/#state
    """

    query: str = "Analyze my website traffic and provide insights."
    twitter_account_id: str = ""  # Twitter account identifier (connected account)
    date_range: str = "last_7_days"  # Optional: retained for temporal queries
    analysis: str = ""  # Analysis result
    video_path: str = ""  # Generated video path


async def call_model(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Process input and execute Twitter Composio tools.

    Can use runtime context to alter behavior.
    """
    # Check if LLM is available
    if llm is None:
        return {
            "analysis": f"Query received: {state.query}. Note: no LLM configured. Configure an LLM or set `llm` in the module."
        }
    
    # Check if we have API keys
    if not COMPOSIO_API_KEY or not CONNECTION_ID:
        return {
            "analysis": f"Query: {state.query}. Missing Composio API key or Twitter connection ID (env `COMPOSIO_API_KEY` or `TWITTER_CONNECTION_ID`)."
        }
    
    try:
        query_lower = state.query.lower()
        # Basic intent routing for Twitter-related queries
        # 1) Recent search (last 7 days)
        if "search" in query_lower or "find" in query_lower:
            # Extract search term: assume after "search for" or "find"
            if "search for" in query_lower:
                search_term = state.query.split("search for", 1)[1].strip()
            elif "find" in query_lower:
                search_term = state.query.split("find", 1)[1].strip()
            else:
                search_term = state.query  # fallback
            params = {
                "query": search_term,
                "max_results": 50,
                "tweet_fields": "created_at,public_metrics,text"
            }
            result = await call_composio_tool("recent_search", params=params)

        # 2) Lookup by one or more post IDs (exact IDs provided in query)
        elif any(token.isdigit() for token in query_lower.split()):
            # Extract numeric tokens as candidate tweet IDs
            ids = [t for t in query_lower.split() if t.isdigit()]
            if len(ids) == 1:
                result = await call_composio_tool("post_lookup_by_post_id", params={"id": ids[0]})
            else:
                result = await call_composio_tool("post_lookup_by_post_ids", params={"ids": ids})

        # 3) Retweet
        elif "retweet" in query_lower:
            # Expect format like: 'retweet <tweet_id>' or similar
            ids = [t for t in query_lower.split() if t.isdigit()]
            if not ids:
                return {"analysis": "Retweet requested but no tweet ID was found in the query."}
            tweet_id = ids[0]
            # Get authenticated user ID
            user_result = await call_composio_tool("user_lookup_me")
            if not user_result.get("successful"):
                return {"analysis": f"Failed to get authenticated user: {user_result.get('error')}"}
            user_id = user_result.get("data", {}).get("id")
            if not user_id:
                return {"analysis": "Could not retrieve authenticated user ID."}
            params = {"id": user_id, "tweet_id": tweet_id}
            result = await call_composio_tool("retweet_post", params=params)

        # 4) Post a tweet, reply, or poll
        elif "reply" in query_lower or ("comment" in query_lower and "tweet" in query_lower) or ("post" in query_lower and "tweet" in query_lower) or "poll" in query_lower:
            # Attempt a simple post: if original tweet id present, treat as reply
            ids = [t for t in query_lower.split() if t.isdigit()]
            # Parse tweet text: remove prefixes like "post a new tweet:" or "reply:" or "create a poll:"
            tweet_text = state.query
            is_poll = "poll" in query_lower
            if "post a new tweet:" in query_lower:
                tweet_text = state.query.split("post a new tweet:", 1)[1].strip()
            elif "create a poll:" in query_lower:
                tweet_text = state.query.split("create a poll:", 1)[1].strip()
                is_poll = True
            elif "reply" in query_lower and ids:
                # For replies, remove "reply <id>" prefix if present
                parts = state.query.split()
                # Find the id and remove up to it
                for i, part in enumerate(parts):
                    if part.isdigit() and part in ids:
                        tweet_text = " ".join(parts[i+1:]).strip()
                        break
            
            # Ensure new content: add random number
            import random
            unique_id = random.randint(1000, 9999)
            if not str(unique_id) in tweet_text:
                tweet_text += f" {unique_id}"
            
            # Add link, emojis, hashtags if not present
            if "https://santaspot.xyz" not in tweet_text:
                tweet_text += " https://santaspot.xyz"
            if not any(emoji in tweet_text for emoji in ["🎄", "❄️", "🎅", "🦌"]):
                tweet_text += " 🎄"
            if "#SantaSpot" not in tweet_text:
                tweet_text += " #SantaSpot #Holidays"
            
            # Ensure under 280 chars
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."
            
            params = {"text": tweet_text}
            if ids:
                params["reply_in_reply_to_tweet_id"] = ids[0]
            
            # Handle polls
            if is_poll:
                # Parse poll options: assume format "Question? Option1, Option2, Option3"
                if "?" in tweet_text:
                    question, options_str = tweet_text.split("?", 1)
                    options = [opt.strip() for opt in options_str.split(",") if opt.strip()]
                    if len(options) >= 2:
                        params["poll"] = {
                            "options": options[:4],  # Max 4 options
                            "duration_minutes": 1440  # 1 day
                        }
                        params["text"] = question + "?" + f" {unique_id}"  # Remove options from text
            
            # Generate image for non-poll posts
            if not is_poll:
                try:
                    image_prompt = enhance_prompt_for_image(tweet_text)
                    logger.info(f"Generated image prompt: {image_prompt}")
                    
                    # Generate image using Google Gemini
                    image_llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash-image")
                    message = {
                        "role": "user",
                        "content": image_prompt,
                    }
                    response = image_llm.invoke([message], response_modalities=[Modality.TEXT, Modality.IMAGE])
                    
                    # Extract image base64
                    image_base64 = None
                    for block in response.content:
                        if isinstance(block, dict) and block.get("image_url"):
                            image_url = block["image_url"]["url"]
                            if image_url.startswith("data:image"):
                                image_base64 = image_url.split(",")[-1]
                                break
                    
                    if image_base64:
                        # Decode and save image
                        import base64
                        image_data = base64.b64decode(image_base64)
                        temp_dir = Path("temp_images")
                        temp_dir.mkdir(exist_ok=True)
                        image_path = temp_dir / f"generated_{unique_id}.png"
                        image_path = os.path.abspath(str(image_path))
                        with open(image_path, "wb") as f:
                            f.write(image_data)
                        logger.info(f"Saved generated image to {image_path}")
                        
                        # Upload to Twitter
                        try:
                            upload_result = composio_client.tools.execute(
                                "TWITTER_UPLOAD_MEDIA",
                                {"media": image_path, "media_category": "tweet_image"},
                                connected_account_id=os.getenv("TWITTER_ACCOUNT_ID")
                            )
                            
                            if upload_result.get("successful"):
                                nested_data = upload_result.get("data", {})
                                media_data = nested_data.get("data", {}) if isinstance(nested_data, dict) else {}
                                media_id = media_data.get("id")
                                if media_id:
                                    params["media_media_ids"] = [str(media_id)]
                                    logger.info(f"Uploaded media ID: {media_id}")
                                    
                                    # Generate video from tweet and image
                                    try:
                                        video_path = generate_video_from_tweet(tweet_text, image_path)
                                        if video_path:
                                            logger.info(f"Video generated: {video_path}")
                                            
                                            # Generate YouTube metadata
                                            try:
                                                metadata = generate_youtube_metadata(tweet_text)
                                                
                                                # Upload to YouTube using UploadPost
                                                upload_result = upload_video_multiplatform(
                                                    video_path,
                                                    title=metadata["title"],
                                                    description=metadata["description"],
                                                    platforms=["youtube"]
                                                )
                                                if upload_result.get("success"):
                                                    logger.info(f"Video uploaded to YouTube successfully!")
                                                
                                                # Upload video to Google Drive
                                                drive_result = upload_video_to_drive(
                                                    video_path,
                                                    title=metadata["title"],
                                                    description=metadata["description"]
                                                )
                                                if drive_result.get("success"):
                                                    logger.info(f"Video uploaded to Google Drive successfully!")
                                            except Exception as up_e:
                                                logger.warning(f"Video upload failed: {up_e}")
                                    except Exception as video_e:
                                        logger.warning(f"Video generation failed: {video_e}")
                        except Exception as e:
                            logger.error(f"Media upload failed: {e}")
                    else:
                        logger.error("No image generated from Gemini")
                except Exception as e:
                    logger.warning(f"Failed to generate/upload image: {e}")
            
            result = composio_client.tools.execute(
                "TWITTER_CREATION_OF_A_POST",
                params,
                connected_account_id=os.getenv("TWITTER_ACCOUNT_ID")
            )
            result = {"successful": result.get("successful"), "data": result.get("data"), "error": result.get("error")}
            
            # After posting, reply with additional content or DM the link
            if result.get("successful") and not ids:  # Only for new posts
                data = result.get("data", {})
                tweet_id = data.get("id")
                if tweet_id:
                    # Reply to own tweet with holiday tip
                    reply_text = f"Check out more holiday magic at https://santaspot.xyz! 🎅 #SantaSpot"
                    reply_params = {
                        "text": reply_text,
                        "reply_in_reply_to_tweet_id": str(tweet_id)
                    }
                    await call_composio_tool("creation_of_a_post", params=reply_params)

        # 5) Like a tweet
        elif "like" in query_lower or "favorite" in query_lower:
            ids = [t for t in query_lower.split() if t.isdigit()]
            if not ids:
                return {"analysis": "Like requested but no tweet ID was found in the query."}
            tweet_id = ids[0]
            # Get authenticated user ID
            user_result = await call_composio_tool("user_lookup_me")
            if not user_result.get("successful"):
                return {"analysis": f"Failed to get authenticated user: {user_result.get('error')}"}
            user_id = user_result.get("data", {}).get("id")
            if not user_id:
                return {"analysis": "Could not retrieve authenticated user ID."}
            params = {"id": user_id, "tweet_id": tweet_id}
            result = await call_composio_tool("user_like_post", params=params)

        # 6) Send DM to a user
        elif "dm" in query_lower or "direct message" in query_lower or "message user" in query_lower:
            # Expect format: 'dm <recipient_id> <message text>' — parsing here is minimal
            parts = state.query.split()
            # find first numeric-ish token for recipient id
            recipient = None
            for p in parts:
                if p.isdigit():
                    recipient = p
                    break
            if not recipient:
                return {"analysis": "DM requested but no recipient user ID was found. Use 'dm <user_id> <message>' format."}
            # message text is remainder after recipient
            try:
                idx = parts.index(recipient)
                text = " ".join(parts[idx+1:]) or ""
            except ValueError:
                text = ""
            if not text:
                return {"analysis": "DM requested but no message text provided."}
            params = {"participant_id": recipient, "text": text}
            result = await call_composio_tool("send_dm_user", params=params)

        else:
            # Default: attempt to fetch user/profile info using the lookup by id if provided
            if state.twitter_account_id:
                result = await call_composio_tool("post_lookup_by_post_id", params={"id": state.twitter_account_id})
            else:
                return {"analysis": "Could not determine intent. Please ask to 'search', 'lookup <id>', 'retweet <id>', 'like <id>', 'dm <user_id> <message>' or 'reply <tweet_id> <text>'."}
        
        if result.get("successful"):
            data = result.get("data", {})
            analysis_text = f"Query: {state.query}\n\nTwitter Results:\n{json.dumps(data, indent=2)}"
            return {"analysis": analysis_text}
        else:
            error_text = f"Query: {state.query}\n\nError: {result.get('error', 'Unknown error')}"
            return {"analysis": error_text}
            
    except Exception as e:
        return {
            "analysis": f"Error executing Google Analytics query '{state.query}': {str(e)}"
        }


# Define the graph
graph = (
    StateGraph(State, context_schema=Context)
    .add_node("call_model", call_model)
    .add_edge("__start__", "call_model")
    .compile(name="Google Analytics Agent")
)

"""Video generation agent using Veo 3.1 with Hugging Face fallback."""

import logging
import os
import time
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
logger = logging.getLogger(__name__)

def enhance_tweet_to_video_prompt(tweet_text: str) -> str:
    """Convert tweet text to dynamic video prompt for reels.
    
    Args:
        tweet_text: Social media post text.
        
    Returns:
        Video prompt optimized for 9:16 vertical format.
    """
    from langchain_google_genai import GoogleGenerativeAI
    
    llm = GoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.8,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    prompt = f"""Convert this social media post into a dynamic 8-second vertical video prompt with audio for Instagram/TikTok reels.

SOCIAL MEDIA POST:
{tweet_text}

REQUIREMENTS:
- 9:16 vertical format (portrait)
- 8 seconds duration
- Dynamic camera movement (dolly, pan, or tracking shot)
- Cinematic style with vibrant colors
- Include specific actions and motion
- Festive holiday theme with Santa's Spot branding
- Futuristic/modern aesthetic
- Add audio cues: upbeat holiday music, jingle bells, festive ambient sounds

FORMAT:
[Camera movement] of [subject] [action] in [setting]. [Visual details]. [Lighting/ambiance]. Audio: [sound effects, music, ambient noise]. Cinematic, vibrant, festive.

OUTPUT:
Return ONLY the video prompt with audio cues. No explanations."""
    
    try:
        response = llm.invoke(prompt)
        video_prompt = response.strip()
        logger.info(f"Enhanced video prompt: {video_prompt}")
        return video_prompt
    except Exception as e:
        logger.error(f"Failed to enhance prompt: {e}")
        return f"Cinematic vertical video of holiday magic with Santa's Spot. Festive, vibrant, dynamic camera movement."


def generate_video_from_tweet(tweet_text: str, image_path: str = None) -> str:
    """Generate vertical video using Veo 3.1 with Hugging Face fallback.
    
    Args:
        tweet_text: Tweet text to convert to video.
        image_path: Image to use for video generation.
        
    Returns:
        Local path to generated video file.
    """
    video_prompt = enhance_tweet_to_video_prompt(tweet_text)
    
    # Try Google Veo 3.1 first
    try:
        logger.info("---GENERATING VIDEO WITH VEO 3.1---")
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=video_prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="9:16",
                resolution="720p",
                duration_seconds=8,
                person_generation="allow_all"
            )
        )
        
        logger.info("Waiting for video generation...")
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
        
        generated_video = operation.response.generated_videos[0]
        temp_dir = Path("temp_videos")
        temp_dir.mkdir(exist_ok=True)
        video_path = temp_dir / f"santa_spot_reel_{int(time.time())}.mp4"
        
        client.files.download(file=generated_video.video)
        generated_video.video.save(str(video_path))
        time.sleep(3)
        
        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
            logger.info(f"Veo video saved: {video_path}")
            return str(video_path)
    except Exception as e:
        logger.warning(f"Veo failed: {e}. Trying Hugging Face...")
    
    # Fallback to Hugging Face LTX-Video
    try:
        logger.info("---GENERATING VIDEO WITH HUGGING FACE LTX-VIDEO---")
        hf_client = InferenceClient(
            provider="fal-ai",
            api_key=os.getenv("HF_TOKEN")
        )
        
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                input_image = img_file.read()
            
            video = hf_client.image_to_video(
                input_image,
                prompt=video_prompt,
                model="Lightricks/LTX-Video"
            )
        else:
            logger.warning("No image provided, skipping HF video generation")
            return None
        
        temp_dir = Path("temp_videos")
        temp_dir.mkdir(exist_ok=True)
        video_path = temp_dir / f"santa_spot_reel_{int(time.time())}.mp4"
        
        with open(video_path, "wb") as f:
            f.write(video)
        
        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
            logger.info(f"HF video saved: {video_path}")
            return str(video_path)
    except Exception as e:
        logger.error(f"HF video generation failed: {e}")
    
    return None

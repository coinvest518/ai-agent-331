"""Image Prompt Enhancement Sub-Agent.

Converts social media text into clean, visual prompts for AI image generation.
"""

import logging
import os
import re

from langchain_google_genai import GoogleGenerativeAI
from langsmith import traceable

logger = logging.getLogger(__name__)


@traceable(name="enhance_image_prompt")
def enhance_prompt_for_image(text: str, product_name: str = None, product_price: str = None) -> str:
    """Convert social media text into a clean visual prompt for image generation with a selling focus.

    Args:
        text: Social media post text with hashtags and formatting.
        product_name: Optional name of the product to include in the prompt.
        product_price: Optional price of the product to include in the prompt.

    Returns:
        Clean, descriptive image prompt optimized for Google Gemini AI image generation.
    """
    logger.info("Enhancing image prompt...")

    llm = GoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    selling_focus = ""
    if product_name:
        selling_focus += f" Highlight the product '{product_name}'."
    if product_price:
        selling_focus += f" Include the price '{product_price}'."

    prompt = f"""
Convert this social media post into a visual art prompt for AI image generation focused on AI tools, credit repair, and automation.

SOCIAL MEDIA TEXT:
{text}

REQUIREMENTS:
- Remove ALL hashtags
- Remove ALL special characters (* # @ etc)
- Remove ALL markdown formatting
- Extract core visual theme related to AI, credit repair, automation, or business growth
- Add modern tech imagery: AI interfaces, credit score dashboards, automation workflows, digital tools, futuristic tech
- Style: modern, professional, tech-forward, clean, inspiring
- Include visual elements: credit score graphs, AI robots, automation symbols, success imagery
- Maximum 200 characters
{selling_focus}

OUTPUT:
Return ONLY the clean image prompt. No explanations.
"""

    try:
        response = llm.invoke(prompt)
        visual_prompt = response.strip()

        # Additional cleanup
        visual_prompt = re.sub(r"[*#@\[\]{}()\'\"\\]", "", visual_prompt)
        visual_prompt = re.sub(r"\s+", " ", visual_prompt).strip()

        logger.info("Enhanced prompt: %s", visual_prompt)
        return visual_prompt

    except Exception as e:
        logger.exception("Error enhancing prompt: %s", e)
        # Fallback: basic cleanup
        fallback = re.sub(r"[*#@\[\]{}()\'\"\\]", "", text)
        fallback = re.sub(r"\s+", " ", fallback).strip()
        fallback_prompt = f"Modern AI and credit repair tech image: {fallback[:150]}"
        if product_name:
            fallback_prompt += f" Featuring '{product_name}'."
        if product_price:
            fallback_prompt += f" Price: {product_price}."
        return fallback_prompt
# Santa's Spot AI Agent

Autonomous AI agent that generates and posts holiday-themed content to Twitter and YouTube. Built with LangGraph, Composio, and Google AI.

## Features

- **Autonomous Tweet Generation**: Creates engaging holiday tweets with emojis, hashtags, and links
- **AI Image Generation**: Generates custom images using Gemini 2.5 Flash
- **AI Video Generation**: Creates 8-second vertical reels (9:16) using Veo 3.1 with audio cues
- **Twitter Integration**: Posts tweets with images via Composio
- **YouTube Upload**: Uploads videos with AI-generated titles and descriptions via UploadPost API
- **YouTube Analytics**: Retrieves channel statistics and activities
- **Automated Scheduling**: Runs every 1 hour 17 minutes for continuous posting

## Getting Started

1. Install dependencies:

```bash
pip install -e .
```

2. Set up environment variables in `.env`:

```env
COMPOSIO_API_KEY=your_composio_api_key
TWITTER_ACCOUNT_ID=your_twitter_account_id
COMPOSIO_TOOLKIT_VERSION_TWITTER=20251024_00
GOOGLE_API_KEY=your_google_ai_api_key
UPLOADPOST_API_KEY=your_uploadpost_api_key
UPLOADPOST_USER=your_uploadpost_username
YOUTUBE_CHANNEL_HANDLE=@YourChannel
```

3. Run the agent:

```bash
# Single run
python test_main_graph.py

# Autonomous scheduling
python scheduler.py
```

## Architecture

- **LangGraph**: Orchestrates multi-step workflow
- **Composio**: Twitter and YouTube API integration
- **Google AI (Gemini 2.5 Flash)**: Image generation and LLM
- **Google Veo 3.1**: Text-to-video generation with audio
- **UploadPost API**: Multi-platform video distribution

## Workflow

1. Generate holiday-themed tweet text
2. Create AI image from tweet content
3. Post tweet with image to Twitter
4. Generate video prompt with audio cues
5. Create 8-second vertical video using Veo 3.1
6. Generate YouTube title and description
7. Upload video to YouTube


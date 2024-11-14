# AxoGPT Discord Bot Setup Guide

## Prerequisites
- Python 3.8 or higher
- A Discord account
- A Google Cloud account (for Gemini API)

## Step 1: Create Discord Bot
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **"New Application"** and give it a name.
3. Go to the **"Bot"** section.
4. Click **"Add Bot"**.
5. Under **Privileged Gateway Intents**, enable the following:
   - **Message Content Intent**
   - **Server Members Intent**
6. Save changes.
7. Copy the bot token (you'll need this later).

## Step 2: Get API Key
### Google Gemini API Key:
1. Go to [Google AI Studio](https://ai.google.com).
2. Create a new API key.
3. Copy the key.

## Step 3: Install Required Packages
Run the following commands to install the necessary packages:
```bash
pip install discord.py
pip install google-generativeai
pip install python-dotenv
```

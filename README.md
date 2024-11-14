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

## Step 4: Set Up Environment Variables
Create a file named .env in your project directory:

### Step 5: Invite Bot to Server
1. Go back to Discord Developer Portal
2. Select your application
3. Go to OAuth2 → URL Generator
4. Select the following scopes:
   - bot
applications.commands
5. Select bot permissions:
   - Send Messages
   - Read Messages/View Channels
   - Send Messages in Threads
Copy the generated URL and open it in a browser
6. Select your server and authorize the bot

## Step 6: Run the Bot
1. Save the bot code as discordai.py
2. Run the bot:
Bash
```bash
python discordai.py
```

Once the bot is running, you can interact with it using:
```bash
!help - Show available commands
!joke - Get a random joke
!fact - Get a random fact
Mention the bot using @AxoGPT
Include "axogpt" in your message
```
## Troubleshooting
### Common Issues:

#### ModuleNotFoundError:
- Make sure you've installed all required packages
- Run `pip install -r requirements.txt` if using a requirements file

#### Invalid Token:
- Double-check your `.env` file
- Ensure there are no spaces around the `=` signs
- Make sure the token values are correct

#### Permission Issues:
- Check if the bot has the correct permissions in your Discord server
- Verify all required intents are enabled in the Discord Developer Portal

#### API Key Issues:
- Verify API key is valid
- Check if you have sufficient quota/credits

### Support
- Discord Developer Documentation: [discord.dev](https://discord.dev)
- Google AI Documentation: [Google AI docs](https://ai.google.dev/docs)

fin

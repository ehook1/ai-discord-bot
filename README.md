AxoGPT Discord Bot Setup Guide
Prerequisites
Python 3.8 or higher
A Discord account
A Google Cloud account (for Gemini API)
Step 1: Create Discord Bot
Go to Discord Developer Portal
Click "New Application" and give it a name
3. Go to the "Bot" section
Click "Add Bot"
Under Privileged Gateway Intents, enable:
Message Content Intent
Server Members Intent
Save changes
Copy the bot token (you'll need this later)
Step 2: Get API Key
Google Gemini API Key:
Go to Google AI Studio
Create a new API key
Copy the key
Step 3: Install Required Packages
pip install discord.py
pip install google-generativeai
pip install python-dotenv
Step 4: Set Up Environment Variables
Create a file named .env in your project directory:
Step 5: Invite Bot to Server
Go back to Discord Developer Portal
Select your application
Go to OAuth2 → URL Generator
Select the following scopes:
bot
applications.commands
Select bot permissions:
Send Messages
Read Messages/View Channels
Send Messages in Threads
Copy the generated URL and open it in a browser
Select your server and authorize the bot
Step 6: Run the Bot
Save the bot code as discordai.py
Run the bot:
Bash
Usage
Once the bot is running, you can interact with it using:
!help - Show available commands
!joke - Get a random joke
!fact - Get a random fact
Mention the bot using @AxoGPT
Include "axogpt" in your message
Troubleshooting
Common Issues:
ModuleNotFoundError:
Make sure you've installed all required packages
Run pip install -r requirements.txt if using a requirements file
Invalid Token:
Double-check your .env file
Ensure there are no spaces around the = signs
Make sure the token values are correct
Permission Issues:
Check if the bot has the correct permissions in your Discord server
Verify all required intents are enabled in the Discord Developer Portal
API Key Issues:
Verify API key is valid
Check if you have sufficient quota/credits
Support
Discord Developer Documentation: discord.dev
Google AI Documentation: Google AI docs

fin

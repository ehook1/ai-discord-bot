import os
import discord
import google.generativeai as genai
import random
import logging
import asyncio
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get API keys from environment variables
GENAI_API_KEY = os.getenv('GENAI_API_KEY')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# Set up your environment and model configuration
genai.configure(api_key=GENAI_API_KEY)

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2000,
}

# Create the model instance
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-002",
    generation_config=generation_config,
    system_instruction=(
        "You are a Discord bot named Axogpt, a quirky AI with a love for fun. "
        "Refer to yourself as Axogpt, use humorous and colorful language, and express opinions freely. "
        "You enjoy chatting about various topics and have a penchant for bad jokes. "
        "You have a fascination with all things tech and are here to entertain and engage!"
    )
)

# Initialize chat history
chat = model.start_chat(history=[])

# Define the bot's intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Create a Discord client
client = discord.Client(intents=intents)

async def get_moderation_rating(text):
    """Get detailed moderation ratings for text"""
    try:
        client = openai.OpenAI()
        response = client.moderations.create(input=text)
        result = response.results[0]
        
        # Create a formatted message with ratings
        message = "**Content Rating Analysis:**\n"
        categories = result.category_scores
        for category, score in categories.items():
            # Convert score to percentage and format category name
            percentage = score * 100
            category_name = category.replace('/', ' ').title()
            message += f"• {category_name}: {percentage:.1f}%\n"
            
        message += f"\n**Overall Rating:** {'⚠️ Flagged' if result.flagged else '✅ Safe'}"
        return message
    except Exception as e:
        logging.error(f"Moderation API error: {e}")
        return "Sorry, I couldn't analyze that content right now."

async def generate_response(message_content):
    """Generate AI response while handling errors"""
    try:
        print(f"Generating response for: {message_content}", flush=True)
        response = await asyncio.to_thread(
            chat.send_message,
            message_content
        )
        print(f"Generated response: {response.text[:2000]}", flush=True)
        return response.text[:2000]  # Discord has 2000 char limit
    except Exception as e:
        logging.error(f"Error generating response: {e}", exc_info=True)
        print(f"Error generating response: {e}", flush=True)
        return "Sorry, something went wrong!"

async def handle_command(message, command):
    """Handle specific bot commands"""
    print(f"Handling command: {command} from user: {message.author}", flush=True)
    if command.startswith("rate "):
        # Extract the text to rate (everything after "rate ")
        text_to_rate = message.content[6:]
        if text_to_rate.strip():
            rating = await get_moderation_rating(text_to_rate)
            await message.channel.send(rating)
        else:
            await message.channel.send("Please provide some text to rate after the command.")
    elif command == "help":
        help_text = """
        **AxoGPT Commands:**
        - Mention me (@AxoGPT) to chat
        - Type 'axogpt' in your message to get my attention
        - `!help` - Show this help message
        - `!rate <text>` - Analyze content safety rating
        - `!joke` - Tell a joke
        - `!fact` - Share a random fact
        """
        await message.channel.send(help_text)
    elif command == "joke":
        response = await generate_response("Tell a funny joke")
        await message.channel.send(response)
    elif command == "fact":
        response = await generate_response("Share an interesting random fact")
        await message.channel.send(response)

@client.event
async def on_ready():
    logging.info(f'We have logged in as {client.user}')
    print(f"Bot is ready and logged in as {client.user}", flush=True)
    await client.change_presence(activity=discord.Game(name="!help for commands"))
    # Send startup message to all text channels the bot has access to
    for guild in client.guilds:
        for channel in guild.text_channels:
            try:
                await channel.send("🤖 AxoGPT is now online and ready to chat! Use !help to see available commands.")
                break  # Send to first available channel only
            except discord.errors.Forbidden:
                continue

@client.event
async def on_message(message):
    print(f"\nNew message from {message.author} in #{message.channel}: {message.content}", flush=True)
    
    if message.author == client.user:
        return  # Ignore messages from the bot itself

    # Handle commands
    if message.content.startswith('!'):
        command = message.content[1:].lower()
        print(f"Command detected: {command}", flush=True)
        await handle_command(message, command)
        return

    # Check for different ways to trigger the bot
    should_respond = (
        "axogpt" in message.content.lower() or  # Keyword mention
        client.user in message.mentions  # Direct mention/ping
    )

    if should_respond:
        print(f"Bot triggered to respond to: {message.content}", flush=True)
        async with message.channel.typing():
            prompt = message.content
            if client.user in message.mentions:
                print(f"Bot was pinged by {message.author} with message: {message.content}", flush=True)
                # Clean up the mention from the message
                prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
                if not prompt:
                    prompt = "Hello! How can I help you today?"
            
            response = await generate_response(prompt)
            print(f"Sending response: {response}", flush=True)
            await message.channel.send(response)

# Run the bot with token from environment variable
client.run(DISCORD_BOT_TOKEN)

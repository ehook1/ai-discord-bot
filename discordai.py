import os
import discord
import google.generativeai as genai
import random
import logging
import asyncio
from dotenv import load_dotenv
import openai
import sys
import time
from datetime import datetime
from gooey import Gooey, GooeyParser

# Test mode flag
TEST_MODE = False  # Set to True to test error handling and downtime detection

@Gooey(
    program_name="AxoGPT Discord Bot",
    default_size=(1000, 800),
    navigation='TABBED',
    show_success_modal=False,
    richtext_controls=True,
    program_description="A customizable Discord bot powered by Google's Gemini AI",
    header_bg_color='#2c2f33',
    body_bg_color='#36393f',
    terminal_panel_color='#36393f',
    terminal_font_color='#ffffff',
    header_height=80,
    menu=[{
        'name': 'File',
        'items': [{
            'type': 'AboutDialog',
            'menuTitle': 'About',
            'name': 'AxoGPT Bot',
            'description': 'A Discord bot powered by Gemini AI',
            'version': '1.0.0'
        }]
    }]
)
def main():
    parser = GooeyParser(description="Configure your AxoGPT Discord Bot")
    
    # Organize settings into meaningful tabs
    general_group = parser.add_argument_group(
        'General Settings',
        'Basic configuration options for the bot'
    )
    general_group.add_argument(
        '--trigger_word',
        default='axogpt',
        help='Word to trigger the bot (default: axogpt)',
        gooey_options={
            'validator': {
                'test': 'len(user_input) > 0',
                'message': 'Trigger word cannot be empty'
            }
        }
    )
    general_group.add_argument(
        '--log_file',
        default='ai-discord-bot/bot_errors.log',
        help='Path to log file',
        widget='FileChooser'
    )
    general_group.add_argument(
        '--test_mode',
        action='store_true',
        help='Enable test mode for debugging',
        gooey_options={'initial_value': False}
    )

    ai_group = parser.add_argument_group(
        'AI Configuration',
        'Settings for the AI personality and behavior'
    )
    ai_group.add_argument(
        '--system_prompt',
        default=(
            "You are a Discord bot named Axogpt, a quirky AI with a love for fun. "
            "Refer to yourself as Axogpt, use humorous and colorful language, and express opinions freely. "
            "You enjoy chatting about various topics and have a penchant for bad jokes. "
            "You have a fascination with all things tech and are here to entertain and engage!"
        ),
        widget='Textarea',
        help='Define the AI\'s personality and behavior',
        gooey_options={
            'height': 200,
            'placeholder': 'Enter the system prompt that defines the AI\'s personality...'
        }
    )
    ai_group.add_argument(
        '--temperature',
        default=20,
        widget='Slider',
        help='AI creativity level (1 = focused, 20 = creative)',
        gooey_options={
            'min': 1,
            'max': 20,
            'increment': 1
        }
    )

    api_group = parser.add_argument_group(
        'API Configuration',
        'API keys and authentication settings'
    )
    api_group.add_argument(
        '--genai_key',
        widget='PasswordField',
        help='Google GenerativeAI API Key'
    )
    api_group.add_argument(
        '--discord_token',
        widget='PasswordField',
        help='Discord Bot Token'
    )
    api_group.add_argument(
        '--openai_key',
        widget='PasswordField',
        help='OpenAI API Key (for moderation)'
    )

    advanced_group = parser.add_argument_group(
        'Advanced Settings',
        'Additional configuration options for advanced users'
    )
    advanced_group.add_argument(
        '--max_reconnect_attempts',
        default=5,
        help='Maximum number of reconnection attempts',
        gooey_options={
            'validator': {
                'test': 'user_input.isdigit() and int(user_input) > 0',
                'message': 'Please enter a positive number'
            }
        }
    )
    advanced_group.add_argument(
        '--max_response_length',
        default=2000,
        help='Maximum length of bot responses',
        gooey_options={
            'validator': {
                'test': 'user_input.isdigit() and int(user_input) > 0',
                'message': 'Please enter a positive number'
            }
        }
    )

    args = parser.parse_args()
    
    # Update your generation config with the GUI temperature
    generation_config = {
        "temperature": float(args.temperature) / 10,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    # Update global variables based on GUI input
    global TEST_MODE
    TEST_MODE = args.test_mode

    # Load environment variables
    load_dotenv()

    # Set up logging
    log_file = args.log_file
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a'),
            logging.StreamHandler()
        ]
    )
    logging.info("Starting bot and logging to: " + os.path.abspath(log_file))
    if TEST_MODE:
        logging.warning("Running in TEST MODE - Error handling and downtime detection will be tested")

    # Get API keys from GUI or environment variables
    GENAI_API_KEY = args.genai_key or os.getenv('GENAI_API_KEY')
    DISCORD_BOT_TOKEN = args.discord_token or os.getenv('DISCORD_BOT_TOKEN')
    OPENAI_API_KEY = args.openai_key or os.getenv('OPENAI_API_KEY')

    # Set up your environment and model configuration
    genai.configure(api_key=GENAI_API_KEY)

    # Create the model instance
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-002",
        generation_config=generation_config,
        system_instruction=args.system_prompt
    )

    # Initialize chat history
    chat = model.start_chat(history=[])

    # Define the bot's intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True

    # Create a Discord client
    client = discord.Client(intents=intents)

    # Track uptime and downtime
    start_time = datetime.now()
    total_downtime = 0
    last_disconnect = None

    # Add heartbeat check
    async def heartbeat():
        global total_downtime, last_disconnect
        test_failure_count = 0
        while True:
            await asyncio.sleep(60)  # Check every minute
            try:
                # In test mode, simulate connection issues every 3rd check
                if TEST_MODE and test_failure_count % 3 == 0:
                    raise Exception("Simulated connection failure for testing")
                    
                if client.ws is not None and client.is_ready():
                    logging.info("Heartbeat check - Bot is connected")
                    if last_disconnect:
                        downtime = (datetime.now() - last_disconnect).total_seconds()
                        total_downtime += downtime
                        last_disconnect = None
                else:
                    logging.warning("Heartbeat check - Bot connection issues detected")
                    if not last_disconnect:
                        last_disconnect = datetime.now()
                    await client.close()
            except Exception as e:
                logging.error(f"Heartbeat check failed: {e}")
                if not last_disconnect:
                    last_disconnect = datetime.now()
                await client.close()
                
            if TEST_MODE:
                test_failure_count += 1

    async def get_moderation_rating(text):
        """Get detailed moderation ratings for text"""
        try:
            # In test mode, randomly simulate API errors
            if TEST_MODE and random.random() < 0.2:  # 20% chance of error
                raise Exception("Simulated moderation API error for testing")
                
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
            # In test mode, randomly simulate API errors
            if TEST_MODE and random.random() < 0.2:  # 20% chance of error
                raise Exception("Simulated API error for testing")
                
            logging.info(f"Generating response for message")
            response = await asyncio.to_thread(
                chat.send_message,
                message_content
            )
            logging.info("Response generated successfully")
            return response.text[:2000]  # Discord has 2000 char limit
        except Exception as e:
            logging.error(f"Error generating response: {e}", exc_info=True)
            return "Sorry, something went wrong!"

    async def handle_command(message, command):
        """Handle specific bot commands"""
        logging.info(f"Handling command: {command}")
        
        # In test mode, randomly simulate command failures
        if TEST_MODE and random.random() < 0.2:  # 20% chance of error
            logging.error("Simulated command failure for testing")
            await message.channel.send("Sorry, that command failed! (Test Mode)")
            return
            
        if command.startswith("rate "):
            # Extract the text to rate (everything after "rate ")
            text_to_rate = message.content[6:]
            if text_to_rate.strip():
                rating = await get_moderation_rating(text_to_rate)
                await message.channel.send(rating)
            else:
                await message.channel.send("Please provide some text to rate after the command.")
        elif command == "help":
            # In test mode, randomly show test version of help
            if TEST_MODE and random.random() < 0.2:
                help_text = "**TEST MODE HELP**\nAll commands may randomly fail for testing purposes!"
            else:
                help_text = """
                **AxoGPT Commands:**
                - Mention me (@AxoGPT) to chat
                - Type 'axogpt' in your message to get my attention
                - `!help` - Show this help message
                - `!rate <text>` - Analyze content safety rating
                - `!joke` - Tell a joke
                - `!fact` - Share a random fact
                - `!uptime` - Check bot uptime and downtime
                
                Note: The shutdown command has been disabled for security reasons.
                """
            await message.channel.send(help_text)
        elif command == "joke":
            if TEST_MODE and random.random() < 0.2:
                await message.channel.send("Error: Joke module malfunctioned! (Test Mode)")
            else:
                response = await generate_response("Tell a funny joke")
                await message.channel.send(response)
        elif command == "fact":
            if TEST_MODE and random.random() < 0.2:
                await message.channel.send("Error: Fact database unavailable! (Test Mode)")
            else:
                response = await generate_response("Share an interesting random fact")
                await message.channel.send(response)
        elif command == "uptime":
            if TEST_MODE and random.random() < 0.2:
                await message.channel.send("Error: Could not calculate uptime! (Test Mode)")
            else:
                uptime = datetime.now() - start_time
                uptime_str = str(uptime).split('.')[0]  # Remove microseconds
                downtime_minutes = total_downtime / 60
                await message.channel.send(f"🕒 **Bot Status**\nUptime: {uptime_str}\nTotal Downtime: {downtime_minutes:.2f} minutes")
        # NOT FOR PRODUCTION USE #
        elif command == "shutdown":
            if TEST_MODE and random.random() < 0.2:
                await message.channel.send("Error: Shutdown failed! (Test Mode)")
            else:
                await message.channel.send("Shutting down... Goodbye! 👋")
                await client.close()
                sys.exit(0)
        elif command == "restart":
            if TEST_MODE and random.random() < 0.2:
                await message.channel.send("Error: Restart failed! (Test Mode)")
            else:
                logging.info("Restart command received")
            
    @client.event
    async def on_ready():
        logging.info('Bot is ready and logged in')
        await client.change_presence(activity=discord.Game(name="!help for commands"))
        # Start heartbeat check
        client.loop.create_task(heartbeat())
        # Send startup message to all text channels the bot has access to
        for guild in client.guilds:
            for channel in guild.text_channels:
                try:
                    if TEST_MODE and random.random() < 0.2:
                        await channel.send("🤖 AxoGPT Test Mode Active - Expect random failures!")
                    else:
                        await channel.send("🤖 AxoGPT is now online and ready to chat! Use !help to see available commands.")
                    break  # Send to first available channel only
                except discord.errors.Forbidden:
                    continue

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return  # Ignore messages from the bot itself

        # Check for shutdown command
        if message.content.lower() == "axogpt shut down":
            if TEST_MODE and random.random() < 0.2:
                logging.info("Simulated shutdown failure")
                await message.channel.send("Error: Shutdown failed! (Test Mode)")
                return
                
            logging.info("Shutdown command received")
            await message.channel.send("Shutting down... Goodbye! 👋")
            await client.close()
            sys.exit(0)

        # Handle commands
        if message.content.startswith('!'):
            command = message.content[1:].lower()
            logging.info(f"Command received: {command}")
            await handle_command(message, command)
            return

        # Check for different ways to trigger the bot
        should_respond = (
            "axogpt" in message.content.lower() or  # Keyword mention
            client.user in message.mentions  # Direct mention/ping
        )

        if should_respond:
            logging.info("Bot triggered to respond")
            async with message.channel.typing():
                prompt = message.content
                if client.user in message.mentions:
                    logging.info("Bot was mentioned")
                    # Clean up the mention from the message
                    prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
                    if not prompt:
                        prompt = "Hello! How can I help you today?"
                
                response = await generate_response(prompt)
                logging.info("Response sent")
                await message.channel.send(response)

    # Add this near the top of your file with other global variables
    MAX_RECONNECT_ATTEMPTS = args.max_reconnect_attempts
    reconnect_attempts = 0

    # Modify the main loop at the bottom of the file
    while True:
        try:
            reconnect_attempts = 0  # Reset counter on successful connection
            client.run(DISCORD_BOT_TOKEN)
        except Exception as e:
            reconnect_attempts += 1
            logging.error(f"Bot disconnected with error: {e}")
            if reconnect_attempts >= MAX_RECONNECT_ATTEMPTS:
                logging.critical(f"Failed to reconnect after {MAX_RECONNECT_ATTEMPTS} attempts. Shutting down.")
                sys.exit(1)
            wait_time = min(5 * reconnect_attempts, 60)  # Exponential backoff, max 60 seconds
            logging.info(f"Reconnecting in {wait_time} seconds... (Attempt {reconnect_attempts}/{MAX_RECONNECT_ATTEMPTS})")
            time.sleep(wait_time)

if __name__ == '__main__':
    main()

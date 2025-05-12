import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keepalive import keep_alive
from pymongo import MongoClient

load_dotenv()
TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")  # Ensure you have MONGO_URI in your .env file

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    "d!"), intents=intents, help_command=None)

# Connect to MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['discord_economy']  # Use the database name explicitly


async def get_prefix(bot, message):
    try:
        if not message.guild:
            return "?"

        # Get prefix from MongoDB
        prefix_data = db.prefixes.find_one({"guild_id": str(message.guild.id)})
        return prefix_data["prefix"] if prefix_data else "d!"
    except Exception:
        return "d!"  # Default fallback


bot.command_prefix = get_prefix


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Load all extensions from /commands
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"commands.{filename[:-3]}")
                print(f"Loaded {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

    # Sync slash commands only once
    try:
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")





keep_alive()
bot.run(TOKEN)
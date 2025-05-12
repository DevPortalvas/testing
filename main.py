import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keepalive import keep_alive

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)

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

@bot.command()
async def clearslash(ctx):
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    await ctx.send("Cleared global slash commands.")


keep_alive()
bot.run(TOKEN)

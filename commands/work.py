import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os

DATA_FILE = "data.json"

def get_balance(user_id):
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        if str(user_id) not in data:
            data[str(user_id)] = {"pocket": 0, "bank": 0}
            with open(DATA_FILE, "w") as f:
                json.dump(data, f)

    return data[str(user_id)]

def update_balance(user_id, amount):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if str(user_id) not in data:
        data[str(user_id)] = {"pocket": 0, "bank": 0}
    data[str(user_id)]["pocket"] += amount

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Prefix command
    @commands.command(help="Work for money, cooldown = 10 minutes.")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def work(self, ctx):
        await self.do_work_prefix(ctx)

    # Slash command
    @app_commands.command(name="work", description="Work for money (10 min cooldown)")
    @app_commands.checks.cooldown(1, 600)
    async def work_slash(self, interaction: discord.Interaction):
        await self.do_work_slash(interaction)

    # Separate logic for prefix
    async def do_work_prefix(self, ctx):
        user_id = ctx.author.id
        earnings = random.randint(1000, 5000)
        update_balance(user_id, earnings)
        msg = self.get_random_message(earnings)
        embed = discord.Embed(title="You finally did a job pig!", description=msg, color=discord.Color.orange())
        await ctx.send(embed=embed)

    # Separate logic for slash
    async def do_work_slash(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        earnings = random.randint(1000, 5000)
        update_balance(user_id, earnings)
        msg = self.get_random_message(earnings)
        embed = discord.Embed(title="You finally did a job pig!", description=msg, color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)

    def get_random_message(self, earnings):
        messages = [
            f"You mowed a lawn and earned ${earnings}!",
            f"You wrote some code and got paid ${earnings}!",
            f"You delivered food and received ${earnings}!",
            f"You danced in the street and got tipped ${earnings}!",
            f"You robbed a lemonade stand and ran with ${earnings}!",
            f"You walked someone's dog and earned ${earnings}!",
            f"You won a small bet and gained ${earnings}!",
            f"You found a wallet and kept ${earnings}!",
            f"You made a meme and it went viral — you got ${earnings}!",
            f"You sold some art and made ${earnings}!"
        ]
        return random.choice(messages)

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="You're tired!",
                description=f"Come back in {int(error.retry_after // 60)} minutes.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @work_slash.error
    async def work_slash_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title="You're tired!",
                description=f"Come back in {int(error.retry_after // 60)} minutes.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Work(bot))

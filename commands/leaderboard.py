import discord  
from discord.ext import commands  
from discord import app_commands  
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

class Leaderboard(commands.Cog):  
    def __init__(self, bot):  
        self.bot = bot  
  
    @commands.command(help="Ranks users based on their networth (only top 10.)")  
    async def leaderboard(self, ctx):  
        await self._show_leaderboard(ctx)  
  
    @app_commands.command(name="leaderboard", description="Ranks users based on their networth (only top 10.)")  
    async def leaderboard_slash(self, interaction: discord.Interaction):  
        await self._show_leaderboard(interaction)  
  
    async def _show_leaderboard(self, ctx_or_interaction):  
        with open(DATA_FILE, "r") as f:  
            data = json.load(f)  
        
        # Calculate total money for each user
        user_totals = []
        for user_id, balances in data.items():
            total = balances["pocket"] + balances["bank"]
            user_totals.append((user_id, total))
        
        # Sort by total money, descending
        user_totals.sort(key=lambda x: x[1], reverse=True)
        
        embed = discord.Embed(
            title="🏆 Richest Users",
            color=discord.Color.gold()
        )
        
        # Get top 10 users
        for i, (user_id, total) in enumerate(user_totals[:10], 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                embed.add_field(
                    name=f"{i}. {user.name}",
                    value=f"${total:,}",
                    inline=False
                )
            except:
                continue
        
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

async def setup(bot):  
    await bot.add_cog(Leaderboard(bot))
  

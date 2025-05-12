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
  
class Balance(commands.Cog):  
    def __init__(self, bot):  
        self.bot = bot  
  
    @commands.command(help="Check your current money in your pocket and your bank.")  
    async def balance(self, ctx, member: discord.Member=None):  
        await self._check_balance(ctx, member)  
  
    @app_commands.command(name="balance", description="Check your current money in your pocket and your bank")  
    async def balance_slash(self, interaction: discord.Interaction, member: discord.Member=None):  
        await self._check_balance(interaction, member)  
  
    async def _check_balance(self, ctx_or_interaction, member=None):  
        user = member or (ctx_or_interaction.author if hasattr(ctx_or_interaction, 'author') else ctx_or_interaction.user)  
        bal = get_balance(user.id)  
  
        embed = discord.Embed(title=f"{user.name}'s Balance", color=discord.Color.green())  
        embed.add_field(name="Pocket", value=f"${bal['pocket']}", inline=True)  
        embed.add_field(name="Bank", value=f"${bal['bank']}", inline=True)  
  
        if isinstance(ctx_or_interaction, discord.Interaction):  
            await ctx_or_interaction.response.send_message(embed=embed)  
        else:  
            await ctx_or_interaction.send(embed=embed)  
  
async def setup(bot):  
    await bot.add_cog(Balance(bot))
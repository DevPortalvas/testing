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
  
class Slut(commands.Cog):  
    def __init__(self, bot):  
        self.bot = bot  
  
    @commands.command(name="slut", help="Do dirty stuff for money;)")  
    @commands.cooldown(1, 600, commands.BucketType.user)  
    async def work(self, ctx):  
        await self._do_slut(ctx)  
  
    @app_commands.command(name="slut", description="Do dirty stuff for money;)")  
    @app_commands.checks.cooldown(1, 600)  
    async def slut_slash(self, interaction: discord.Interaction):  
        await self._do_slut(interaction)  
  
    async def _do_slut(self, ctx_or_interaction):  
        user_id = ctx_or_interaction.user.id if isinstance(ctx_or_interaction, discord.Interaction) else ctx_or_interaction.author.id  
        earnings = random.randint(3000, 6000)  
  
        messages = [  
            f"You sucked someone off, you made ${earnings}!",  
            f"your ass is cooked now but at least you made ${earnings}!",  
            f"sold feet picks for ${earnings}!",  
            f"You danced in a strip club and made from the tips ${earnings}!",  
            f"You made an only fans and you got ${earnings} somehow",  
            f"You acted as someones dog and made ${earnings}!",  
            f"You followed this desperate mom into the hotel she suggested and made ${earnings}!",  
            f"You had your fun with her, and managed to steal from them ${earnings} tsktsktsk!",  
            f"now you are all white stuff and you made ${earnings}, was it really worth it...? probably yes",  
            f"Had to call dudes 'good boy' now you made ${earnings}! desperate motherfuckers"  
        ]  
  
        result_message = random.choice(messages)  
        update_balance(user_id, earnings)  
  
        embed = discord.Embed(title="U MADE SOME MONEY DIRTY SLUTTTTT",   
                            description=result_message,  
                            color=discord.Color.orange()  
                            )  
          
        if isinstance(ctx_or_interaction, discord.Interaction):  
            await ctx_or_interaction.response.send_message(embed=embed)  
        else:  
            await ctx_or_interaction.send(embed=embed)  
  
    @work.error  
    async def work_error(self, ctx, error):  
        if isinstance(error, commands.CommandOnCooldown):  
            embed = discord.Embed(title="You're tired!",  
                                description=f"come back in {int(error.retry_after // 60)} minutes.",  
                                color=discord.Color.red()  
                                )  
            await ctx.send(embed=embed)  
  
    @slut_slash.error  
    async def work_slash_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):  
        if isinstance(error, app_commands.CommandOnCooldown):  
            embed = discord.Embed(title="hoe chill out you are tired and emotionally traumatised!",  
                                description=f"come back in {int(error.retry_after // 60)} minutes.",  
                                color=discord.Color.red()  
                                )  
            await interaction.response.send_message(embed=embed, ephemeral=True)  
  
async def setup(bot):  
    await bot.add_cog(Slut(bot))
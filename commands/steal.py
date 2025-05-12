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

class Steal(commands.Cog):  
    def __init__(self, bot):  
        self.bot = bot  

    @commands.command(help="Attempt to steal money from another user.")  
    @commands.cooldown(1, 1800, commands.BucketType.user)  # 30 minutes  
    async def steal(self, ctx, target: discord.Member):  
        await self._do_steal(ctx, ctx.author, target)  

    @app_commands.command(name="steal", description="Attempt to steal money from another user.")  
    @app_commands.checks.cooldown(1, 1800)  
    async def steal_slash(self, interaction: discord.Interaction, target: discord.Member):  
        await self._do_steal(interaction, interaction.user, target)  

    async def _do_steal(self, ctx_or_interaction, thief, target):  
        thief_id = str(thief.id)  
        target_id = str(target.id)  

        if thief_id == target_id:  
            embed = discord.Embed(  
                title="Shrug...",  
                description="You can't steal from yourself. ¯\\_(ツ)_/¯",  
                color=discord.Color.light_grey()  
            )  
            return await self._send(ctx_or_interaction, embed, True)  

        thief_bal = get_balance(thief_id)  
        target_bal = get_balance(target_id)  

        if target_bal["pocket"] <= 0:  
            embed = discord.Embed(  
                title="Oops!",  
                description=f"{target.display_name} has no pocket money to steal. {random.choice(['No luck!', 'Try someone richer.', 'They broke.'])}",  
                color=discord.Color.red()  
            )  
            return await self._send(ctx_or_interaction, embed, True)  

        if random.random() < 0.2:  # 20% chance to get caught  
            fine = random.randint(100, 10000)  
            update_balance(thief_id, -fine)  
            embed = discord.Embed(  
                title="Caught! **You got arrested!**",  
                description=f"**You were fined ${fine}** for trying to steal! {random.choice(['Better luck next time.', 'The cops were fast today.', 'Rip...'])} \n\n**{thief.display_name} is now in debt!**" if thief_bal["pocket"] - fine < 0 else "",  
                color=discord.Color.red()  
            )  
            embed.set_footer(text="Police sirens intensify")  
            return await self._send(ctx_or_interaction, embed)  

        steal_percent = random.uniform(0.03, 1.0)  
        amount_stolen = max(1, int(target_bal["pocket"] * steal_percent))  
        update_balance(thief_id, amount_stolen)  
        update_balance(target_id, -amount_stolen)  

        embed = discord.Embed(  
            title="Success! **You stole some cash!**",  
            description=f"**{thief.display_name}** stole **${amount_stolen}** from **{target.display_name}**! \n\n{random.choice(['Smooth criminal.', 'No witnesses.', 'That was slick.'])}",  
            color=discord.Color.green()  
        )  
        embed.set_footer(text="Don’t get too greedy now...")  
        return await self._send(ctx_or_interaction, embed)  

    async def _send(self, ctx_or_interaction, embed, ephemeral=False):  
        if isinstance(ctx_or_interaction, discord.Interaction):  
            await ctx_or_interaction.response.send_message(embed=embed, ephemeral=ephemeral)  
        else:  
            await ctx_or_interaction.send(embed=embed)  

    @steal.error  
    async def steal_error(self, ctx, error):  
        if isinstance(error, commands.CommandOnCooldown):  
            minutes = int(error.retry_after // 60)  
            embed = discord.Embed(  
                title="Cooldown!",  
                description=f"You must wait {minutes} minutes before stealing again!",  
                color=discord.Color.orange()  
            )  
            await ctx.send(embed=embed)  

    @steal_slash.error  
    async def steal_slash_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):  
        if isinstance(error, app_commands.CommandOnCooldown):  
            minutes = int(error.retry_after // 60)  
            embed = discord.Embed(  
                title="Cooldown!",  
                description=f"You must wait {minutes} minutes before stealing again!",  
                color=discord.Color.orange()  
            )  
            await interaction.response.send_message(embed=embed, ephemeral=True)  

async def setup(bot):  
    await bot.add_cog(Steal(bot))
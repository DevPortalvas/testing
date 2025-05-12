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
  
def save_balance(user_id, balance):  
    with open(DATA_FILE, "r") as f:  
        data = json.load(f)  
    data[str(user_id)] = balance  
    with open(DATA_FILE, "w") as f:  
        json.dump(data, f)  
  
class Withdraw(commands.Cog):  
    def __init__(self, bot):  
        self.bot = bot  
  
    @commands.command(help="Withdraw money from your bank.")  
    async def withdraw(self, ctx, amount):  
        await self._do_withdraw(ctx, amount)  
  
    @app_commands.command(name="withdraw", description="Withdraw money from your bank")  
    @app_commands.describe(amount="Amount to withdraw or 'all'")  
    async def withdraw_slash(self, interaction: discord.Interaction, amount: str):  
        await self._do_withdraw(interaction, amount)  
  
    async def _do_withdraw(self, ctx_or_interaction, amount):  
        user_id = ctx_or_interaction.user.id if isinstance(ctx_or_interaction, discord.Interaction) else ctx_or_interaction.author.id  
        balance = get_balance(user_id)  
  
        if amount.lower() == "all":  
            amount_to_withdraw = balance["bank"]  
            if amount_to_withdraw == 0:  
                if isinstance(ctx_or_interaction, discord.Interaction):  
                    await ctx_or_interaction.response.send_message("You have nothing to withdraw.")  
                else:  
                    await ctx_or_interaction.send("You have nothing to withdraw.")  
                return  
        else:  
            try:  
                amount_to_withdraw = int(amount)  
            except ValueError:  
                if isinstance(ctx_or_interaction, discord.Interaction):  
                    await ctx_or_interaction.response.send_message("Please enter a valid number or 'all'.")  
                else:  
                    await ctx_or_interaction.send("Please enter a valid number or 'all'.")  
                return  
  
            if amount_to_withdraw <= 0:  
                if isinstance(ctx_or_interaction, discord.Interaction):  
                    await ctx_or_interaction.response.send_message("Amount must be more than 0.")  
                else:  
                    await ctx_or_interaction.send("Amount must be more than 0.")  
                return  
  
            if balance["bank"] < amount_to_withdraw:  
                if isinstance(ctx_or_interaction, discord.Interaction):  
                    await ctx_or_interaction.response.send_message("You don't have that much in your bank.")  
                else:  
                    await ctx_or_interaction.send("You don't have that much in your bank.")  
                return  
  
        balance["bank"] -= amount_to_withdraw  
        balance["pocket"] += amount_to_withdraw  
        save_balance(user_id, balance)  
  
        embed = discord.Embed(  
            title="Withdraw Successful",  
            description=f"You withdrew ${amount_to_withdraw} to your pocket!",  
            color=discord.Color.blurple()  
        )  
          
        if isinstance(ctx_or_interaction, discord.Interaction):  
            await ctx_or_interaction.response.send_message(embed=embed)  
        else:  
            await ctx_or_interaction.send(embed=embed)  
  
async def setup(bot):  
    await bot.add_cog(Withdraw(bot))
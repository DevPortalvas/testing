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
  
class Deposit(commands.Cog):  
    def __init__(self, bot):  
        self.bot = bot  
  
    @commands.command(help="Deposit money into your bank.")  
    async def deposit(self, ctx, amount):  
        await self._do_deposit(ctx, amount)  
  
    @app_commands.command(name="deposit", description="Deposit money into your bank")  
    @app_commands.describe(amount="Amount to deposit or 'all'")  
    async def deposit_slash(self, interaction: discord.Interaction, amount: str):  
        await self._do_deposit(interaction, amount)  
  
    async def _do_deposit(self, ctx_or_interaction, amount):  
        user_id = ctx_or_interaction.user.id if isinstance(ctx_or_interaction, discord.Interaction) else ctx_or_interaction.author.id  
        balance = get_balance(user_id)  
  
        if amount.lower() == "all":  
            amount_to_deposit = balance["pocket"]  
            if amount_to_deposit == 0:  
                if isinstance(ctx_or_interaction, discord.Interaction):  
                    await ctx_or_interaction.response.send_message("you have no money brokie")  
                else:  
                    await ctx_or_interaction.send("you have no money brokie")  
                return  
        else:  
            try:  
                amount_to_deposit = int(amount)  
            except ValueError:  
                if isinstance(ctx_or_interaction, discord.Interaction):  
                    await ctx_or_interaction.response.send_message("enter a valid number or 'all'")  
                else:  
                    await ctx_or_interaction.send("enter a valid number or 'all'")  
                return  
  
            if amount_to_deposit <= 0:  
                if isinstance(ctx_or_interaction, discord.Interaction):  
                    await ctx_or_interaction.response.send_message("amount must be more than 0")  
                else:  
                    await ctx_or_interaction.send("amount must be more than 0")  
                return  
  
            if balance["pocket"] < amount_to_deposit:  
                if isinstance(ctx_or_interaction, discord.Interaction):  
                    await ctx_or_interaction.response.send_message("you dont have that much money dude")  
                else:  
                    await ctx_or_interaction.send("you dont have that much money dude")  
                return  
  
        balance["pocket"] -= amount_to_deposit  
        balance["bank"] += amount_to_deposit  
        save_balance(user_id, balance)  
  
        embed = discord.Embed(  
            title="Deposit Successful",  
            description=f"You deposited ${amount_to_deposit} into your bank.",  
            color=discord.Color.green()  
        )  
          
        if isinstance(ctx_or_interaction, discord.Interaction):  
            await ctx_or_interaction.response.send_message(embed=embed)  
        else:  
            await ctx_or_interaction.send(embed=embed)  
  
async def setup(bot):  
    await bot.add_cog(Deposit(bot))
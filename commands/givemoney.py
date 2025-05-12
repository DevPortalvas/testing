import discord  
from discord.ext import commands  
from discord import app_commands, Interaction  
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
  
class ConfirmView(discord.ui.View):  
    def __init__(self, sender, receiver, amount):  
        super().__init__(timeout=30)  
        self.sender = sender  
        self.receiver = receiver  
        self.amount = amount  
  
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, emoji="✅")  
    async def confirm(self, interaction: Interaction, button: discord.ui.Button):  
        if interaction.user.id != self.sender.id:  
            await interaction.response.send_message("You can't confirm someone else's transfer.", ephemeral=True)  
            return  
        update_balance(str(self.sender.id), -self.amount)  
        update_balance(str(self.receiver.id), self.amount)  
        embed = discord.Embed(  
            title="Money Sent!",  
            description=f"{self.sender.mention} gave ${self.amount} to {self.receiver.mention}.",  
            color=discord.Color.gold()  
        )  
        await interaction.response.edit_message(embed=embed, view=None)  
  
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")  
    async def cancel(self, interaction: Interaction, button: discord.ui.Button):  
        if interaction.user.id != self.sender.id:  
            await interaction.response.send_message("You can't cancel someone else's transfer.", ephemeral=True)  
            return  
        embed = discord.Embed(  
            title="Transfer Cancelled",  
            description="No money was transferred.",  
            color=discord.Color.red()  
        )  
        await interaction.response.edit_message(embed=embed, view=None)  
  
class GiveMoney(commands.Cog):  
    def __init__(self, bot):  
        self.bot = bot  
  
    @app_commands.command(name="givemoney", description="Give pocket money to another user.")  
    async def givemoney_slash(self, interaction: Interaction, user: discord.User, amount: int):  
        await self.send_givemoney(interaction, user, amount)  
  
    @commands.command(name="givemoney")  
    async def givemoney_prefix(self, ctx, user: discord.User, amount: int):  
        await self.send_givemoney(ctx, user, amount)  
  
    async def send_givemoney(self, ctx_or_inter, user: discord.User, amount: int):  
        sender = ctx_or_inter.user if isinstance(ctx_or_inter, Interaction) else ctx_or_inter.author  
  
        if user.id == sender.id:  
            msg = "You can’t give money to yourself!"  
            return await ctx_or_inter.response.send_message(msg, ephemeral=True) if isinstance(ctx_or_inter, Interaction) else await ctx_or_inter.send(msg)  
  
        sender_id = str(sender.id)  
        sender_balance = get_balance(sender_id)  
  
        if sender_balance["pocket"] < amount or amount <= 0:  
            msg = "You don’t have enough money to give!"  
            return await ctx_or_inter.response.send_message(msg, ephemeral=True) if isinstance(ctx_or_inter, Interaction) else await ctx_or_inter.send(msg)  
  
        embed = discord.Embed(  
            title="Confirm Transfer",  
            description=f"Are you sure you want to give **${amount}** to {user.mention}?",  
            color=discord.Color.blue()  
        )  
        view = ConfirmView(sender, user, amount)  
  
        if isinstance(ctx_or_inter, Interaction):  
            await ctx_or_inter.response.send_message(embed=embed, view=view, ephemeral=True)  
        else:  
            await ctx_or_inter.send(embed=embed, view=view)  
  
async def setup(bot):  
    await bot.add_cog(GiveMoney(bot))
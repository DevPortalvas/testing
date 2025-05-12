from discord.ext import commands  
from discord import app_commands, Interaction  
import discord  
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
  
class MoneyControl(commands.Cog):  
    def __init__(self, bot):  
        self.bot = bot  
  
    def has_privilege(self, interaction: Interaction):  
        allowed_id = 545609811354583040  
        perms = interaction.user.guild_permissions  
        return (  
            interaction.user.id == allowed_id or  
            perms.administrator or  
            perms.manage_guild or  
            interaction.user.id == interaction.guild.owner_id  
        )  
  
    @app_commands.command(name="addmoney", description="Add pocket money to a user.")  
    async def add_money(self, interaction: Interaction, user: discord.User, amount: int):  
        if not self.has_privilege(interaction):  
            await interaction.response.send_message("You don’t have permission to use this command.", ephemeral=True)  
            return  
        update_balance(user.id, amount)  
        await interaction.response.send_message(f"Added ${amount} to {user.mention}'s pocket.", ephemeral=True)  
  
    @app_commands.command(name="removemoney", description="Remove pocket money from a user.")  
    async def remove_money(self, interaction: Interaction, user: discord.User, amount: int):  
        if not self.has_privilege(interaction):  
            await interaction.response.send_message("You don’t have permission to use this command.", ephemeral=True)  
            return  
        update_balance(user.id, -amount)  
        await interaction.response.send_message(f"Removed ${amount} from {user.mention}'s pocket.", ephemeral=True)  
  
async def setup(bot):  
    await bot.add_cog(MoneyControl(bot))
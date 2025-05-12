import discord  
from discord.ext import commands  
from discord import app_commands  
import asyncio  
import random  
import json  
import os  
  
DATA_FILE = "data.json"  
ROULETTE_OPTIONS = ["Red", "Black", "Green"]  
WIN_MULTIPLIERS = {"Red": 2, "Black": 2, "Green": 14}  
  
# Helpers for balance  
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
  
# Roulette game state  
active_game = {  
    "message_id": None,  
    "bets": {},  
    "participants": set(),  
    "status": "idle"  
}  
  
class BetSelect(discord.ui.Select):  
    def __init__(self):  
        options = [  
            discord.SelectOption(label="Red", description="Bet on Red", emoji="🔴"),  
            discord.SelectOption(label="Black", description="Bet on Black", emoji="⚫"),  
            discord.SelectOption(label="Green", description="Bet on Green", emoji="🟢")  
        ]  
        super().__init__(placeholder="Choose where to place your bet (multiple allowed)...",  
                         min_values=1, max_values=3, options=options)  
  
    async def callback(self, interaction: discord.Interaction):  
        view: BetView = self.view  
        await view.process_bet_selection(interaction, self.values)  
  
class BetView(discord.ui.View):  
    def __init__(self, bot, bet_amount):  
        super().__init__(timeout=180)  
        self.bot = bot  
        self.bet_amount = bet_amount  
        self.add_item(BetSelect())  
  
    async def process_bet_selection(self, interaction: discord.Interaction, selections):  
        user_id = str(interaction.user.id)  
        bal = get_balance(user_id)  
  
        if bal["pocket"] < self.bet_amount:  
            await interaction.response.send_message("You don't have enough money.", ephemeral=True)  
            return  
  
        split_amount = self.bet_amount // len(selections)  
        if split_amount == 0:  
            await interaction.response.send_message("Your bet is too small to split.", ephemeral=True)  
            return  
  
        update_balance(user_id, -self.bet_amount)  
        active_game["bets"][user_id] = {"amount": self.bet_amount, "choices": selections}  
        active_game["participants"].add(interaction.user)  
  
        await interaction.response.send_message(  
            f"Your bet of ${self.bet_amount} was split across: {', '.join(selections)}", ephemeral=True  
        )  
  
class Roulette(commands.Cog):  
    def __init__(self, bot):  
        self.bot = bot  
  
    @commands.command()  
    async def roulette(self, ctx, bet: str):  
        await self.start_roulette(ctx, bet)  
  
    @app_commands.command(name="roulette", description="Bet on a roulette spin (use 'all' to bet everything)")  
    @app_commands.describe(bet="Amount to bet or type 'all'")  
    async def roulette_slash(self, interaction: discord.Interaction, bet: str):  
        await self.start_roulette(interaction, bet)  
  
    async def start_roulette(self, ctx_or_interaction, bet):  
        user = ctx_or_interaction.user if isinstance(ctx_or_interaction, discord.Interaction) else ctx_or_interaction.author  
        user_id = str(user.id)  
        balance = get_balance(user_id)  
  
        if bet.lower() == "all":  
            bet_amount = balance["pocket"]  
        elif bet.isdigit():  
            bet_amount = int(bet)  
        else:  
            await self._send(ctx_or_interaction, "Invalid bet. Use a number or 'all'.", True)  
            return  
  
        if bet_amount <= 0 or bet_amount > balance["pocket"]:  
            await self._send(ctx_or_interaction, "Insufficient pocket balance.", True)  
            return  
  
        if active_game["status"] == "active":  
            await self.join_existing_game(ctx_or_interaction, bet_amount)  
            return  
  
        active_game["bets"].clear()  
        active_game["participants"].clear()  
        active_game["status"] = "active"  
  
        embed = discord.Embed(title="Roulette Started", description="Select where to place your bet.", color=discord.Color.blurple())  
        embed.set_footer(text="Others can join for 20 seconds.")  
  
        view = BetView(self.bot, bet_amount)  
        if isinstance(ctx_or_interaction, discord.Interaction):  
            await ctx_or_interaction.response.send_message(embed=embed, view=view)  
            sent = await ctx_or_interaction.original_response()  
        else:  
            sent = await ctx_or_interaction.send(embed=embed, view=view)  
  
        active_game["message_id"] = sent.id  
        await asyncio.sleep(20)  
        await self.run_roulette(sent.channel)  
  
    async def join_existing_game(self, ctx_or_interaction, bet_amount):  
        embed = discord.Embed(title="Join Roulette", description="You joined the current round. Pick your bets:", color=discord.Color.blurple())  
        view = BetView(self.bot, bet_amount)  
        if isinstance(ctx_or_interaction, discord.Interaction):  
            await ctx_or_interaction.response.send_message(embed=embed, view=view, ephemeral=True)  
        else:  
            await ctx_or_interaction.send(embed=embed, view=view)  
  
    async def run_roulette(self, channel):  
        result = random.choices(ROULETTE_OPTIONS, weights=[48, 48, 4])[0]  
        winners = []  
  
        for user_id, info in active_game["bets"].items():  
            if result in info["choices"]:  
                share = info["amount"] // len(info["choices"])  
                winnings = share * WIN_MULTIPLIERS[result]  
                update_balance(user_id, winnings)  
                winners.append(f"<@{user_id}> won ${winnings}")  
  
        result_embed = discord.Embed(title="Roulette Result", description=f"The ball landed on **{result}**!", color=discord.Color.green())  
        if winners:  
            result_embed.add_field(name="Winners", value="\n".join(winners), inline=False)  
        else:  
            result_embed.add_field(name="No Winners", value="Better luck next time!", inline=False)  
  
        await channel.send(embed=result_embed)  
        active_game["status"] = "idle"  
  
    async def _send(self, ctx_or_interaction, content, ephemeral=False):  
        if isinstance(ctx_or_interaction, discord.Interaction):  
            await ctx_or_interaction.response.send_message(content, ephemeral=ephemeral)  
        else:  
            await ctx_or_interaction.send(content)  
  
async def setup(bot):  
    await bot.add_cog(Roulette(bot))
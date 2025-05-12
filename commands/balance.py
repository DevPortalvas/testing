
import discord
from discord.ext import commands
from discord import app_commands
from utils.database import get_balance

class Balance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Check your current money in your pocket and your bank.", aliases=['bal', 'money', 'wallet'])
    async def balance(self, ctx, member: discord.Member=None):
        await self._check_balance(ctx, member)

    @app_commands.command(name="balance", description="Check your current money in your pocket and your bank")
    async def balance_slash(self, interaction: discord.Interaction, member: discord.Member=None):
        await self._check_balance(interaction, member)

    async def _check_balance(self, ctx_or_interaction, member=None):
        user = member or (ctx_or_interaction.author if hasattr(ctx_or_interaction, 'author') else ctx_or_interaction.user)
        guild_id = ctx_or_interaction.guild.id
        bal = get_balance(guild_id, user.id)

        embed = discord.Embed(title=f"{user.name}'s Balance", color=discord.Color.green())
        pocket_display = "∞" if bal['pocket'] >= 2**63-1 else f"${bal['pocket']:,}"
        bank_display = "∞" if bal['bank'] >= 2**63-1 else f"${bal['bank']:,}"
        embed.add_field(name="Pocket", value=pocket_display, inline=True)
        embed.add_field(name="Bank", value=bank_display, inline=True)

        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Balance(bot))


import discord 
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_cmd(self, ctx):
        await self._show_help(ctx)

    @app_commands.command(name="help", description="Show all available commands")
    async def help_slash(self, interaction: discord.Interaction):
        await self._show_help(interaction)
        
    async def _show_help(self, ctx_or_interaction):
        embed = discord.Embed(title="Help!",
                            description="here are all the available commands:",
                            color=discord.Color.teal()
                            )
        for command in self.bot.commands:
            if not command.hidden:
                embed.add_field(name=f"{command.name}",
                              value=command.help or "No description provided",
                              inline=False
                              )
        
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))

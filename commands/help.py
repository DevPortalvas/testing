
import discord
from discord.ext import commands
from discord import app_commands
import math

class HelpButtons(discord.ui.View):
    def __init__(self, commands_list, page=0):
        super().__init__(timeout=180)
        self.commands_list = commands_list
        self.page = page
        self.max_pages = math.ceil(len(commands_list) / 5) - 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.max_pages:
            self.page += 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)
        else:
            await interaction.response.defer()

    def get_page_embed(self):
        start_idx = self.page * 5
        end_idx = start_idx + 5
        current_page_commands = self.commands_list[start_idx:end_idx]

        embed = discord.Embed(
            title="Help Menu",
            description=f"Page {self.page + 1}/{self.max_pages + 1}",
            color=discord.Color.blue()
        )

        for cmd in current_page_commands:
            aliases = ", ".join(cmd.aliases) if hasattr(cmd, 'aliases') and cmd.aliases else "None"
            value = f"Description: {cmd.help or 'No description provided'}\nAliases: {aliases}"
            embed.add_field(name=cmd.name, value=value, inline=False)

        return embed

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", help="Shows all available commands")
    async def help_cmd(self, ctx):
        await self._show_help(ctx)

    @app_commands.command(name="help", description="Shows all available commands")
    async def help_slash(self, interaction: discord.Interaction):
        await self._show_help(interaction)

    async def _show_help(self, ctx_or_interaction):
        # Get all visible commands
        commands_list = [cmd for cmd in self.bot.commands if not cmd.hidden]
        
        # Create view with buttons
        view = HelpButtons(commands_list)
        embed = view.get_page_embed()

        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed, view=view)
        else:
            await ctx_or_interaction.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))

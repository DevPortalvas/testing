
import discord
import asyncio
from datetime import datetime

class WebhookManager:
    def __init__(self, webhook_url, bot, db_connection):
        self.webhook_url = webhook_url
        self.bot = bot
        self.db_connection = db_connection
        self.webhook = None
        self.message_id = "1371243723119136868"
        self.is_running = True
        self.start_time = datetime.utcnow()
        
    async def initialize(self):
        self.webhook = discord.Webhook.from_url(self.webhook_url, session=self.bot.session)
        
    async def update_status(self):
        while self.is_running:
            try:
                total_members = sum(guild.member_count for guild in self.bot.guilds)
                embed = discord.Embed(
                    title="Bot Status Monitor",
                    color=discord.Color.green() if self.bot.is_ready() else discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="Server Count", 
                    value=f"🌐 {len(self.bot.guilds)} servers", 
                    inline=True
                )
                embed.add_field(
                    name="Total Members", 
                    value=f"👥 {total_members:,} members", 
                    inline=True
                )
                embed.add_field(
                    name="Bot Status", 
                    value="🟢 Online" if self.bot.is_ready() else "🔴 Offline", 
                    inline=True
                )
                
                # Check database connection
                try:
                    self.db_connection.client.admin.command('ping')
                    db_status = "🟢 Connected"
                except Exception:
                    db_status = "🔴 Disconnected"
                
                embed.add_field(
                    name="Database Status", 
                    value=db_status, 
                    inline=True
                )

                # Calculate uptime
                now = datetime.utcnow()
                delta = now - self.start_time
                days = delta.days
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                uptime_str = f"{days}d {hours}h {minutes}m"
                
                embed.add_field(
                    name="Uptime",
                    value=uptime_str,
                    inline=True
                )
                
                embed.set_footer(text=f"Last updated at {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                
                try:
                    await self.webhook.edit_message(self.message_id, embed=embed)
                except discord.NotFound:
                    print(f"Could not find message with ID {self.message_id}")
                    
            except Exception as e:
                print(f"Error updating webhook status: {e}")
                
            await asyncio.sleep(60)  # Update every 1 minute

    async def set_offline(self):
        self.is_running = False
        if self.message_id and self.webhook:
            try:
                embed = discord.Embed(
                    title="Bot Status Monitor",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Bot Status", value="🔴 Offline", inline=False)
                embed.set_footer(text="Bot is shutting down")
                await self.webhook.edit_message(self.message_id, embed=embed)
            except Exception as e:
                print(f"Error setting offline status: {e}")

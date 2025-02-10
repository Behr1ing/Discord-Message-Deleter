import discord
from discord.ext import tasks, commands
import asyncio
from datetime import datetime, timedelta, timezone
import pytz

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True  # Ensure the bot can access guild information
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix='!', intents=intents)

# Replace 'YOUR_CHANNEL_ID' with the actual channel ID
CHANNEL_ID = 'YOUR_CHANNEL_ID'
next_deletion_time = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Bot is in the following guilds:')
    for guild in bot.guilds:
        print(f'- {guild.name} (ID: {guild.id})')
    delete_messages.start()

@tasks.loop(seconds=1209600)  # 2 weeks
async def delete_messages():
    global next_deletion_time
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="Warning", description="Deleting all messages in 5 seconds...", color=0xff0000)
        await channel.send(embed=embed)
        await asyncio.sleep(5)
        rate_limited = False
        deleted_count = 0
        async for message in channel.history(limit=None):
            try:
                await message.delete()
                deleted_count += 1
                await asyncio.sleep(0.1 if not rate_limited else 1)  # Fast deletion unless rate limited
            except discord.Forbidden:
                print(f"Forbidden: Cannot delete messages in {channel.name}")
            except discord.HTTPException as e:
                if e.status == 429:  # Rate limited
                    print(f"Rate limited: Slowing down for 5 seconds")
                    rate_limited = True
                    await asyncio.sleep(5)
                else:
                    print(f"HTTPException: Failed to delete message in {channel.name}: {e}")
        next_deletion_time = datetime.now(timezone.utc) + timedelta(seconds=1209600)
        next_deletion_time = next_deletion_time.astimezone(pytz.timezone('US/Eastern'))
        next_deletion_str = next_deletion_time.strftime("%Y-%m-%d %H:%M:%S ET")
        embed = discord.Embed(
            title="Info",
            description=f"All messages have been deleted. {deleted_count} messages were deleted.\n\nDeveloper: @Behr\n\nNext deletion will occur on: {next_deletion_str}",
            color=0x00ff00
        )
        await channel.send(embed=embed)

@bot.command()
async def time_until_deletion(ctx):
    """Check how much time is left until the next deletion."""
    if next_deletion_time:
        now = datetime.now(pytz.timezone('US/Eastern'))
        time_left = next_deletion_time - now
        days, seconds = time_left.days, time_left.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        embed = discord.Embed(
            title="Time Until Next Deletion",
            description=f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Time Until Next Deletion",
            description="The next deletion time is not set.",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='commands')
async def show_commands(ctx):
    """Display the help message with all available commands."""
    embed = discord.Embed(
        title="Help",
        description="Here are the available commands:",
        color=0x00ff00
    )
    embed.add_field(name="!time_until_deletion", value="Check how much time is left until the next deletion.", inline=False)
    embed.add_field(name="!commands", value="Display this help message.", inline=False)
    await ctx.send(embed=embed)

# Replace 'YOUR_NEW_BOT_TOKEN' with your actual bot token
bot.run('YOUR_NEW_BOT_TOKEN')

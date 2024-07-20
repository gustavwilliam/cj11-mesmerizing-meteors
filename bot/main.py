from os import getenv

import discord
from discord.ext import commands
from dotenv import load_dotenv
from paginator import Paginator

load_dotenv()

# Identify the bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


# Basic slash command
@bot.tree.command(name="ping", description="Test command!")
async def merhaba(interaction: discord.Interaction) -> None:
    """Test command."""
    print(interaction.response)
    print(dir(interaction.response))
    await interaction.response \
        .send_message(f"Pong! {interaction.user.display_name}")


# Embed message slash command
@bot.tree.command(name="pages",
                  description="""
                  This command sends the embed message containing the pages!
                  """)
async def embed_command(interaction: discord.Interaction) -> None:
    """Send the embed message containing the pages."""
    pages = [
        discord.Embed(title="Page 1", description="This is a page 1"),
        discord.Embed(title="Page 2", description="This is a page 2"),
        discord.Embed(title="Page 3", description="This is a page 3"),
    ]
    paginator = Paginator(pages)
    await interaction.response.send_message(embed=pages[0], view=paginator)


# Bot ready message
@bot.event
async def on_ready() -> None:
    """Give a status report when the bot is ready."""
    print(f"Bot logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} commands synchronized")
    except discord.DiscordException as e:
        print(f"Err: {e}")


# Start the bot
bot.run(getenv('DISCORD_BOT_KEY'))

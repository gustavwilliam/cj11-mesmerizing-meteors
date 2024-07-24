from os import getenv

import async_tio
import discord
from controller import Controller
from discord.ext import commands
from dotenv import load_dotenv
from levels import register_all_levels
from map import Map, generate_map, image_to_discord_file
from paginator import Paginator
from utils.eval import eval_python

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
    await interaction.response.send_message(f"Pong! {interaction.user.display_name}")


# Embed message slash command
@bot.tree.command(
    name="pages",
    description="""
                  This command sends the embed message containing the pages!
                  """,
)
async def embed_command(interaction: discord.Interaction) -> None:
    """Send the embed message containing the pages."""
    pages = [
        discord.Embed(title="Page 1", description="This is a page 1"),
        discord.Embed(title="Page 2", description="This is a page 2"),
        discord.Embed(title="Page 3", description="This is a page 3"),
    ]
    paginator = Paginator(pages)
    await interaction.response.send_message(embed=pages[0], view=paginator)


@bot.tree.command(name="map", description="Send a part of the game's map")
async def get_map(interaction: discord.Interaction, x: int = 0, y: int = 0) -> None:
    """Send a part of the game's map, centered on the given position."""
    img = image_to_discord_file(
        generate_map(
            (x, y),
            player_name=interaction.user.display_name,
        ),
        image_name := "image",
    )
    embed = discord.Embed(
        title=f"\U0001f5fa {interaction.user.display_name}'s map",
        description="Press the arrow keys to move around.",
        color=discord.Color.blurple(),
    )
    embed.set_image(url=f"attachment://{image_name}.png")
    await interaction.response.send_message(file=img, embed=embed, view=Map((x, y), interaction.user))


@bot.tree.command(name="eval", description="Evaluate Python code")
async def eval_code(interaction: discord.Interaction, code: str) -> None:
    """Evaluate Python code and return the output."""
    await interaction.response.defer()
    try:
        output = await eval_python(code)
        output = (
            ":white_check_mark: Your Python 3 eval job succeeded.\n\n**Output**\n```py\n" + output[:2000] + "\n```"
        )
    except async_tio.ApiError as e:
        print("Tio API error: ", e)
        output = ":cross: An API error occured while running your code. Please try again later."
    await interaction.followup.send(
        embed=discord.Embed(
            title="Eval result",
            description=output,
            color=discord.Color.blurple(),
        ),
    )


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

    register_all_levels()
    print("Loaded levels:", ", ".join(str(level.id) for level in Controller().levels))


# Start the bot
bot.run(getenv("DISCORD_BOT_KEY"))

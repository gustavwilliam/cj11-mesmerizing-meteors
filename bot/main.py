from os import getenv
from pathlib import Path

import async_tio
import discord
from controller import Controller
from discord.ext import commands
from dotenv import load_dotenv
from levels import register_all_levels
from map import Map, generate_map, image_to_discord_file
from story import StoryPage, StoryView
from utils.eval import eval_python

load_dotenv()

# Identify the bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


# Basic slash command
@bot.tree.command(name="ping", description="Test command!")
async def merhaba(interaction: discord.Interaction) -> None:
    """Test command."""
    await interaction.response.send_message(f"Pong! {interaction.user.display_name}", ephemeral=True)


@bot.tree.command(name="play", description="Start the Python Adventures game!")
async def get_map(interaction: discord.Interaction) -> None:
    """Start the game."""
    await interaction.response.defer(thinking=True)
    story = StoryView(
        [
            StoryPage(
                "Welcome to Python Adventures!",
                "Mesmerizing Meteors wish you the best of luck in your adventures to come",
                Path("bot/assets/title-art.png"),
            ),
        ],
        user=interaction.user,
    )
    await interaction.followup.send(
        embed=story.first_embed(),
        file=story.first_attachments()[0],
        view=story,
    )
    await story.wait()
    if story.last_interaction is None:
        return
    await story.last_interaction.response.defer(thinking=False)

    map_view = Map(interaction.user)
    img = image_to_discord_file(
        generate_map(
            map_view.player.get_position(),
            player_username=interaction.user.name,
            player_display_name=interaction.user.display_name,
        ),
        image_name := "image",
    )
    embed = discord.Embed(
        title=f"\U0001f5fa {interaction.user.display_name}'s map",
        description="Press the arrow keys to move around.",
        color=discord.Color.blurple(),
    )
    embed.set_image(url=f"attachment://{image_name}.png")
    await interaction.edit_original_response(
        attachments=[img],
        embed=embed,
        view=map_view,
    )


@bot.tree.command(name="level", description="Play a specific level without opening the map")
async def play_level(interaction: discord.Interaction, level: int) -> None:
    """Play a specific level without opening the map."""
    chosen_level = Controller().get_level_by_id(level)
    if chosen_level is None:
        await interaction.response.send_message("Level not found.", ephemeral=True)
        return
    await chosen_level().run(interaction=interaction, map=Map(interaction.user))


@bot.tree.command(name="eval", description="Evaluate Python code")
async def eval_code(interaction: discord.Interaction, *, code: str) -> None:
    """Evaluate Python code and return the output."""
    await interaction.response.defer(ephemeral=True)
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
        ephemeral=True,  # To not drown the channel with eval, since the game map would be lost
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


# Load levels
register_all_levels()
print("Loaded levels:", ", ".join(str(level.id) for level in Controller().levels))


# Start the bot
bot.run(getenv("DISCORD_BOT_KEY"))

import io
import json
from pathlib import Path

import discord
from config import Emoji
from controller import Controller
from database.models.player import PlayerRepo
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont
from utils.view import UserOnlyView

path_bot = Path("bot")
path_assets = path_bot / "assets"
path_maps = path_assets / "map"
path_font = font_manager.findfont(font_manager.FontProperties(family="sans-serif", weight="normal"))

CAMERA_H = 400
CAMERA_W = 600
SquareOrigo = (637, 1116.5)
SquareDeltaX = (111.3, -52)  # Pixels travelled when moving X on map
SquareDeltaY = (111.3, 52)  # Pixels travelled when moving Y on map
SquareDeltaZ = (0, -105)  # Pixels travelled when moving Z on map


with Path.open(path_bot / "map_z.json") as f:
    map_z = json.load(f)


def validate_coord(coord: tuple[int, int]) -> bool:
    """Return whether or not the coordinate is not in the map."""
    return not (map_z.get(str(coord[0])) is None or map_z[str(coord[0])].get(str(coord[1])) is None)


class Map(UserOnlyView):
    """Allows the user to navigate the map."""

    def __init__(self, user: discord.User | discord.Member) -> None:
        super().__init__(original_user=user)
        self.player = PlayerRepo().get(user.name)
        self.user = user
        self.update_buttons()

    async def move(
        self,
        interaction: discord.Interaction,
        x: int = 0,
        y: int = 0,
    ) -> None:
        """Move the player to the new position."""
        old_x, old_y = self.player.get_position()
        new_coord = old_x + x, old_y + y
        if validate_coord(new_coord):
            self.player.set_position(*new_coord)
            PlayerRepo().save(self.player)
            await self.navigate(interaction)
        # If the new position is invalid, do nothing. Since the buttons are
        # disabled if the resulting move would be invalid, this should only
        # happen if the user somehow manages to click the button before it
        # has a chance to be disabled. In that case, we just ignore the click.

    @staticmethod
    def get_embed_description(position: tuple[int, int]) -> str:
        """Get a descripton of the map at the given position."""
        level = Controller().get_level(position)
        if level is None:
            return "Press the arrow keys to move around."

        return f"## {level.name}: {level.topic}\nPress {Emoji.CHECK.value} to start the level."

    def update_buttons(self) -> None:
        """Update the buttons to match the current position."""

        def should_disable(x: int, y: int) -> bool:
            return not validate_coord((x, y))

        x, y = self.player.get_position()
        for child in self.children:
            if not isinstance(child, discord.ui.Button):
                continue
            if child.custom_id == "button_left":
                child.disabled = should_disable(x - 1, y)
            if child.custom_id == "button_up":
                child.disabled = should_disable(x, y - 1)
            if child.custom_id == "button_down":
                child.disabled = should_disable(x, y + 1)
            if child.custom_id == "button_right":
                child.disabled = should_disable(x + 1, y)
            if child.custom_id == "button_confirm":
                child.disabled = not Controller().is_level(self.player.get_position())

    async def navigate(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """Update map to the new position."""
        await interaction.response.defer(thinking=False)
        embed = discord.Embed(
            title=f"\U0001f5fa {self.user.display_name}'s Map",
            color=discord.Color.blurple(),
        )
        embed.description = self.get_embed_description(self.player.get_position())
        img = image_to_discord_file(
            generate_map(
                self.player.get_position(),
                player_username=interaction.user.name,
                player_display_name=self.user.display_name,
            ),
            image_name := "image",
        )
        embed.set_image(url=f"attachment://{image_name}.png")
        self.update_buttons()

        await interaction.edit_original_response(
            embed=embed,
            attachments=[img],
            view=self,
        )

    @discord.ui.button(
        emoji=discord.PartialEmoji.from_str(Emoji.ARROW_LEFT.value),
        style=discord.ButtonStyle.primary,
        custom_id="button_left",
        row=2,
    )
    async def button_left_clicked(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button,
    ) -> None:
        """Go left on the map."""
        await self.move(interaction, x=-1)

    @discord.ui.button(
        emoji=discord.PartialEmoji.from_str(Emoji.ARROW_UP.value),
        style=discord.ButtonStyle.primary,
        custom_id="button_up",
    )
    async def button_up_clicked(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button,
    ) -> None:
        """Go up on the map."""
        await self.move(interaction, y=-1)

    @discord.ui.button(
        emoji=discord.PartialEmoji.from_str(Emoji.ARROW_RIGHT.value),
        style=discord.ButtonStyle.primary,
        custom_id="button_right",
    )
    async def button_right_clicked(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button,
    ) -> None:
        """Go right on the map."""
        await self.move(interaction, x=1)

    @discord.ui.button(
        emoji=discord.PartialEmoji.from_str(Emoji.ARROW_DOWN.value),
        style=discord.ButtonStyle.primary,
        custom_id="button_down",
        row=2,
    )
    async def button_down_clicked(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button,
    ) -> None:
        """Go down on the map."""
        await self.move(interaction, y=1)

    @discord.ui.button(
        emoji=discord.PartialEmoji.from_str(Emoji.CHECK.value),
        style=discord.ButtonStyle.success,
        custom_id="button_confirm",
        disabled=True,
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button,
    ) -> None:
        """Confirm/select on the map."""
        level = Controller().get_level(self.player.get_position())
        if level is not None:
            await level().run(interaction=interaction, map=self)


def get_camera_box(
    position: tuple[int, int],
    offset: tuple[int, int] = (0, 0),
) -> tuple[int, int, int, int]:
    """Get the camera box for the map.

    offset is specified in pixels.
    """
    x, y = position
    z = map_z[str(x)][str(y)]
    pos_x = round(
        SquareOrigo[0] + x * SquareDeltaX[0] + y * SquareDeltaY[0] + z * SquareDeltaZ[0] + offset[0],
    )
    pos_y = round(
        SquareOrigo[1] + x * SquareDeltaX[1] + y * SquareDeltaY[1] + z * SquareDeltaZ[1] + offset[1],
    )
    return (
        pos_x - round(CAMERA_W / 2),
        pos_y - round(CAMERA_H / 2),
        pos_x + round(CAMERA_W / 2),
        pos_y + round(CAMERA_H / 2),
    )


def image_to_discord_file(image: Image.Image, file_name: str = "image") -> discord.File:
    """Get a discord.File from a Pillow.Image.Image. Do not include extension in the file name."""
    with io.BytesIO() as image_binary:
        image.save(image_binary, "PNG")
        image_binary.seek(0)
        return discord.File(fp=image_binary, filename=file_name + ".png")


def _crop_map(
    position: tuple[int, int],
    *,
    map_name: str = "map-done-abc.png",
    offset: tuple[int, int] = (0, 0),
) -> Image.Image:
    """Crop the map so the camera centers on the given position, with the given offset.

    The function currently only supports the fully unlocked map.
    """
    img = Image.open(path_maps / map_name)
    box = get_camera_box(position, offset)
    return img.crop(box)


def draw_player(position: tuple[int, int], map_name: str = "map-done-abc.png") -> tuple[Image.Image, int]:
    """Draw the player on the map centered on the given position.

    Returns the map with the player on it and the player's height.
    """
    player = Image.open(path_assets / "player.png").convert("RGBA")
    player_w, player_h = player.size
    offset = (0, round(-player_h / 2))
    bg = _crop_map(position, offset=offset, map_name=map_name).convert("RGBA")
    bg.paste(
        player,
        (
            round(CAMERA_W / 2 - player_w / 2),
            round(CAMERA_H / 2 - player_h / 2),
        ),
        player,
    )
    return bg, player_h


def draw_name_box(bg: Image.Image, player_name: str, player_h: int) -> None:
    """Draw a name box with the player's name on the map."""
    name_box = Image.open(path_assets / "name-box.png").convert("RGBA")
    name_box_w, name_box_h = name_box.size
    bg.paste(
        name_box,
        (
            round(CAMERA_W / 2 - name_box_w / 2),
            round(CAMERA_H / 2 - player_h / 2 - 40),
        ),
        name_box,
    )
    draw = ImageDraw.Draw(bg)

    fontsize = 24
    font = ImageFont.truetype(path_font, fontsize)
    while font.getlength(player_name) > name_box_w - 10:
        # Decrease font size until the text fits in the box
        fontsize -= 1
        font = ImageFont.truetype(path_font, fontsize)
    left, top, _, bottom = draw.textbbox(
        (
            round(CAMERA_W / 2),
            round(CAMERA_H / 2 - player_h / 2 - 40),
        ),
        player_name,
        font=font,
        align="center",
        anchor="mm",
    )
    draw.text(
        (left, top + name_box_h / 2 - (bottom - top) / 2),
        player_name,
        font=font,
        fill="black",
    )


def get_map_name(player_name: str) -> str:
    """Get the file name for the map version that only has the player's levels unlocked."""
    player = PlayerRepo().get(player_name)
    file_name = "map-done" if player.max_level == 11 else f"map-lvl{player.next_level}"  # noqa: PLR2004, 11 is last level

    completed_levels = player.history.summary(completed=True)
    all_levels = player.history.summary()
    special = ""
    if any(level["lvl_id"] == 12 for level in completed_levels):  # noqa: PLR2004
        special += "a"
    if any(level["lvl_id"] == 13 for level in all_levels):  # noqa: PLR2004
        special += "b"
    if any(level["lvl_id"] == 14 for level in all_levels):  # noqa: PLR2004
        special += "c"

    return f"{file_name}{f'-{''.join(lvl for lvl in special)}' if special else ''}.png"


def generate_map(
    position: tuple[int, int],
    *,
    player_username: str,
    with_player: bool = True,
    player_display_name: str | None = None,
) -> Image.Image:
    """Generate a map centered on the provided map coordinate.

    The map coordinate is not in pixels but in the map's coordinate system.
    Provide (x, y, z) coordinates to center the camera on the specified point.

    If with_player is True, the player will be added to the center of the camera.
    The camera centers on the player centered and shifts the background image slightly,
    so the player correctly stands on the point specified by MapPosition.
    """
    if not with_player:
        return _crop_map(position, map_name=get_map_name(player_username))
    bg, player_h = draw_player(position, map_name=get_map_name(player_username))

    if player_display_name is None:
        return bg
    draw_name_box(bg, player_display_name, player_h)

    return bg

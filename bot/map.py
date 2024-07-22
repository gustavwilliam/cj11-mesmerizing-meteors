from code import interact
from dis import disco
from hmac import new
import io
from enum import Enum
import json
from pathlib import Path

import discord
from PIL import Image

path_bot = Path("bot")
path_assets = path_bot / "assets"
path_maps = path_assets / "map"

CAMERA_H = 400
CAMERA_W = 600
SquareOrigo = (637, 1116.5)
SquareDeltaX = (111.3, -52)  # Pixels travelled when moving X on map
SquareDeltaY = (111.3, 52)  # Pixels travelled when moving Y on map
SquareDeltaZ = (0, -105)  # Pixels travelled when moving Z on map


with open(path_bot / "map_z.json") as f:
    map_z = json.load(f)


class MapPosition(Enum):
    """Positions that the camera can focus on.

    Consists of the x, y coordinates of the center of the camera.
    The coordinates are in the map format. Not pixel coordinates.

    The following types of positions are available:
    - LvlX: Levels 1 to 11, where X is the level's number
    - LvlA, LvlB, LvlC: Special levels A, B, and C
    """

    Lvl1 = (1, 0)
    Lvl2 = (3, 0)
    Lvl3 = (5, 0)
    Lvl4 = (8, 0)
    Lvl5 = (10, 0)
    Lvl6 = (11, 1)
    Lvl7 = (11, 3)
    Lvl8 = (11, 5)
    Lvl9 = (10, 6)
    Lvl10 = (8, 6)
    Lvl11 = (6, 6)
    LvlA = (8, -2)
    LvlB = (12, 1)
    LvlC = (13, 4)


def validate_coord(coord: tuple[int, int]) -> bool:
    """Raise an error if the coordinate is not in the map."""
    return not (
        map_z.get(str(coord[0])) is None
        or map_z[str(coord[0])].get(str(coord[1])) is None
    )


class Map(discord.ui.View):
    """Allows the user to navigate the map."""

    def __init__(self, position: tuple[int, int]) -> None:
        super().__init__(timeout=180)
        self.position = position

    async def move(
        self, interaction: discord.Interaction, x: int = 0, y: int = 0
    ) -> None:
        """Move the player to the new position."""
        old_x, old_y = self.position
        new_coord = old_x + x, old_y + y
        if validate_coord(new_coord):
            self.position = new_coord
            await self.navigate(interaction)
        # If the new position is invalid, do nothing. Since the buttons are
        # disabled if the resulting move would be invalid, this should only
        # happen if the user somehow manages to click the button before it
        # has a chance to be disabled. In that case, we just ignore the click.

    def update_buttons(self):
        """Update the buttons to match the current position."""

        def should_disable(x: int, y: int) -> bool:
            return not validate_coord((x, y))

        x, y = self.position
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

    async def navigate(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """Updates map to the new position."""
        embed = discord.Embed()
        img = image_to_discord_file(generate_map(self.position), image_name := "image")
        embed.set_image(url=f"attachment://{image_name}.png")
        self.update_buttons()

        await interaction.response.edit_message(
            embed=embed, attachments=[img], view=self
        )

    @discord.ui.button(
        label="◀",
        style=discord.ButtonStyle.primary,
        custom_id="button_left",
    )
    async def button_left_clicked(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        """Go left on the map."""
        await self.move(interaction, x=-1)

    @discord.ui.button(
        label="▲",
        style=discord.ButtonStyle.primary,
        custom_id="button_up",
    )
    async def button_up_clicked(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        """Go up on the map."""
        await self.move(interaction, y=-1)

    @discord.ui.button(
        label="▼",
        style=discord.ButtonStyle.primary,
        custom_id="button_down",
    )
    async def button_down_clicked(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        """Go down on the map."""
        await self.move(interaction, y=1)

    @discord.ui.button(
        label="►",
        style=discord.ButtonStyle.primary,
        custom_id="button_right",
    )
    async def button_right_clicked(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        """Go right on the map."""
        await self.move(interaction, x=1)

    @discord.ui.button(
        label="✅", style=discord.ButtonStyle.success, custom_id="confirm"
    )
    async def confirm_page(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        """Confirm the action on the current page."""
        self.clear_items()


def get_camera_box(
    position: tuple[int, int],
    offset: tuple[int, int] = (0, 0),
) -> tuple[int, int, int, int]:
    """
    Get the camera box for the map.

    offset is specified in pixels.
    """
    x, y = position
    z = map_z[str(x)][str(y)]
    pos_x = round(
        SquareOrigo[0]
        + x * SquareDeltaX[0]
        + y * SquareDeltaY[0]
        + z * SquareDeltaZ[0]
        + offset[0]
    )
    pos_y = round(
        SquareOrigo[1]
        + x * SquareDeltaX[1]
        + y * SquareDeltaY[1]
        + z * SquareDeltaZ[1]
        + offset[1]
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
    offset: tuple[int, int] = (0, 0),
) -> Image.Image:
    """Crop the map so the camera centers on the given position, with the given offset.

    The function currently only supports the fully unlocked map.
    """
    img = Image.open(path_maps / "map-done-abc.png")
    box = get_camera_box(position, offset)
    return img.crop(box)


def generate_map(position: tuple[int, int], *, with_player: bool = True) -> Image.Image:
    """Generate a map centered on the provided map coordinate.

    The map coordinate is not in pixels but in the map's coordinate system.
    Provide (x, y, z) coordinates to center the camera on the specified point.

    If with_player is True, the player will be added to the center of the camera.
    The camera centers on the player centered and shifts the background image slightly,
    so the player correctly stands on the point specified by MapPosition.
    """
    if not with_player:
        return _crop_map(position)

    player = Image.open(path_assets / "player.png").convert("RGBA")
    player_h, player_w = player.size
    offset = (0, round(-player_h / 2))
    bg = _crop_map(position, offset=offset).convert("RGBA")
    bg.paste(
        player,
        (
            round(CAMERA_W / 2 - player_w / 2),
            round(CAMERA_H / 2 - player_h / 2),
        ),
        player,
    )
    return bg

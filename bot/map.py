import io
from enum import Enum
from pathlib import Path

import discord
from PIL import Image

assets = Path("bot/assets")
maps = assets / "map"

CAMERA_H = 400
CAMERA_W = 600
SquareOrigo = (637, 1116.5)
SquareDeltaX = (111.3, -52)  # Pixels travelled when moving X on map
SquareDeltaY = (111.3, 52)  # Pixels travelled when moving Y on map
SquareDeltaZ = (0, -105)  # Pixels travelled when moving Z on map


class MapPosition(Enum):
    """Positions that the camera can focus on.

    Consists of the x, y coordinates of the center of the camera.
    The coordinates are in the map format. Not pixel coordinates.

    The following types of positions are available:
    - LvlX: Levels 1 to 11, where X is the level's number
    - LvlA, LvlB, LvlC: Special levels A, B, and C
    """

    Lvl1 = (1, 0, 0)
    Lvl2 = (3, 0, 0)
    Lvl3 = (5, 0, 0)
    Lvl4 = (8, 0, 0)
    Lvl5 = (10, 0, 0)
    Lvl6 = (11, 1, 0)
    Lvl7 = (11, 3, -1)
    Lvl8 = (11, 5, -1)
    Lvl9 = (10, 6, -1)
    Lvl10 = (8, 6, -1)
    Lvl11 = (6, 6, -1)
    LvlA = (8, -2, 0)
    LvlB = (12, 1, 0)
    LvlC = (13, 4, -1)


def get_camera_box(
    position: tuple[int, int, int],
    offset: tuple[int, int] = (0, 0),
) -> tuple[int, int, int, int]:
    """
    Get the camera box for the map.

    offset is specified in pixels.
    """
    x, y, z = position
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
    position: tuple[int, int, int],
    *,
    offset: tuple[int, int] = (0, 0),
) -> Image.Image:
    """Crop the map so the camera centers on the given position, with the given offset.

    The function currently only supports the fully unlocked map.
    """
    img = Image.open(maps / "map-done-abc.png")
    box = get_camera_box(position, offset)
    return img.crop(box)


def generate_map(
    position: tuple[int, int, int], *, with_player: bool = True
) -> Image.Image:
    """Generate a map centered on the provided map coordinate.

    The map coordinate is not in pixels but in the map's coordinate system.
    Provide (x, y, z) coordinates to center the camera on the specified point.

    If with_player is True, the player will be added to the center of the camera.
    The camera centers on the player centered and shifts the background image slightly,
    so the player correctly stands on the point specified by MapPosition.
    """
    if not with_player:
        return _crop_map(position)

    player = Image.open(assets / "player.png").convert("RGBA")
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

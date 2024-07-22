import io
from enum import Enum
from pathlib import Path

import discord
from PIL import Image

assets = Path("bot/assets")
maps = assets / "map"

CAMERA_H = 400
CAMERA_W = 600


class MapPosition(Enum):
    """Positions that the camera can focus on.

    Consists of the x, y coordinates of the center of the camera.

    The following types of positions are available:
    - LvlX: Levels 1 to 11, where X is the level's number
    - LvlA, LvlB, LvlC: Special levels A, B, and C
    - PosX: Custom positions, where X is the ID of the position
    """

    Lvl1 = (750, 1063)
    Lvl2 = (967, 958)
    Lvl3 = (1191, 852)
    Lvl4 = (1532, 697)
    Lvl5 = (1751, 597)
    Lvl6 = (1986, 597)
    Lvl7 = (2193, 805)
    Lvl8 = (2417, 906)
    Lvl9 = (2419, 1007)
    Lvl10 = (2193, 1114)
    Lvl11 = (1965, 1220)
    LvlA = (1311, 597)
    LvlB = (2065, 555)
    LvlC = (2496, 767)


def get_camera_box(
    position: MapPosition,
    offset: tuple[int, int] = (0, 0),
) -> tuple[int, int, int, int]:
    """Get the camera box for the map."""
    x, y = position.value
    x += offset[0]
    y += offset[1]

    return (
        x - round(CAMERA_W / 2),
        y - round(CAMERA_H / 2),
        x + round(CAMERA_W / 2),
        y + round(CAMERA_H / 2),
    )


def image_to_discord_file(image: Image.Image, file_name: str = "image") -> discord.File:
    """Get a discord.File from a Pillow.Image.Image. Do not include extension in the file name."""
    with io.BytesIO() as image_binary:
        image.save(image_binary, "PNG")
        image_binary.seek(0)
        return discord.File(fp=image_binary, filename=file_name + ".png")


def _crop_map(
    position: MapPosition = MapPosition.Lvl1,
    offset: tuple[int, int] = (0, 0),
) -> Image.Image:
    """Crop the map so the camera centers on the given position, with the given offset.

    The function currently only supports the fully unlocked map.
    """
    img = Image.open(maps / "map-done-abc.png")
    box = get_camera_box(position, offset)
    return img.crop(box)


def generate_map(position: MapPosition, *, with_player: bool = True) -> Image.Image:
    """Generate a map centered on the provided MapPosition.

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

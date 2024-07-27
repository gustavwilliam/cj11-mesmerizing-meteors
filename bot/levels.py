import json
from pathlib import Path
from typing import Protocol

import discord
from controller import Controller
from discord import Interaction
from map import Map, generate_map, image_to_discord_file
from questions import Question, QuestionStatus, question_factory
from story import StoryPage, StoryView

with Path.open(Path("bot/questions.json")) as f:
    all_questions = json.load(f)


class Level(Protocol):
    """Protocol that all levels must implement.

    Different level types can be created by subclassing this protocol.
    All levels must run `Level.register()` to register the level class with the controller.
    This should happen at startup.

    Instances of the levels that subclass this protocol are created
    when a level is run. The data for the level is stored in the instance,
    for example, the score of the specific run. When the run is over,
    the instance is destroyed, so all data that should persist between runs
    should be stored in a different place.
    """

    id: int
    name: str
    topic: str
    map_position: tuple[int, int]
    questions: list[Question]

    @classmethod
    def register(cls) -> None:
        """Register a Level class with the controller."""
        Controller().add_level(cls)

    def __init__(self) -> None:
        """Fetch the data for the level."""
        self.fetch_level_data()

    def __str__(self) -> str:
        return self.name

    def fetch_level_data(self) -> None:
        """Fetch the questions, answers, and other data for the level and assign to questions attribute.

        The data is retrieved from bot/questions.json. The id of the level in the JSON file
        must match the id attribute of the Level subclass for the information to be loaded.
        If no questions are found for the level, a ValueError is raised.
        """
        questions = all_questions.get(str(self.id))
        if questions is None:
            raise ValueError("No questions found for level " + str(self.id))
        self.questions = [question_factory(**question_data) for question_data in questions]

    async def return_to_map(self, interaction: Interaction, map: Map) -> None:
        """Return to the map after the level is exited."""
        img = image_to_discord_file(
            generate_map(
                map.position,
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
        await interaction.edit_original_response(
            attachments=[img],
            embed=embed,
            view=Map(map.position, interaction.user),
        )

    async def run(self, interaction: Interaction, map: Map) -> None:
        """Run the level."""
        next_interaction = interaction
        await next_interaction.response.defer()
        for i, question in enumerate(self.questions):
            question_view = question.view()
            await next_interaction.edit_original_response(
                embed=question.embed(level=self, question_index=i + 1),
                view=question_view,
                attachments=[],
            )
            await question_view.wait()
            next_interaction = question_view.next_question_interaction
            if next_interaction is None:
                break
            if question_view.status == QuestionStatus.EXITED:
                break
        else:
            await self.on_success(next_interaction)

        if next_interaction is not None:
            next_interaction = await self.return_to_map(interaction, map)

    async def on_failure(self, interaction: Interaction) -> Interaction:
        """Call when the player fails the level."""
        story = StoryView(
            pages=[
                StoryPage(
                    title="Level failed!",
                    description="Try again and let's beat this level!.",
                    image_path=Path("bot/assets/level-fail.png"),
                    color=discord.Color.red(),
                ),
            ],
        )
        await interaction.edit_original_response(
            embed=story.first_embed(),
            attachments=story.first_attachments(),
            view=story,
        )
        await story.wait()
        if story.last_interaction is None:
            raise ValueError
        await story.last_interaction.response.defer()
        return story.last_interaction

    async def on_success(self, interaction: Interaction) -> Interaction:
        """Call when the player succeeds the level."""
        story = StoryView(
            pages=[
                StoryPage(
                    title="Level complete!",
                    description="Well done completing the level.",
                    image_path=Path("bot/assets/level-success.png"),
                    color=discord.Color.green(),
                ),
            ],
        )
        await interaction.edit_original_response(
            embed=story.first_embed(),
            attachments=story.first_attachments(),
            view=story,
        )
        await story.wait()
        if story.last_interaction is None:
            raise ValueError
        await story.last_interaction.response.defer()
        return story.last_interaction


class Level1(Level):  # noqa: D101
    id = 1
    name = "Level 1"
    topic = "List Comprehensions"
    map_position = (1, 0)


class Level2(Level):  # noqa: D101
    id = 2
    name = "Level 2"
    topic = "Generators"
    map_position = (3, 0)


class Level3(Level):  # noqa: D101
    id = 3
    name = "Level 3"
    topic = "Iterator"
    map_position = (5, 0)


class Level4(Level):  # noqa: D101
    id = 4
    name = "Level 4"
    topic = "Function overloading"
    map_position = (8, 0)


class Level5(Level):  # noqa: D101
    id = 5
    name = "Level 5"
    topic = "Rewind Showcase"
    map_position = (10, 0)


class Level6(Level):  # noqa: D101
    id = 6
    name = "Level 6"
    topic = "File Handling"
    map_position = (11, 1)


class Level7(Level):  # noqa: D101
    id = 7
    name = "Level 7"
    topic = "Regular Expressions"
    map_position = (11, 3)


class Level8(Level):  # noqa: D101
    id = 8
    name = "Level 8"
    topic = "OOP (Part I)"
    map_position = (11, 5)


class Level9(Level):  # noqa: D101
    id = 9
    name = "Level 9"
    topic = "OOP (Part II)"
    map_position = (10, 6)


class Level10(Level):  # noqa: D101
    id = 10
    name = "Level 10"
    topic = "Quizmaster's Reflection"
    map_position = (8, 6)


class Level11(Level):  # noqa: D101
    id = 11
    name = "Level 11"
    topic = "Final Insight Odyssey"
    map_position = (6, 6)


def register_all_levels() -> None:
    """Register all levels with the controller."""
    Level1.register()
    Level2.register()
    Level3.register()
    Level4.register()
    Level5.register()
    Level6.register()
    Level7.register()
    Level8.register()
    Level9.register()
    Level10.register()
    Level11.register()

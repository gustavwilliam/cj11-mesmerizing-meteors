import json
from pathlib import Path
from typing import Protocol

import discord
from controller import Controller
from database.models.player import Player, PlayerRepo, Position
from discord import File, Interaction
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
    hearts: int = 3

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
        position = map.player.get_position()
        if position == (12, 1):  # Move player out of B cave
            position = Position(11, 1)
        if position == (13, 4):  # Move player out of C cave
            position = Position(12, 4)
        map.player.set_position(*position)
        PlayerRepo().save(map.player)

        img = image_to_discord_file(
            generate_map(
                position=position,
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
            view=Map(interaction.user),
        )

    def get_hearts_file(self) -> File:
        """Return the path to the hearts image file."""
        return File(
            Path(f"bot/assets/hearts_{self.hearts}.png"),
            filename="hearts.png",  # Must be exactly this. Question.embed() depends on it
        )

    def _level_unlocked(self, player: Player) -> bool:
        """Return True if level is unlocked."""
        level = player.summary
        return any(run["available"] for run in level if run["lvl_id"] == self.id) if level else False

    async def run(self, interaction: Interaction, map: Map) -> None:
        """Run the level."""
        player = PlayerRepo().get(interaction.user.name)
        if not self._level_unlocked(player):
            await interaction.response.send_message("Level is locked. Keep playing to unlock it!", ephemeral=True)
            return

        next_interaction = interaction
        await next_interaction.response.defer()
        for i, question in enumerate(self.questions):
            while next_interaction is not None:
                question_view = question.view(interaction.user)
                await next_interaction.edit_original_response(
                    embed=question.embed(level=self, question_index=i + 1),
                    view=question_view,
                    attachments=[self.get_hearts_file()],
                )
                await question_view.wait()
                next_interaction = question_view.next_question_interaction
                if question_view.status in [QuestionStatus.EXITED, QuestionStatus.CORRECT]:
                    break
                if question_view.status == QuestionStatus.INCORRECT:
                    self.hearts -= 1
                    if self.hearts == 0:
                        if next_interaction is None:
                            break
                        await self.on_failure(next_interaction)
                        break
            if next_interaction is None or question_view.status in [QuestionStatus.EXITED, QuestionStatus.INCORRECT]:
                break
        if next_interaction is not None:
            if question_view.status == QuestionStatus.CORRECT:
                await self.on_success(next_interaction)
            next_interaction = await self.return_to_map(interaction, map)

    async def on_failure(self, interaction: Interaction) -> Interaction:
        """Call when the player fails the level."""
        story = StoryView(
            pages=[
                StoryPage(
                    title="No lives left",
                    description="Try again and let's beat this level!",
                    image_path=Path("bot/assets/level-fail.png"),
                    color=discord.Color.red(),
                ),
            ],
            continue_button_style=discord.ButtonStyle.danger,
            user=interaction.user,
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

    def _success_page(self) -> StoryPage:
        """Return the success pages for the level.

        This can be overridden by subclasses to add more pages to the success story, or to change the success page.
        """
        return StoryPage(
            title="Level complete!",
            description="Well done completing the level.",
            image_path=Path("bot/assets/level-success.png"),
            color=discord.Color.green(),
        )

    def _success_more_pages(self) -> list[StoryPage]:
        """Return additional success pages for the level.

        This can be overridden by subclasses to add more pages to the success story.
        Defaults to an adding no additional pages.
        """
        return []

    async def _success_story(self, interaction: Interaction) -> Interaction:
        story = StoryView(
            pages=[self._success_page(), *(self._success_more_pages())],
            continue_button_style=discord.ButtonStyle.success,
            user=interaction.user,
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
        player = PlayerRepo().get(interaction.user.name)
        player.complete_level(level=self.id, score=1)
        PlayerRepo().save(player)
        return await self._success_story(interaction=interaction)


class Level1(Level):  # noqa: D101
    id = 1
    name = "Level 1"
    topic = "List Comprehensions"
    map_position = (1, 0)

    async def run(self, interaction: Interaction[discord.Client], map: Map) -> None:
        """Run the level. Overwrites to add a notice about hearts on first level."""
        await interaction.response.defer(thinking=True)
        story = StoryView(
            [
                StoryPage(
                    "Quick note about lives",
                    "You have three lives for every level. If you answer a question incorrectly, you will lose a life.\
 Lose all 3 and you lose the level. Keep track of your current lives in the top right corner of the question embed.",
                    Path("bot/assets/guide-hearts.png"),
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
            return None
        return await super().run(story.last_interaction, map)


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

    async def on_success(self, interaction: Interaction[discord.Client]) -> Interaction:
        """Unlock special level A."""
        player = PlayerRepo().get(interaction.user.name)
        player.unlock_level(level=12)
        PlayerRepo().save(player)
        return await super().on_success(interaction)


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

    async def on_success(self, interaction: Interaction[discord.Client]) -> Interaction:
        """Unlock special level B."""
        player = PlayerRepo().get(interaction.user.name)
        player.unlock_level(level=13)
        PlayerRepo().save(player)
        return await super().on_success(interaction)

    def _success_more_pages(self) -> list[StoryPage]:
        return [
            *super()._success_more_pages(),
            StoryPage(
                title="Special level B unlocked!",
                description="You have completed the final level of the normal path of the game. \
                    Now it's time for you to prove your skills in the *special levels*.",
                image_path=Path("bot/assets/unlocked-b.png"),
                color=discord.Color.green(),
            ),
        ]


class LevelA(Level):  # noqa: D101
    id = 12
    name = "Level A"
    topic = "Quadratic Quest"
    map_position = (8, -2)


class LevelB(Level):  # noqa: D101
    id = 13
    name = "Level B"
    topic = "Fusion Master"
    map_position = (12, 1)

    async def on_success(self, interaction: Interaction[discord.Client]) -> Interaction:
        """Unlock special level C."""
        player = PlayerRepo().get(interaction.user.name)
        player.unlock_level(level=14)
        PlayerRepo().save(player)
        return await super().on_success(interaction)

    def _success_more_pages(self) -> list[StoryPage]:
        return [
            *super()._success_more_pages(),
            StoryPage(
                title="Special level C unlocked!",
                description="You have completed a special level. Complete the newly unlocked *special level C* \
                    to complete the whole game! This is the final level.",
                image_path=Path("bot/assets/unlocked-c.png"),
                color=discord.Color.green(),
            ),
        ]


class LevelC(Level):  # noqa: D101
    id = 14
    name = "Level C"
    topic = "Final Frontier"
    map_position = (13, 4)

    def _success_page(self) -> StoryPage:
        return StoryPage(
            title="You finished Python Adventures!",
            description="You have completed all levels of the game — well done! While this may be the end of \
                Python Adventures, it is only the beginning of *your* Python adventure. \
                    Keep coding and keep learning!\n\nThank you for playing our game. We hope you enjoyed it :)\n\
                        ~ Mesmerizing Meteors",
            image_path=Path("bot/assets/game-win.png"),
            color=discord.Color.yellow(),
        )


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
    LevelA.register()
    LevelB.register()
    LevelC.register()

from pathlib import Path

import discord


class StoryPage:
    """A page in a story, with a title, description, and optional image."""

    def __init__(self, title: str, description: str, image_path: Path | None = None) -> None:
        self.title = title
        self.description = description
        self.image_path = image_path

    def embed(self) -> discord.Embed:
        """Return an embed with the image."""
        embed = discord.Embed(title=self.title, description=self.description)
        if self.image_path:
            embed.set_image(url=f"attachment://{self.image_path.name}")
        return embed

    def attachments(self) -> list[discord.File]:
        """Return the image as a discord.py File object."""
        if not self.image_path:
            return []
        return [discord.File(self.image_path, filename=self.image_path.name)]


class StoryView(discord.ui.View):
    """Story pages, with an image/text in an embed, allowing the user to continue."""

    def __init__(self, pages: list[StoryPage], *, skippable: bool = False) -> None:
        super().__init__()
        if len(pages) < 1:
            raise ValueError
        self.pages = pages
        self.skippable = skippable
        self.current_page = 0
        self.last_interaction: discord.Interaction | None = None
        self.skip_button.disabled = not skippable

    def _next_page(self) -> None:
        """Turn to the next page only, but don't send the response.

        Raises ValueError if there are no more pages to turn to.
        """
        self.current_page += 1
        if self.current_page >= len(self.pages):
            raise ValueError

    def first_embed(self) -> discord.Embed:
        """Show the first page."""
        page = self.pages[self.current_page]
        return page.embed()

    def first_attachments(self) -> list[discord.File]:
        """Show the first page."""
        page = self.pages[self.current_page]
        return page.attachments()

    async def show_page(self, interaction: discord.Interaction) -> None:
        """Show the current page."""
        page = self.pages[self.current_page]
        await interaction.response.edit_message(embed=page.embed(), attachments=page.attachments(), view=self)

    async def show_next_page(self, interaction: discord.Interaction) -> None:
        """Show the next page."""
        try:
            self._next_page()
        except ValueError:
            self.end(interaction)
        else:
            await self.show_page(interaction)

    def end(self, interaction: discord.Interaction) -> None:
        """End the story."""
        self.last_interaction = interaction
        self.stop()

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.success)
    async def continue_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Show the next page."""
        await self.show_next_page(interaction)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.secondary, custom_id="skip_button")
    async def skip_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Skip the story."""
        if self.skippable:
            self.end(interaction)

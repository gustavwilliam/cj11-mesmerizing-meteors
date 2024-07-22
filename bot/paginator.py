import discord


class Paginator(discord.ui.View):
    """Allow you to reliably navigate the pages within the embed messages."""

    def __init__(self, pages: list[discord.Embed]) -> None:
        super().__init__(timeout=180)
        self.pages = pages

        self.current_page = 0
        self.last_page = len(pages) - 1

    def turn_page(self, *, next: bool = True) -> None:
        """Change the current page and enables/disables the buttons depending on the conditions.

        Args:
        ----
            next (bool, optional): go to the next page? Defaults to True.

        """
        self.current_page = max(0, min(self.current_page + (1 if next else -1), self.last_page))

        self.prev_button_click.disabled = self.current_page == 0
        self.next_button_click.disabled = self.current_page == self.last_page

    @discord.ui.button(label="◀", style=discord.ButtonStyle.primary, custom_id="prev", disabled=1)
    async def prev_button_click(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Go to the previous page."""
        self.turn_page(next=False)

        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="✅", style=discord.ButtonStyle.success, custom_id="confirm")
    async def confirm_page(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Confirm the action on the current page."""
        self.clear_items()
        await interaction.response.edit_message(
            embed=None,
            content=f"You selected page number {(self.current_page+1)}",
            view=self,
        )

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary, custom_id="next")
    async def next_button_click(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Go to next page."""
        self.turn_page()

        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

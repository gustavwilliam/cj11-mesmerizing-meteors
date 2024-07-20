import discord


class Paginator(discord.ui.View):
    """Allow you to reliably navigate the pages within the embed messages."""

    def __init__(self, pages: list[discord.Embed]) -> None:
        super().__init__(timeout=180)
        self.pages = pages
        self.current_page = 0

    def update_buttons(self) -> None:
        """Change the status of buttons to enabled or disabled depending on the current page."""
        self.children[0].disabled = self.current_page == 0
        self.children[2].disabled = self.current_page == len(self.pages) - 1

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary, custom_id="prev", disabled=1)
    async def prev_button_click(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:  # noqa: ARG002
        """Go to the previous page."""
        self.current_page = (self.current_page - 1) % len(self.pages)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="✅", style=discord.ButtonStyle.success, custom_id="confirm")
    async def confirm_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:  # noqa: ARG002
        """Confirm the action on the current page."""
        self.clear_items()
        await interaction.response.edit_message(
            embed=None,
            content=f"You selected page number {(self.current_page+1)}",
            view=self,
        )

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary, custom_id="next")
    async def next_button_click(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:  # noqa: ARG002
        """Go to next page."""
        self.current_page = (self.current_page + 1) % len(self.pages)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

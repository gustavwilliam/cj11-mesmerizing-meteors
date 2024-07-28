import discord


class UserOnlyView(discord.ui.View):
    """A view that only allows the original author to interact with it, and doesn't time out."""

    def __init__(self, *args, original_user: discord.User | discord.Member, **kwargs) -> None:  # noqa: ANN002, ANN003
        super().__init__(*args, **kwargs, timeout=None)
        self.original_user = original_user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if the interaction is from the original author."""
        if interaction.user == self.original_user:
            return True
        await interaction.response.send_message("You can't interact with this view.", ephemeral=True)
        return False

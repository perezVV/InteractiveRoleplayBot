import random
import datetime

from discord.ext import commands
from discord import app_commands
import discord

import utils.helpers as helpers

class ETCCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #region /roll
    @app_commands.command(name = "roll", description = "Roll for a random number.")
    @app_commands.describe(max_num = "The maximum number for the roll.")
    @app_commands.describe(passing_roll = "Optional; The number that the roll must be more than to be considered a passing roll.")
    async def roll(self, interaction: discord.Interaction, max_num: int, passing_roll: int = -1):
        await interaction.response.defer(thinking=True)
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        rollNum = random.randint(1, max_num)
        passingString = '.'

        if passing_roll != -1:
            passingString = (
                f', attempting to beat **{passing_roll}**. Roll **succeeded**!'
                if rollNum >= passing_roll
                else f', attempting to beat **{passing_roll}**. Roll **failed**.'
            )
            
        if player is not None:
            await interaction.followup.send(
                f"***{player.get_name()}** rolled **{rollNum}** out of **{max_num}**{passingString}*"
            )
            return

        if passing_roll == -1:
            passingString = ''
            
        await interaction.followup.send(
            f"*Rolled **{rollNum}** out of **{max_num}**{passingString}*"
        )
        return
    #endregion
    #region /time
    @app_commands.command(name = "time", description = "Check the current time in roleplay.")
    async def time(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)

        t = datetime.datetime.now()
        current_time = t.strftime("%I:%M %p")

        if player is not None:
            await interaction.followup.send(f"***{player.get_name()}** checked the time:*\n`{current_time }`")
            return

        await interaction.followup.send(f"`{current_time}`")
    #endregion

async def setup(bot: commands.Bot):
    await bot.add_cog(ETCCMDs(bot))
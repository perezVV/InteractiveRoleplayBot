import typing

from discord.ext import commands
from discord import app_commands
import discord

import utils.autocompletes as autocompletes
import utils.helpers as helpers
import utils.data as data

class PlayerCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #region /players
    @app_commands.command(name = "players", description = "List all players in the current room.")
    async def players(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        channel_id = interaction.channel_id
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        currRoom = helpers.get_room_from_id(channel_id)

        if await helpers.check_paused(player, interaction):
            return

        if currRoom is None:
            await interaction.followup.send("*You are not currently in a room. Please contact an admin if you believe this is a mistake.*")
            return

        playerList: typing.List[str] = []
        for thisPlayer in data.playerdata.values():
            currPlayer = ''
            if thisPlayer.get_room() is not None and thisPlayer.get_room().get_name() == currRoom.get_name():
                currPlayer = thisPlayer.get_name()
                playerList.append(f"`{currPlayer}`")

        allPlayers = ", ".join(playerList)

        if player is None:
            if not playerList:
                await interaction.followup.send(f"*Looked at the players in the room **{currRoom.get_name()}**:*\n\n`No players found.`")
                return
            await interaction.followup.send(f"*Looked at the players in the room **{currRoom.get_name()}**:*\n\n{allPlayers}")
            return


        if not playerList:
            await interaction.followup.send(f"***{player.get_name()}** looked at the players in the room **{currRoom.get_name()}**:*\n\n`No players found.`")
            return

        await interaction.followup.send(f"***{player.get_name()}** looked at the players in the room **{currRoom.get_name()}**:*\n\n{allPlayers}")
    #endregion
    
async def setup(bot: commands.Bot):
    await bot.add_cog(PlayerCMDs(bot))
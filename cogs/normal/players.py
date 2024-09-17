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

    #region /lookplayer
    @app_commands.command(name = "lookplayer", description = "Get the description of a specific player in the current room.")
    @app_commands.describe(player_name = "The list of players in the current room.")
    @app_commands.autocomplete(player_name=autocompletes.players_autocomplete)
    async def lookplayer(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer(thinking=True)
        player_id = interaction.user.id
        lookingPlayer = helpers.get_player_from_id(player_id)

        if await helpers.check_paused(lookingPlayer, interaction):
            return

        simplified = helpers.simplify_string(player_name)
        player = None

        for p in data.playerdata.values():
            if helpers.simplify_string(p.get_name()) == simplified:
                player = p

        if player is None:
            await interaction.followup.send(f"*Could not find player **{player_name}**. Please use `/players` to see a list of all players in the current room.*")
            return

        clothesList = player.get_clothes()
        clothesNames = [f"`{clothing.get_name()}`" for clothing in clothesList]
        allClothes = ', '.join(clothesNames)

        if lookingPlayer is None:
            if player.get_desc() == '':
                if len(clothesList) == 0:
                    await interaction.followup.send(f"*Looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `Nothing.`\n\n`Player has no description.`")
                    return
                await interaction.followup.send(f"*Looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {allClothes}\n\n`Player has no description.`")
                return
            if len(clothesList) == 0:
                await interaction.followup.send(f"*Looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `Nothing.`\n\n{player.get_desc()}")
                return
            await interaction.followup.send(f"*Looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {allClothes}\n\n{player.get_desc()}")
            return

        if lookingPlayer is player:
            if player.get_desc() == '':
                if len(clothesList) == 0:
                    await interaction.followup.send(f"***{lookingPlayer.get_name()}** looked at themself:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `Nothing.`\n\n`Player has no description.`")
                    return
                await interaction.followup.send(f"***{lookingPlayer.get_name()}** looked at themself:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {allClothes}\n\n`Player has no description.`")
                return
            if len(clothesList) == 0:
                await interaction.followup.send(f"***{lookingPlayer.get_name()}** looked at themself:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `Nothing.`\n\n{player.get_desc()}")
                return
            await interaction.followup.send(f"***{lookingPlayer.get_name()}** looked at themself:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {allClothes}\n\n{player.get_desc()}")
            return


        if player.get_desc() == '':
                if len(clothesList) == 0:
                    await interaction.followup.send(f"***{lookingPlayer.get_name()}** looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `Nothing.`\n\n`Player has no description.`")
                    return
                await interaction.followup.send(f"***{lookingPlayer.get_name()}** looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {allClothes}\n\n`Player has no description.`")
                return

        if len(clothesList) == 0:
            await interaction.followup.send(f"***{lookingPlayer.get_name()}** looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `Nothing.`\n\n{player.get_desc()}")
            return
        await interaction.followup.send(f"***{lookingPlayer.get_name()}** looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {allClothes}\n\n{player.get_desc()}")
    #endregion
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
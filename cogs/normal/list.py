import typing

from discord.ext import commands
from discord import app_commands
import discord

import utils.data as data
import utils.helpers as helpers
import utils.autocompletes as autocompletes

class ListCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #region /items
    @app_commands.command(name = "items", description = "List all of the items in the current room.")
    async def items(self, interaction: discord.Interaction):
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

        itemList = currRoom.get_items()
        itemNames = [f"`{item.get_name()}`" for item in itemList]
        allItems = ', '.join(itemNames)

        if player is None:
            if len(itemList) == 0:
                await interaction.followup.send(f"*Looked at the items in the room **{str(currRoom.get_name())}**:*\n\n`No items found.`")
                return
            await interaction.followup.send(f"*Looked at the items in the room **{str(currRoom.get_name())}**:*\n\n{allItems}")
            return

        if len(itemList) == 0:
            await interaction.followup.send(f"***{player.get_name()}** looked at the items in the room **{str(currRoom.get_name())}**:*\n\n`No items could be found in the room.`")
            return
        await interaction.followup.send(f"***{player.get_name()}** looked at the items in the room **{str(currRoom.get_name())}**:*\n\n{allItems}")
    #endregion
    #region /inventory
    @app_commands.command(name = "inventory", description = "List all of the items in your inventory.")
    async def inv(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        player = helpers.get_player_from_id(id)

        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake.*")
            return

        playerItems = player.get_items()

        if len(playerItems) == 0:
            await interaction.followup.send(f"***{player.get_name()}** looked into their inventory:*\n\n__`Weight`__: `0`/`{data.get_max_carry_weight()}`\n\n`No items found.`")
            return

        itemNames = [f"`{item.get_name()}` (weight: `{item.get_weight()}`)" for item in playerItems]
        allItems = '\n'.join(itemNames)
        await interaction.followup.send(f"***{player.get_name()}** looked into their inventory:*\n\n__`Weight`__: `{player.get_weight()}`/`{data.get_max_carry_weight()}`\n\n{allItems}")
    #endregion
    #region /clothes
    @app_commands.command(name = "clothes", description = "List all of the clothes you are currently wearing.")
    async def clothes(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        player = helpers.get_player_from_id(id)

        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake.*")
            return

        playerClothes = player.get_clothes()

        if len(playerClothes) == 0:
                await interaction.followup.send(f"***{player.get_name()}** looked at their clothes:*\n\n__`Weight`__: `0`/`{data.get_max_wear_weight()}`\n\n`No clothes found.`")
                return

        clothesNames: typing.List[str] = [
            f"`{clothes.get_name()}` (weight: `{clothes.get_weight()}`)" for clothes in playerClothes
        ]
        allClothes = '\n'.join(clothesNames)
        await interaction.followup.send(f"***{player.get_name()}** looked at their clothes:*\n\n__`Weight`__: `{player.get_clothes_weight()}`/`{data.get_max_wear_weight()}`\n\n{allClothes}")
    #endregion
    #region /objects
    @app_commands.command(name = "objects", description = "List all of the objects in the current room.")
    async def objects(self, interaction: discord.Interaction):
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

        objList = currRoom.get_objects()
        objNames = [f"`{obj.get_name()}`" for obj in objList]
        allObjs = ', '.join(objNames)

        if player is not None:
            if len(objList) == 0:
                await interaction.followup.send(f"***{player.get_name()}** looked at the objects in the room **{currRoom.get_name()}**:*\n\n`No objects found.`")
                return
            await interaction.followup.send(f"***{player.get_name()}** looked at the objects in the room **{currRoom.get_name()}**:*\n\n{allObjs}")
            return

        if len(objList) == 0:
            await interaction.followup.send(f"*Looked at the objects in the room **{currRoom.get_name()}**:*\n\n`No objects found.`")
            return
        await interaction.followup.send(f"*Looked at the objects in the room **{currRoom.get_name()}**:*\n\n{allObjs}")
    #endregion
    #region /contents
    @app_commands.command(name = "contents", description = "List all of the items inside of an object.")
    @app_commands.describe(object_name = "The name of the object you wish to look inside of.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete)
    async def contents(self, interaction: discord.Interaction, object_name: str):
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

        searchedObj = None
        for object in currRoom.get_objects():
            if helpers.simplify_string(object.get_name()) == helpers.simplify_string(object_name):
                searchedObj = object

        if searchedObj is None:
            await interaction.followup.send(f"*Could not find the object **{object_name}**. Please use `/objects` to see a list of all the objects in the current room.*")
            return

        is_display = searchedObj.get_display_state() if hasattr(searchedObj, "isDisplay") else False

        if not searchedObj.get_container_state():
            if player is not None:
                await interaction.followup.send(f"***{player.get_name()}** tried to look inside of the object **{searchedObj.get_name()}**, but it was not a container.*")
                return
            await interaction.followup.send(f"*Tried to look inside of the object **{searchedObj.get_name()}**, but it was not a container.*")
            return

        if searchedObj.get_locked_state() and not is_display:
            if player is not None:
                await interaction.followup.send(f"***{player.get_name()}** tried to look inside of the object **{searchedObj.get_name()}**, but it was locked.*")
                return
            await interaction.followup.send(f"*Tried to look inside of the object **{searchedObj.get_name()}**, but it was locked.*")
            return
            

        itemList = searchedObj.get_items()
        if len(itemList) == 0:
            if player is not None:
                await interaction.followup.send(f"***{player.get_name()}** looked inside of the object **{searchedObj.get_name()}**:*\n\n`No items could be found`.")
                return
            await interaction.followup.send(f"*Looked inside of the object **{searchedObj.get_name()}**:*\n\n`No items could be found`.")
            return

        itemNames = [f"`{item.get_name()}`" for item in itemList]
        allItems = ', '.join(itemNames)
        if player is not None:
            await interaction.followup.send(f"***{player.get_name()}** looked inside of the object **{searchedObj.get_name()}**:*\n\n{allItems}")
            return
        await interaction.followup.send(f"*Looked inside of the object **{searchedObj.get_name()}**:*\n\n{allItems}")
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
    #region /exits
    @app_commands.command(name = "exits", description = "List all locations that are connected to your current room.")
    async def exits(self, interaction: discord.Interaction):
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

        exits = currRoom.get_exits()

        if len(exits) == 0:
            await interaction.followup.send(f"***{player.get_name()}** looked at the exits in the room **{currRoom.get_name()}**:*\n\n`No exits found.`")
            return

        exitNames: typing.List[str] = []
        for exit in exits:
            currExit = ''
            if exit.get_room1() == currRoom.get_name():
                currExit = exit.get_room2()
            else:
                currExit = exit.get_room1()
            if exit.get_locked_state():
                currExit = f'{currExit} (Locked)'
            exitNames.append(f"`{currExit}`")

        allExits = ', '.join(exitNames)
        await interaction.followup.send(f"***{player.get_name()}** looked at the exits in the room **{currRoom.get_name()}**:*\n\n{allExits}")
    #endregion

async def setup(bot: commands.Bot):
    await bot.add_cog(ListCMDs(bot))
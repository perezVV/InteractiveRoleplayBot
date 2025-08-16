import typing

from discord.ext import commands
from discord import app_commands
import discord

import utils.data as data
import utils.helpers as helpers
import utils.autocompletes as autocompletes

class LockCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #region /lockobject
    @app_commands.command(name = "lockobject", description = "Lock an object in the current room using a key from your inventory.")
    @app_commands.describe(object_name = "The name of the object you wish to lock.")
    @app_commands.describe(key_name = "The name of the item in your inventory that can lock the object.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete, key_name=autocompletes.user_items_autocomplete)
    async def lockobject(self, interaction: discord.Interaction, object_name: str, key_name: str):
        await interaction.response.defer(thinking=True)
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        channel_id = interaction.channel_id
        currRoom = helpers.get_room_from_id(channel_id)

        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("You are not a valid player. Please contact an admin if you believe this is a mistake.")
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

        if not searchedObj.get_container_state():
            await interaction.followup.send(f"***{player.get_name()}** tried to lock **{searchedObj.get_name()}**, but it had no lock.*")
            return

        if searchedObj.get_locked_state():
            await interaction.followup.send(f"***{player.get_name()}** tried to lock the object **{searchedObj.get_name()}**, but it was already locked.*")
            return

        searchedItem = None

        itemList = player.get_items()
        for item in itemList:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(key_name):
                searchedItem = item

        if searchedItem is None:
            await interaction.followup.send(f"*Could not find the item **{key_name}**. Please use `/inventory` to see a list of all the items in your inventory.*")
            return

        if helpers.simplify_string(searchedObj.get_key_name()) == helpers.simplify_string(searchedItem.get_name()):
            searchedObj.switch_locked_state(True)
            data.save()
            await interaction.followup.send(f"***{player.get_name()}** locked the object **{searchedObj.get_name()}** using **{searchedItem.get_name()}**.*")
            return

        await interaction.followup.send(f"***{player.get_name()}** tried to lock the object **{searchedObj.get_name()}**, but **{searchedItem.get_name()}** was not the key.*")
        return
    #endregion
    #region /unlockobject
    @app_commands.command(name = "unlockobject", description = "Unlock an object in the current room using a key from your inventory.")
    @app_commands.describe(object_name = "The name of the object you wish to unlock.")
    @app_commands.describe(key_name = "The name of the item in your inventory that can unlock the object.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete, key_name=autocompletes.user_items_autocomplete)
    async def unlockobject(self, interaction: discord.Interaction, object_name: str, key_name: str):
        await interaction.response.defer(thinking=True)
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        channel_id = interaction.channel_id
        currRoom = helpers.get_room_from_id(channel_id)

        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact an admin if you believe this is a mistake.*")
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

        if not searchedObj.get_container_state():
            await interaction.followup.send(f"***{player.get_name()}** tried to unlock **{searchedObj.get_name()}**, but it had no lock.*")
            return

        if not searchedObj.get_locked_state():
            await interaction.followup.send(f"***{player.get_name()}** tried to unlock the object **{searchedObj.get_name()}**, but it was already unlocked.*")
            return

        searchedItem = None

        itemList = player.get_items()
        for item in itemList:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(key_name):
                searchedItem = item

        if searchedItem is None:
            await interaction.followup.send(f"*Could not find the item **{key_name}**. Please use `/inventory` to see a list of all the items in your inventory.*")
            return

        if helpers.simplify_string(searchedObj.get_key_name()) == helpers.simplify_string(searchedItem.get_name()):
            searchedObj.switch_locked_state(False)
            data.save()
            await interaction.followup.send(f"***{player.get_name()}** unlocked the object **{searchedObj.get_name()}** using **{searchedItem.get_name()}**.*")
            return

        await interaction.followup.send(f"***{player.get_name()}** tried to unlock the object **{searchedObj.get_name()}**, but **{searchedItem.get_name()}** was not the key.*")
        return
    #endregion
    #region /lockexit
    @app_commands.command(name = "lockexit", description = "Locks an exit that is connected to the current room using a key.")
    @app_commands.describe(exit_name = "The name of the exit you wish to lock.")
    @app_commands.describe(key_name = "The name of the item in your inventory that can lock the exit.")
    @app_commands.autocomplete(exit_name=autocompletes.exit_name_autocomplete, key_name=autocompletes.user_items_autocomplete)
    async def lockexit(self, interaction: discord.Interaction, exit_name: str, key_name: str):
        await interaction.response.defer(thinking=True)
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        channel_id = interaction.channel_id
        currRoom = helpers.get_room_from_id(channel_id)


        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake.*")
            return

        if currRoom is None:
            await interaction.followup.send("*You are not currently in a room. Please contact an admin if you believe this is a mistake.*")
            return
        
        room = helpers.get_room_from_name(exit_name)
        if room is None:
            await interaction.followup.send(f"*There is no exit to the room **{exit_name}** from **{currRoom.get_name()}**. Please use `/exits` to see a list of exits in the current room.*")
            return

        exits = currRoom.get_exits()

        if len(exits) == 0:
            await interaction.followup.send(f"*There are no exits in the room **{currRoom.get_name()}**.*")
            return

        searchedExit = None
        searchedExitName = ''
        for exit in exits:
            if helpers.simplify_string(exit_name) == helpers.simplify_string(exit.get_room1()):
                searchedExit = exit
                searchedExitName = exit.get_room1()
            elif helpers.simplify_string(exit_name) == helpers.simplify_string(exit.get_room2()):
                searchedExit = exit
                searchedExitName = exit.get_room2()

        if searchedExit is None:
            await interaction.followup.send(f"*There is no exit to the room **{exit_name}** from **{currRoom.get_name()}**. Please use `/exits` to see a list of exits in the current room.*")
            return

        if searchedExit.get_locked_state():
            await interaction.followup.send(f"***{player.get_name()}** tried to lock the exit to **{searchedExitName}**, but it was already locked.*")
            return

        searchedItem = None
        itemList = player.get_items()
        for item in itemList:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(key_name):
                searchedItem = item

        if searchedItem is None:
            await interaction.followup.send(f"*Could not find the item **{key_name}**. Please use `/inventory` to see a list of all the items in your inventory.*")
            return

        if helpers.simplify_string(searchedExit.get_key_name()) == helpers.simplify_string(searchedItem.get_name()):
            channel = self.bot.get_channel(int(room.get_id()))
            if channel is None:
                await interaction.followup.send(f"*Could not find the channel for **{exit_name}**. The room may need to be fixed — please contact an admin.*")

            searchedExit.switch_locked_state(True)
            data.save()
            await interaction.followup.send(f"***{player.get_name()}** locked the exit to **{searchedExitName}** using **{searchedItem.get_name()}***.")
            await channel.send(f"*The exit to **{currRoom.get_name()}** was locked.*")
            return

        await interaction.followup.send(f"***{player.get_name()}** tried to lock the exit to **{searchedExitName}**, but **{searchedItem.get_name()}** was not the key.*")
        return
    #endregion
    #region /unlockexit
    @app_commands.command(name = "unlockexit", description = "Unlocks an exit that is connected to the current room using a key.")
    @app_commands.describe(exit_name = "The name of the exit you wish to unlock.")
    @app_commands.describe(key_name = "The name of the item in your inventory that can unlock the exit.")
    @app_commands.autocomplete(exit_name=autocompletes.exit_name_autocomplete, key_name=autocompletes.user_items_autocomplete)
    async def unlockexit(self, interaction: discord.Interaction, exit_name: str, key_name: str):
        await interaction.response.defer(thinking=True)
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        channel_id = interaction.channel_id
        currRoom = helpers.get_room_from_id(channel_id)

        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake.*")
            return

        if currRoom is None:
            await interaction.followup.send("*You are not currently in a room. Please contact an admin if you believe this is a mistake.*")
            return
        
        room = helpers.get_room_from_name(exit_name)
        if room is None:
            await interaction.followup.send(f"*There is no exit to the room **{exit_name}** from **{currRoom.get_name()}**. Please use `/exits` to see a list of exits in the current room.*")
            return

        exits = currRoom.get_exits()

        if len(exits) == 0:
            await interaction.followup.send(f"*There are no exits in the room **{currRoom.get_name()}**.*")
            return

        searchedExit = None
        searchedExitName = ''
        for exit in exits:
            if helpers.simplify_string(exit_name) == helpers.simplify_string(exit.get_room1()):
                searchedExit = exit
                searchedExitName = exit.get_room1()
            elif helpers.simplify_string(exit_name) == helpers.simplify_string(exit.get_room2()):
                searchedExit = exit
                searchedExitName = exit.get_room2()

        if searchedExit is None:
            await interaction.followup.send(f"*There is no exit to the room **{exit_name}** from **{currRoom.get_name()}**. Please use `/exits` to see a list of exits in the current room.*")
            return

        if not searchedExit.get_locked_state():
            await interaction.followup.send(f"***{player.get_name()}** tried to unlock the exit to **{searchedExitName}**, but it was already unlocked.*")
            return

        searchedItem = None
        itemList = player.get_items()
        for item in itemList:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(key_name):
                searchedItem = item

        if searchedItem is None:
            await interaction.followup.send(f"*Could not find the item **{key_name}**. Please use `/inventory` to see a list of all the items in your inventory.*")
            return

        if helpers.simplify_string(searchedExit.get_key_name()) == helpers.simplify_string(searchedItem.get_name()):
            channel = self.bot.get_channel(int(room.get_id()))
            if channel is None:
                await interaction.followup.send(f"*Could not find the channel for **{exit_name}**. The room may need to be fixed — please contact an admin.*")

            searchedExit.switch_locked_state(False)
            data.save()
            await interaction.followup.send(f"***{player.get_name()}** unlocked the exit to **{searchedExitName}** using **{searchedItem.get_name()}***.")
            await channel.send(f"*The exit to **{currRoom.get_name()}** was unlocked.*")
            return

        await interaction.followup.send(f"***{player.get_name()}** tried to unlock the exit to **{searchedExitName}**, but **{searchedItem.get_name()}** was not the key.*")
        return
    #endregion

async def setup(bot: commands.Bot):
    await bot.add_cog(LockCMDs(bot))
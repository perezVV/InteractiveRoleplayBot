import typing

from discord.ext import commands
from discord import app_commands
import discord

import utils.data as data
import utils.autocompletes as autocompletes
import utils.helpers as helpers

class ObjectCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
    #region /lookobject
    @app_commands.command(name = "lookobject", description = "Get the description of a specific object in the current room.")
    @app_commands.describe(object_name = "The name of the object you wish to look at.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete)
    async def lookobject(self, interaction: discord.Interaction, object_name: str):
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

        if len(objList) == 0:
            await interaction.followup.send("*No objects could be found in the room.*")
            return

        searchedObj = None
        for obj in objList:
            if helpers.simplify_string(obj.get_name()) == helpers.simplify_string(object_name):
                searchedObj = obj

        if searchedObj is None:
            await interaction.followup.send(f"*Could not find the item **{object_name}**. Please use `/objects` to see a list of all the objects in the current room.*")
            return

        is_locked = 'Locked' if searchedObj.get_locked_state() else 'Opened'
        is_display = searchedObj.get_display_state() if hasattr(searchedObj, "isDisplay") else False

        storage_amt = ''
        used_storage = ''
        if searchedObj.get_storage() == -1:
            storage_amt = '∞'
        else:
            storage_amt = str(searchedObj.get_storage())

        used_storage = f'{len(searchedObj.get_items())}/'

        if player is not None:
            if searchedObj.get_container_state():
                if searchedObj.get_desc() == '':
                    await interaction.followup.send(
                        f"***{player.get_name()}** looked at the object **{searchedObj.get_name()}**:*\n\n__`{searchedObj.get_name()}`__\n\n__`Storage`__: `{used_storage}{storage_amt}`\n__`State`__: `{is_locked}`\n__`Display`__: `{is_display}`\n\n`Object has no description.`"
                    )
                    return
                await interaction.followup.send(
                    f"***{player.get_name()}** looked at the object **{searchedObj.get_name()}**:*\n\n__`{searchedObj.get_name()}`__\n\n__`Storage`__: `{used_storage}{storage_amt}`\n__`State`__: `{is_locked}`\n__`Display`__: `{is_display}`\n\n{searchedObj.get_desc()}"
                )
                return
            if searchedObj.get_desc() == '':
                await interaction.followup.send(f"***{player.get_name()}** looked at the object **{searchedObj.get_name()}**:*\n\n__`{searchedObj.get_name()}`__\n\n`Object has no description.`")
                return
            await interaction.followup.send(f"***{player.get_name()}** looked at the object **{searchedObj.get_name()}**:*\n\n__`{searchedObj.get_name()}`__\n\n{searchedObj.get_desc()}")
            return

        containerState = searchedObj.get_container_state()
        if containerState == True:
            if searchedObj.get_desc() == '':
                await interaction.followup.send(
                    f"*Looked at the object **{searchedObj.get_name()}**:*\n\n__`{searchedObj.get_name()}`__\n\n__`Storage`__: `{storage_amt}`\n__`State`__: `{is_locked}`\n__`Display`__: `{is_display}`\n\n`Object has no description.`"
                )
                return
            await interaction.followup.send(
                f"*Looked at the object **{searchedObj.get_name()}**:*\n\n__`{searchedObj.get_name()}`__\n\n__`Storage`__: `{storage_amt}`\n__`State`__: `{is_locked}`\n__`Display`__: `{is_display}`\n\n{searchedObj.get_desc()}"
            )
            return

        if searchedObj.get_desc() == '':
            await interaction.followup.send(f"*Looked at the object **{searchedObj.get_name()}**:*\n\n__`{searchedObj.get_name()}`__\n\n`Object has no description.`")
            return
        await interaction.followup.send(f"*Looked at the object **{searchedObj.get_name()}**:*\n\n__`{searchedObj.get_name()}`__\n\n{searchedObj.get_desc()}")
        return
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
    #region /lookinside
    @app_commands.command(name = "lookinside", description = "Get the description of a specific item in an object.")
    @app_commands.describe(object_name = "The name of the object you wish to look inside of.")
    @app_commands.describe(item_name = "The name of the item you wish to look at.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete, item_name=autocompletes.object_contents_autocomplete)
    async def lookinside(self, interaction: discord.Interaction, object_name: str, item_name: str):
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
            await interaction.followup.send(f"*No items could be found in the object **{searchedObj.get_name()}**.*")
            return

        searchedItem = None
        for item in itemList:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(item_name):
                searchedItem = item

        if searchedItem is None:
            await interaction.followup.send(f"*Could not find the item **{item_name}** inside of the object **{searchedObj.get_name()}**. Please use `/contents` to see a list of all the items in an object.*")
            return

        if player is not None:
            if searchedItem.get_desc() == '':
                await interaction.followup.send(f"***{player.get_name()}** looked inside of the object **{searchedObj.get_name()}** at the item **{searchedItem.get_name()}**:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{searchedItem.get_weight()}`\n\n__`Wearable`__: `{searchedItem.get_wearable_state()}`\n\n`Item has no description.`")
            else:
                await interaction.followup.send(f"***{player.get_name()}** looked inside of the object **{searchedObj.get_name()}** at the item **{searchedItem.get_name()}**:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{searchedItem.get_weight()}`\n\n__`Wearable`__: `{searchedItem.get_wearable_state()}`\n\n{searchedItem.get_desc()}")
                return
        
            return
        
        if searchedItem.get_desc() == '':
            await interaction.followup.send(f"*Looked inside of the object **{searchedObj.get_name()}** at the item **{searchedItem.get_name()}**:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{searchedItem.get_weight()}`\n\n__`Wearable`__: `{searchedItem.get_wearable_state()}`\n\n`Item has no description.`")
            return

        await interaction.followup.send(f"*Looked inside of the object **{searchedObj.get_name()}** at the item **{searchedItem.get_name()}**:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{searchedItem.get_weight()}`\n\n__`Wearable`__: `{searchedItem.get_wearable_state()}`\n\n{searchedItem.get_desc()}")
    #endregion

async def setup(bot: commands.Bot):
    await bot.add_cog(ObjectCMDs(bot))
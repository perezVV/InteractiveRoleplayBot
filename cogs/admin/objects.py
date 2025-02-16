import typing

from discord.ext import commands
from discord import app_commands
import discord

import utils.autocompletes as autocompletes
import utils.helpers as helpers
import utils.data as data

class AdminObjectsCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #region /addobject 
    @app_commands.command(name = "addobject", description = "Add an object into a room.")
    @app_commands.describe(room_name = "The room you wish to add the object to.")
    @app_commands.describe(object_name = "The name of the object you wish to add to the room.")
    @app_commands.describe(is_container = "True or false; whether or not you wish the object to be able to store items.")
    @app_commands.describe(is_locked = "True or false; whether or not you wish the object to be locked.")
    @app_commands.describe(key_name = "The name of the item you wish to be able lock and unlock the object.")
    @app_commands.describe(storage = "The max amount of items you wish to be able to store in the object. If left blank, there will be no maximum.")
    @app_commands.describe(desc = "The description of the object you wish to add to the room.")
    @app_commands.default_permissions()
    async def addobject(self, interaction: discord.Interaction, room_name: str, object_name: str, is_container: bool, is_locked: bool = False, key_name: str = '', storage: int = -1, desc: str = ''):
        await interaction.response.defer(thinking=True)

        room = helpers.get_room_from_name(room_name)

        if room is None:
            await interaction.followup.send(f"*Room **{room_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
            return
        
        object: data.Object = data.Object(object_name, is_container, is_locked, key_name, storage, desc)
        room.add_object(object)

        data.save()
        await interaction.followup.send(f"*Added the object **{object_name}** to the room **{room.get_name()}**.*")
    #endregion
    #region /delobject 
    @app_commands.command(name = "delobject", description = "Delete an object in a room.")
    @app_commands.describe(room_name = "The room you wish to add the object to.")
    @app_commands.describe(object_name = "The name of the object you wish to add to the room.")
    @app_commands.autocomplete(room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.autocomplete(object_name=autocompletes.admin_object_autocomplete)
    @app_commands.default_permissions()
    async def delobject(self, interaction: discord.Interaction, room_name: str, object_name: str):
        await interaction.response.defer(thinking=True)

        room = helpers.get_room_from_name(room_name)

        if room is None:
            await interaction.followup.send(f"*Room **{room_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
            return
        
        objList = room.get_objects()

        if len(objList) == 0:
            await interaction.followup.send("*No objects could be found in that room.*")
            return
        
        searchedObj = None
        for obj in objList:
            if helpers.simplify_string(obj.get_name()) == helpers.simplify_string(object_name):
                searchedObj = obj
        
        if searchedObj is None:
            await interaction.followup.send(f"*Could not find the item **{object_name}**. Please use `/objects` in <#{room.get_id()}> to see a list of all the objects in that room.*")
            return

        room.del_object(searchedObj)

        data.save()
        await interaction.followup.send(f"*Deleted the object **{searchedObj.get_name()}** from the room **{room.get_name()}**.*")
    #endregion
    #region /listobjects
    @app_commands.command(name = "listobjects", description = "List all of the objects in a room.")
    @app_commands.describe(room_name = "The room that you wish to see the objects of.")
    @app_commands.default_permissions()
    async def listobjects(self, interaction: discord.Interaction, room_name: str):
        await interaction.response.defer(thinking=True)
        currRoom = helpers.get_room_from_name(room_name)

        if currRoom is None:
            await interaction.followup.send(f"*Could not find the room **{room_name}**. Please use `/listrooms` to see a list of all current rooms.*")
            return

        objList = currRoom.get_objects()
        objNames = [f"`{obj.get_name()}`" for obj in objList]
        allObjs = ', '.join(objNames)

        if len(objList) == 0:
            await interaction.followup.send(f"*Looked at the objects in the room **{currRoom.get_name()}**:*\n\n`No objects found.`")
            return
        
        await interaction.followup.send(f"*Looked at the objects in the room **{currRoom.get_name()}**:*\n\n{allObjs}")
    #endregion
    #region /seeobject
    @app_commands.command(name = "seeobject", description = "Get the description of a specific object from anywhere.")
    @app_commands.describe(room_name = "The room of the object you wish to look at.")
    @app_commands.describe(object_name = "The name of the object you wish to look at.")
    @app_commands.autocomplete(room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.autocomplete(object_name=autocompletes.admin_object_autocomplete)
    @app_commands.default_permissions()
    async def seeobject(self, interaction: discord.Interaction, room_name: str, object_name: str):
        await interaction.response.defer(thinking=True)
        currRoom = helpers.get_room_from_name(room_name)

        if currRoom is None:
            await interaction.followup.send(f"*Room **{room_name}** could not be found. Please use `/listrooms` to see a list of all current rooms.*")
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

        storage_amt = ''
        used_storage = ''
        if searchedObj.get_storage() == -1:
            storage_amt = '∞'
        else:
            storage_amt = str(searchedObj.get_storage())

        used_storage = f'{len(searchedObj.get_items())}/'

        keyName = str(searchedObj.get_key_name()) or "None"

        if searchedObj.get_desc() == '':
            await interaction.followup.send(
                f"*Looked at the object **{searchedObj.get_name()}**:*\n\n__`{searchedObj.get_name()}`__\n\n__`Storage`__: `{used_storage}{storage_amt}`\n__`State`__: `{is_locked}`\n__`Key Name`__: `{keyName}`\n\n`Object has no description.`"
            )
            return

        await interaction.followup.send(
            f"*Looked at the object **{searchedObj.get_name()}**:*\n\n__`{searchedObj.get_name()}`__\n\n__`Storage`__: `{used_storage}{storage_amt}`\n__`State`__: `{is_locked}`\n__`Key Name`__: `{keyName}`\n\n{searchedObj.get_desc()}"
        )
        return
    #endregion
    #region /editobject
    @app_commands.command(name = "editobject", description = "Edit the value of an object.")
    @app_commands.describe(room_name = "The room of the object you wish to edit.")
    @app_commands.describe(object_name = "The name of the object you wish to edit.")
    @app_commands.describe(new_name = "The new name of the object.")
    @app_commands.describe(new_desc = "The new description of the object.")
    @app_commands.describe(new_container_state = "Whether the object is a container or not.")
    @app_commands.describe(new_locked_state = "Whether the object is locked or not.")
    @app_commands.describe(new_key = "The name of the key for the object.")
    @app_commands.describe(new_storage = "The new amount of items that can fit into the object. If infinite, input -1.")
    @app_commands.autocomplete(room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.autocomplete(object_name=autocompletes.admin_object_autocomplete)
    @app_commands.default_permissions()
    async def editobject(self, interaction: discord.Interaction, room_name: str, object_name: str, new_name: str = '', new_desc: str = '', new_container_state: bool = None, new_locked_state: bool = None, new_key: str = '', new_storage: int = -2):
        await interaction.response.defer(thinking=True)
        currRoom = helpers.get_room_from_name(room_name)

        if new_storage <= -3:
            await interaction.followup.send(
                f"***{new_storage}** is an invalid storage input; please use a positive number or -1 for infinity.*"
            )
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

        if (
            not new_name
            and not new_desc
            and new_container_state is None
            and new_locked_state is None
            and not new_key
            and new_storage == -2
        ):
            await interaction.followup.send(
                "*Please select an option and enter a new value to edit an exit.*"
            )
            return

        output_str: typing.List[str] = []
        if new_name != '':
            searchedObj.edit_name(new_name)
            output_str.append("name")
        if new_desc != '':
            searchedObj.edit_desc(new_desc)
            output_str.append("description")
        if new_container_state != None:
            searchedObj.switch_container_state(new_container_state)
            output_str.append("container state")
        if new_locked_state != None:
            searchedObj.switch_locked_state(new_locked_state)
            output_str.append("locked state")
        if new_key != '':
            searchedObj.edit_key_name(new_key)
            output_str.append("key name")
        if new_storage != -2:
            searchedObj.set_storage(new_storage)
            output_str.append("storage")

        edited = ''
        if not output_str:
            edited = ''
        elif len(output_str) == 1:
            edited = output_str[0]
        elif len(output_str) == 2:
            edited = f"{output_str[0]} and {output_str[1]}"
        else:
            edited = ", ".join(output_str[:-1]) + f", and {output_str[-1]}"

        data.save()
        await interaction.followup.send(f"*Changed the object **{searchedObj.get_name()}**'s {edited}.*")
    #endregion

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminObjectsCMDs(bot))
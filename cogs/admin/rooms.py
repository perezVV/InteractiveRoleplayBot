import typing

from discord.ext import commands
from discord import app_commands
import discord

import utils.autocompletes as autocompletes
import utils.helpers as helpers
import utils.data as data

class AdminRoomCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #region /addroom
    @app_commands.command(name = "addroom", description = "Add a room to the experience.")
    @app_commands.describe(room_name = "The name of the room you wish to create.")
    @app_commands.describe(room_id = "The Discord ID of the channel you wish to connect the room to.")
    @app_commands.describe(desc = "The description of the room you wish to add to the experience.")
    @app_commands.default_permissions()
    async def addroom(self, interaction: discord.Interaction, room_name: str, room_id: str, desc: str = ''):
        await interaction.response.defer(thinking=True)

        try:
            room_id = int(room_id)
        except ValueError:
            await interaction.followup.send("*A room ID must be made up entirely of integers. Please enter a valid room ID.*")
            return

        if interaction.guild.get_channel(room_id) is None:
            await interaction.followup.send(f"*Could not find the channel <#{room_id}>.*")
            return

        for room in data.roomdata.values():
            if helpers.simplify_string(room_name) == helpers.simplify_string(room.get_name()):
                await interaction.followup.send(f"*Room name **{room_name}** is already in use. Please give the room a separate name.*")
                return
            if room.get_id() == room_id:
                await interaction.followup.send(
                    f"*The channel <#{room_id}> is already in use. Please give the room a separate channel.*"
                )
                return

        data.roomdata[room_name] = data.Room(room_name, room_id, desc)
        channel = self.bot.get_channel(room_id)
        if (desc != ''):
            await channel.edit(topic=desc)
        data.save()

        await interaction.followup.send(
            f"*Room **{room_name}** connected to <#{room_id}>.*"
        )
    #endregion
    #region /delroom
    @app_commands.command(name = "delroom", description = "Remove a room from the experience.")
    @app_commands.describe(room_name = "The name of the room you wish to remove.")
    @app_commands.autocomplete(room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.default_permissions()
    async def delroom(self, interaction: discord.Interaction, room_name: str):
        await interaction.response.defer(thinking=True)
        simplified_room = helpers.simplify_string(room_name)
        simplified_keys = {helpers.simplify_string(key): key for key in data.roomdata.keys()}
        if simplified_room in simplified_keys:
            original_key = simplified_keys[simplified_room]
            try:
                del data.roomdata[original_key]
                for room in data.roomdata.values():
                    exits = room.get_exits()
                    for exit in exits:
                        if exit.get_room1() == original_key or exit.get_room2() == original_key:
                            room.del_exit(exit)
                data.save()
                await interaction.followup.send(f"*Deleted room **{original_key}**.*")
                return
            except Exception:
                await interaction.followup.send(f"*Failed to delete room **{original_key}**. Please contact the bot's developer.*")
                return
        
        else:
            await interaction.followup.send(f"*Could not find room **{room_name}**. Please use `/listrooms` to see all current rooms.*")
    #endregion
    #region /listrooms
    @app_commands.command(name = "listrooms", description = "List all rooms that have been added to the experience.")
    @app_commands.default_permissions()
    async def listrooms(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        if len(data.roomdata) == 0:
            await interaction.followup.send("There are currently no rooms.")
            return
        
        roomList = ''
        for key in data.roomdata:
            currRoom = data.roomdata[key]
            nextRoom = ("`", currRoom.get_name(), "`: <#", str(currRoom.get_id()), ">.")
            nextRoom = ''.join(nextRoom)
            roomList = roomList + "\n" + nextRoom
        
        await interaction.followup.send(roomList)
    #endregion
    #region /addexit
    @app_commands.command(name = "addexit", description = "Add a connection between two rooms.")
    @app_commands.describe(first_room_name = "The first of the two rooms you wish to add a connection between.")
    @app_commands.describe(second_room_name = "The second of the two rooms you wish to add a connection between.")
    @app_commands.describe(is_locked = "True or false; whether or not you wish the exit to be locked.")
    @app_commands.describe(key_name = "The name of the item you wish to be able lock and unlock the exit.")
    @app_commands.autocomplete(first_room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.autocomplete(second_room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.default_permissions()
    async def addexit(self, interaction: discord.Interaction, first_room_name: str, second_room_name: str, is_locked: bool = False, key_name: str = ''):
        await interaction.response.defer(thinking=True)

        room_one = helpers.get_room_from_name(first_room_name)
        room_two = helpers.get_room_from_name(second_room_name)

        if room_one is None:
            await interaction.followup.send(f"*Room **{first_room_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
            return
        if room_two is None:
            await interaction.followup.send(f"*Room **{second_room_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
            return

        for exit in room_one.get_exits():
            if helpers.simplify_string(exit.get_room1()) == helpers.simplify_string(room_one.get_name()):
                if helpers.simplify_string(exit.get_room2()) == helpers.simplify_string(room_two.get_name()):
                    await interaction.followup.send(f"*Connection from **{room_one.get_name()}** to **{room_two.get_name()}** already exists. Please use `/editexit` if you would like to change it.*")
                    return
            elif helpers.simplify_string(exit.get_room1()) == helpers.simplify_string(room_two.get_name()):
                if helpers.simplify_string(exit.get_room2()) == helpers.simplify_string(room_one.get_name()):
                    await interaction.followup.send(f"*Connection from **{room_one.get_name()}** to **{room_two.get_name()}** already exists. Please use `/editexit` if you would like to change it.*")
                    return

        exit: data.Exit = data.Exit(room_one.get_name(), room_two.get_name(), is_locked, key_name)

        room_one.add_exit(exit)
        room_two.add_exit(exit)

        data.save()

        await interaction.followup.send(f"*Connection created between **{room_one.get_name()}** and **{room_two.get_name()}**.*")
    #endregion 
    #region /delexit
    @app_commands.command(name = "delexit", description = "Delete a connection between two rooms.")
    @app_commands.describe(room_one_name = "The first of the two rooms you wish to add a connection between.")
    @app_commands.describe(room_two_name = "The second of the two rooms you wish to add a connection between.")
    @app_commands.autocomplete(room_one_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.autocomplete(room_two_name=autocompletes.admin_exit_autocomplete)
    @app_commands.default_permissions()
    async def delexit(self, interaction: discord.Interaction, room_one_name: str, room_two_name: str):
        await interaction.response.defer(thinking=True)

        simplified_room_one = helpers.simplify_string(room_one_name)
        simplified_room_two = helpers.simplify_string(room_two_name)
        simplified_keys = {helpers.simplify_string(key): key for key in data.roomdata.keys()}

        if simplified_room_one not in simplified_keys:
            await interaction.followup.send(f"*Room **{room_one_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
            return
        if simplified_room_two not in simplified_keys:
            await interaction.followup.send(f"*Room **{room_two_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
            return

        room_one = helpers.get_room_from_name(simplified_room_one)
        room_two = helpers.get_room_from_name(simplified_room_two)
        original_room_one = simplified_keys[simplified_room_one]
        original_room_two = simplified_keys[simplified_room_two]

        exitsOne = room_one.get_exits()
        exitsTwo = room_two.get_exits()

        if len(exitsOne) == 0:
            await interaction.followup.send(f"*There are no exits in the room **{str(room_one.get_name())}**.*")
            return
        if len(exitsTwo) == 0:
            await interaction.followup.send(f"*There are no exits in the room **{str(room_two.get_name())}**.*")
            return

        exit = None
        for exit in exitsOne:
            if exit.get_room1() == room_two.get_name():
                if helpers.simplify_string(exit.get_room2()) == helpers.simplify_string(room_one_name):
                    exit = exit
                    break
            elif exit.get_room1() == room_one.get_name():
                if helpers.simplify_string(exit.get_room2()) == helpers.simplify_string(room_two_name):
                    exit = exit
                    break

        room_one.del_exit(exit)
        room_two.del_exit(exit)

        data.save()

        await interaction.followup.send(f"*Connection removed between **{original_room_one}** and **{original_room_two}**.*")
    #endregion 
    #region /findroom 
    @app_commands.command(name = "findroom", description = "Tells what channel is connected to a room.")
    @app_commands.describe(room_name = "The name of the room you wish to find.")
    @app_commands.default_permissions()
    async def findroom(self, interaction: discord.Interaction, room_name: str):
        await interaction.response.defer(thinking=True)

        room = helpers.get_room_from_name(room_name)

        if room is None:
            await interaction.followup.send(f"*Could not find the room **{room_name}***")
            return

        await interaction.followup.send(
            f"`{room.get_name()}`: <#{str(room.get_id())}>"
        )
    #endregion
    #region /listexits
    @app_commands.command(name = "listexits", description = "List all locations that are connected to a room.")
    @app_commands.describe(room_name = "The name of the room you wish to see the exits of.")
    @app_commands.default_permissions()
    async def listexits(self, interaction: discord.Interaction, room_name: str):
        await interaction.response.defer(thinking=True)
        currRoom = helpers.get_room_from_name(room_name)

        if currRoom is None:
            await interaction.followup.send(f"*Could not find the room **{room_name}**. Please use `/listrooms` to see a list of all current rooms.*")
            return

        exits = currRoom.get_exits()

        if len(exits) == 0:
            await interaction.followup.send(f"*Looked at the exits in the room **{currRoom.get_name()}**:*\n\n`No exits found.`")
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
        await interaction.followup.send(f"*Looked at the exits in the room **{currRoom.get_name()}**:*\n\n{allExits}")
    #endregion
    #region /seeexit
    @app_commands.command(name = "seeexit", description = "Get the locked state of any exit.")
    @app_commands.describe(room_one_name = "The first room of the exit.")
    @app_commands.describe(room_two_name = "The second room of the exit.")
    @app_commands.autocomplete(room_one_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.autocomplete(room_two_name=autocompletes.admin_exit_autocomplete)
    @app_commands.default_permissions()
    async def seeexit(self,interaction: discord.Interaction, room_one_name: str, room_two_name: str):
        await interaction.response.defer(thinking=True)
        room_one = helpers.get_room_from_name(room_one_name)
        room_two = helpers.get_room_from_name(room_two_name)

        if room_one is None:
            await interaction.followup.send(f"*Could not find the room **{room_one_name}**. Please use `/listrooms` to see a list of all current rooms.")
            return

        if room_two is None:
            await interaction.followup.send(f"*Could not find the room **{room_two_name}**. Please use `/listrooms` to see a list of all current rooms.")
            return

        exitsOne = room_one.get_exits()
        exitsTwo = room_two.get_exits()

        if len(exitsOne) == 0:
            await interaction.followup.send(f"*There are no exits in the room **{str(room_one.get_name())}**.*")
            return
        if len(exitsTwo) == 0:
            await interaction.followup.send(f"*There are no exits in the room **{str(room_two.get_name())}**.*")
            return

        exit = None
        for exit in exitsOne:
            if exit.get_room1() == room_one.get_name():
                if helpers.simplify_string(exit.get_room2()) == helpers.simplify_string(room_one_name):
                    exit = exit
            elif helpers.simplify_string(exit.get_room1()) == helpers.simplify_string(room_one_name):
                exit = exit

        isLocked = ''
        isLocked = 'locked' if exit.get_locked_state() else 'opened'
        
        if exit.get_key_name() == '':
            hasKey = "has no key"
        else:
            hasKey = (f"can be locked or unlocked using the key **{exit.get_key_name()}**")

        await interaction.followup.send(f"*The connection between **{room_one.get_name()}** and **{room_two.get_name()}** is **{isLocked}** and {hasKey}.*")
    #endregion
    #region /editroom
    @app_commands.command(name = "editroom", description = "Edit the value of a room.")
    @app_commands.describe(room_name = "The room you wish to edit.")
    @app_commands.describe(new_name = "The new name you wish to give the room.")
    @app_commands.describe(new_desc = "The new description you wish to give the room.")
    @app_commands.autocomplete(room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.default_permissions()
    async def editroom(self, interaction: discord.Interaction, room_name: str, new_name: str = '', new_desc: str = ''):
        await interaction.response.defer(thinking=True)
        room = helpers.get_room_from_name(room_name)

        if room is None:
            await interaction.followup.send(f"*Could not find the room **{room_name}**. Please use `/listrooms` to get a list of the current rooms.*")
            return

        room_id = room.get_id()

        edited = ''

        if new_name != '':
            old_name = room.get_name()
            exits = room.get_exits()
            for exit in exits:
                if exit.get_room1() == room.get_name():
                    exit.edit_room1(new_name)
                elif exit.get_room2() == room.get_name():
                    exit.edit_room2(new_name)
            room.edit_name(new_name)
            data.roomdata[new_name] = data.roomdata[old_name]
            del data.roomdata[old_name]
            edited += f" name to **{new_name}**"
        if new_desc != '':
            room.edit_desc(new_desc)
            channel = self.bot.get_channel(int(room_id))
            await channel.edit(topic=new_desc)
            if edited == '':
                edited = f'{edited} description'
            else:
                edited = f'{edited} and edited its description'

        edited = f"{edited}."

        if not new_name and not new_desc:
            await interaction.followup.send(f"*Please enter a value for either `new_name` or `new_desc` to edit the room **{room.get_name}**.*")
            return

        data.save()
        await interaction.followup.send(f"*Changed <#{room_id}>'s room{edited}*")
    #endregion
    #region /editexit
    @app_commands.command(name = "editexit", description = "Edit the value of an exit.")
    @app_commands.describe(room_one_name = "The first room of the exit.")
    @app_commands.describe(room_two_name = "The second room of the exit.")
    @app_commands.describe(new_locked_state = "The new locked state of the exit.")
    @app_commands.describe(new_key = "The new key for the exit.")
    @app_commands.autocomplete(room_one_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.autocomplete(room_two_name=autocompletes.admin_exit_autocomplete)
    @app_commands.default_permissions()
    async def editexit(self, interaction: discord.Interaction, room_one_name: str, room_two_name: str, new_locked_state: bool = None, new_key: str = ''):
        await interaction.response.defer(thinking=True)
        room_one = helpers.get_room_from_name(room_one_name)
        room_two = helpers.get_room_from_name(room_two_name)

        if room_one is None:
            await interaction.followup.send(f"*Could not find the room **{room_one_name}**. Please use `/listrooms` to see a list of all current rooms.*")
            return

        if room_two is None:
            await interaction.followup.send(f"*Could not find the room **{room_two_name}**. Please use `/listrooms` to see a list of all current rooms.*")
            return

        exitsOne = room_one.get_exits()
        exitsTwo = room_two.get_exits()

        if len(exitsOne) == 0:
            await interaction.followup.send(f"*There are no exits in the room **{str(room_one.get_name())}**.*")
            return
        if len(exitsTwo) == 0:
            await interaction.followup.send(f"*There are no exits in the room **{str(room_two.get_name())}**.*")
            return

        exit = None
        for exit in exitsOne:
            if exit.get_room1() == room_two.get_name():
                if helpers.simplify_string(exit.get_room2()) == helpers.simplify_string(room_one_name):
                    exit = exit
                    break
            elif exit.get_room1() == room_one.get_name():
                if helpers.simplify_string(exit.get_room2()) == helpers.simplify_string(room_two_name):
                    exit = exit
                    break

        if new_locked_state is None and not new_key:
            await interaction.followup.send(
                "*Please select an option and enter a new value to edit an exit.*"
            )
            return

        ouput_strs: typing.List[str] = []
        if new_locked_state != None:
            exit.switch_locked_state(new_locked_state)
            ouput_strs.append("locked state")
        if new_key != '':
            exit.edit_key_name(new_key)
            ouput_strs.append("key name")

        edited = ''
        if not ouput_strs:
            edited = ''
        elif len(ouput_strs) == 1:
            edited = ouput_strs[0]
        else:
            edited = f"{ouput_strs[0]} and {ouput_strs[1]}"

        data.save()
        await interaction.followup.send(f"*Changed the exit between **{room_one.get_name()}** and **{room_two.get_name()}**'s {edited}.*")
    #endregion

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminRoomCMDs(bot))
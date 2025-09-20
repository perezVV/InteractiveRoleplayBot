import typing

from discord.ext import commands
from discord import app_commands
import discord

import utils.data as data
import utils.helpers as helpers
import utils.autocompletes as autocompletes

class RoomCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #region /desc
    @app_commands.command(name = "desc", description = "Get the room's description.")
    async def desc(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        channel_id = interaction.channel_id
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        room = helpers.get_room_from_id(channel_id)

        if await helpers.check_paused(player, interaction):
            return

        if room is None:
            await interaction.followup.send("*You are not currently in a room. Please contact an admin if you believe this is a mistake*.")
            return

        lookedAt = f"Looked around the room **{room.get_name()}**"
        topic = interaction.channel.topic

        if player is not None:
            lookedAt = f"**{player.get_name()}** looked around the room **{room.get_name()}**"
        if topic is None:
            topic = f"`{room.get_name()} has no description.`"

        await interaction.followup.send(f"*{lookedAt}*:\n\n{topic}")
#endregion
    #region /goto
    @app_commands.command(name = "goto", description = "Move to the room that you specify.")
    @app_commands.describe(room_name = "The name of the room you wish the move to.")
    @app_commands.autocomplete(room_name=autocompletes.exit_name_autocomplete)
    async def goto(self, interaction: discord.Interaction, room_name: str):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        currRoom = None

        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake.*")
            return

        room = helpers.get_room_from_name(room_name)

        if room_name is None or room_name.startswith("\\"):
            await interaction.followup.send(f"*You did not enter a valid room name. Please use `/exits` to see a list of exits in the current room.*")
            return

        if room is None:
            await interaction.followup.send(f"*Could not find the exit **{room_name}**. Please use `/exits` to see a list of exits in the current room.*")
            return

        for newRoom in data.roomdata.values():
            if newRoom.get_id() == channel_id:
                currRoom = newRoom

        if currRoom is None:
            await interaction.followup.send(
                "*You are not currently in a room. Please contact an admin if you believe this is a mistake.*"
            )
            return

        exits = currRoom.get_exits()

        if len(exits) == 0:
            await interaction.followup.send(f"*There are no exits in the room **{str(currRoom.get_name())}**.*")
            return

        currExitName = None
        currExit = None
        for exit in exits:
            if exit.get_room1() == currRoom.get_name():
                if helpers.simplify_string(exit.get_room2()) == helpers.simplify_string(room_name):
                    currExitName = exit.get_room2()
                    currExit = exit
            else:
                if helpers.simplify_string(exit.get_room1()) == helpers.simplify_string(room_name):
                    currExitName = exit.get_room1()
                    currExit = exit

        if currExitName is None:
            await interaction.followup.send(f"*There is no exit to the room **{room_name}** from **{currRoom.get_name()}**. Please use `/exits` to see a list of exits in the current room.*")
            return

        if currExit.get_locked_state():
            await interaction.followup.send(f"***{player.get_name()}** tried to enter the room **{currExitName}**, but the exit was locked.*")
            return

        player.set_room(room)
        data.save()

        currChannel = self.bot.get_channel(int(currRoom.get_id()))

        channel = self.bot.get_channel(int(room.get_id()))
        user = self.bot.get_user(int(player.get_id()))

        if channel is None:
            await interaction.followup.send(f"*Could not find the channel for **{room_name}**. The room may need to be fixed — please contact an admin.*")

        if currRoom is not None and currChannel is None:
            await interaction.followup.send(f"*Could not find the channel for **{currChannel.get_name()}**. The room may need to be fixed — please contact an admin.*")

        if user is None:
            await interaction.followup.send(f"*Could not find the user <@{player.get_id()}>. The player may need to be fixed — please contact an admin.*")

        await interaction.followup.send(f"***{player.get_name()}** moved to **{currExitName}**.*")

        if currChannel is not None:
            await channel.send(f"***{player.get_name()}** entered from **{currRoom.get_name()}**.*")
        else:
            await channel.send(f"***{player.get_name()}** entered.*")

        if currChannel is not None:
            await currChannel.set_permissions(user, read_messages = None)

        await channel.set_permissions(user, read_messages = True)
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
    #region /take
    @app_commands.command(name = "take", description = "Take an item from the room.")
    @app_commands.describe(item_name = "The item you wish to take.")
    @app_commands.describe(amount = "The amount of that item you wish to take.")
    @app_commands.autocomplete(item_name=autocompletes.room_items_autocomplete)
    async def take(self, interaction: discord.Interaction, item_name: str, amount: int = 0):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        currRoom = helpers.get_room_from_id(channel_id)

        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake*.")
            return

        if currRoom is None:
            await interaction.followup.send("*You are not currently in a room. Please contact an admin if you believe this is a mistake*.")
            return

        invWeight = player.get_weight()
        itemList = currRoom.get_items()

        if amount in {0, 1}:
            for item in itemList:
                if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                    if (invWeight + item.get_weight()) > data.get_max_carry_weight():
                        await interaction.followup.send(f"***{player.get_name()}** tried to take the item **{item.get_name()}**, but they could not fit it into their inventory.*")
                        return
                    player.add_item(item)
                    currRoom.del_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** took the item **{item.get_name()}***.")
                    return
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/items` to see a list of items in the current room.*")
            return

        if amount < 0:
            await interaction.followup.send(
                f"***{amount}** is an invalid input; please use a positive number.*"
            )
            return

        itemsFound: typing.List[data.Item] = []
        searchedItem = None
        for item in itemList:
            if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                searchedItem = item
                itemsFound.append(searchedItem)

        if not itemsFound or not searchedItem:
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/items` to see a list of items in the current room.*")
            return
        
        if len(itemsFound) < amount:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}**. Please use `/items` to see a list of items in the current room.*"
            )
            return
        
        try:
            newCarryWeight = sum(itemsFound[i].get_weight() for i in range(amount))
            if (invWeight + newCarryWeight) > data.get_max_carry_weight():
                await interaction.followup.send(
                    f"***{player.get_name()}** tried to take **{amount}** of the item **{searchedItem.get_name()}**, but they could not fit that much into their inventory.*"
                )
                return
            for i in range(amount):
                player.add_item(itemsFound[i])
                currRoom.del_item(itemsFound[i])
            data.save()
            await interaction.followup.send(
                f"***{player.get_name()}** took **{amount}** of the item **{searchedItem.get_name()}***."
            )
            return
        except Exception:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}**. Please use `/items` to see a list of items in the current room.*"
            )
            return
    #endregion
    #region /takewear
    @app_commands.command(name = "takewear", description = "Take a clothing item from the room and wear it.")
    @app_commands.describe(item_name = "The clothing item you wish to wear.")
    @app_commands.autocomplete(item_name=autocompletes.room_items_autocomplete)
    async def takewear(self, interaction: discord.Interaction, item_name: str):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        currRoom = helpers.get_room_from_id(channel_id)

        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake.*")
            return

        if currRoom is None:
            await interaction.followup.send("*You are not currently in a room. Please contact an admin if you believe this is a mistake.*")
            return

        clothesWeight = player.get_clothes_weight()
        itemList = currRoom.get_items()

        for item in itemList:
            if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                if item.get_wearable_state():
                    if (clothesWeight + item.get_weight()) > data.get_max_wear_weight():
                        if len(player.get_clothes()) == 0:
                            await interaction.followup.send(f"***{player.get_name()}** tried to take and wear the item **{item.get_name()}**, but it was too heavy.*")
                            return    
                        await interaction.followup.send(f"***{player.get_name()}** tried to take and wear the item **{item.get_name()}**, but they were wearing too much already.*")
                        return
                    player.add_clothes(item)
                    currRoom.del_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** took and wore the item **{item.get_name()}**.*")
                else:
                    await interaction.followup.send(f"***{player.get_name()}** tried to take and wear the item **{item.get_name()}**, but it was not a piece of clothing.*")
                return
            
        await interaction.followup.send(f"Could not find the item **{item_name}**. Please use `/items` to see a list of items in the current room.*")
    #endregion
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
    #region /lookitem
    @app_commands.command(name = "lookitem", description = "Get the description of a specific item in the current room.")
    @app_commands.describe(item_name = "The name of the item you wish to look at.")
    @app_commands.autocomplete(item_name=autocompletes.room_items_autocomplete)
    async def lookitem(self, interaction: discord.Interaction, item_name: str):
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

        if len(itemList) == 0:
            await interaction.followup.send("*No items could be found in the room.*")
            return
        
        searchedItem = None
        for item in itemList:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(item_name):
                searchedItem = item
        
        if searchedItem is None:
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/items` to see a list of all the items in the current room.*")
            return
        
        if player is not None:
            if searchedItem.get_desc() == '':
                await interaction.followup.send(f"***{player.get_name()}** looked at the item **{searchedItem.get_name()}**:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{str(searchedItem.get_weight())}`\n__`Wearable`__: `{str(searchedItem.get_wearable_state())}`\n\nItem has no description.")
                return
            else:
                await interaction.followup.send(f"***{player.get_name()}** looked at the item **{searchedItem.get_name()}**:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{str(searchedItem.get_weight())}`\n__`Wearable`__: `{str(searchedItem.get_wearable_state())}`\n\n{searchedItem.get_desc()}")
            return
        
        if searchedItem.get_desc() == '':
            await interaction.followup.send(f"*Looked at the item **{searchedItem.get_name()}**:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{str(searchedItem.get_weight())}`\n__`Wearable`__: `{str(searchedItem.get_wearable_state())}`\n\nItem has no description.")
            return

        await interaction.followup.send(f"*Looked at the item **{searchedItem.get_name()}**:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{str(searchedItem.get_weight())}`\n__`Wearable`__: `{str(searchedItem.get_wearable_state())}`\n\n{searchedItem.get_desc()}")
    #endregion
    

async def setup(bot: commands.Bot):
    await bot.add_cog(RoomCMDs(bot))
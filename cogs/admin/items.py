import typing
import copy

from discord.ext import commands
from discord import app_commands
import discord

import utils.autocompletes as autocompletes
import utils.helpers as helpers
import utils.data as data

class AdminItemsCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #region /additem
    @app_commands.command(name = "additem", description = "Add an item into the experience.")
    @app_commands.choices(container = [
        app_commands.Choice(name = "Room", value = 0),
        app_commands.Choice(name = "Player's inventory", value = 1),
        app_commands.Choice(name = "Player's clothes", value = 2),
        app_commands.Choice(name = "Object", value = 3)
        ])
    @app_commands.describe(container_name = "The name of the container you wish to add the item to. If an object, be sure to specify a room name.")
    @app_commands.describe(item_name = "The name of the item you wish to add.")
    @app_commands.describe(weight = "The weight of the item you wish to add.")
    @app_commands.describe(wearable = "True or false; whether you wish the item to be wearable or not.")
    @app_commands.describe(desc = "The description of the item you wish to add.")
    @app_commands.describe(amount = "The amount of the item you wish to add.")
    @app_commands.describe(object_room_name = "Optional; if the container is an object, specify the room name.")
    @app_commands.autocomplete(container_name=autocompletes.admin_container_autocomplete)
    @app_commands.autocomplete(object_room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.default_permissions()
    async def additem(self, interaction: discord.Interaction, container: app_commands.Choice[int], container_name: str, item_name: str, weight: float, wearable: bool = False, desc: str = '', amount: int = 1, object_room_name: str = ''):
        await interaction.response.defer(thinking=True)

        ifNone = ''
        containerType = ''
        containerVar = None
        currentWeight = 0
        capacity = 0
        checkCapacity = False
        desc = helpers.format_desc(desc)

        if item_name.startswith("\\"):
            await interaction.followup.send(f"*You did not enter a valid item name. Please do not start a name with a backslash.*")
            return

        if amount < 1:
            await interaction.followup.send(
                f"***{amount}** is an invalid input; please use a positive number greater than one.*"
            )
            return

        if container.value == 0:
            ifNone = f"*Room **{container_name}** could not be found. Please use `/listrooms` to see all current rooms.*"
            containerType = "room"
            containerVar = helpers.get_room_from_name(container_name)

        elif container.value == 1:
            ifNone = f"*Player **{container_name}** could not be found. Please use `/listplayers` to see all current players.*"
            containerType = "inventory of"
            containerVar = helpers.get_player_from_name(container_name)
            currentWeight = containerVar.get_weight()
            checkCapacity = True
            capacity = data.get_max_carry_weight()

        elif container.value == 2:
            ifNone = f"*Player **{container_name}** could not be found. Please use `/listplayers` to see all current players.*"
            containerType = "clothes of"
            containerVar = helpers.get_player_from_name(container_name)
            currentWeight = containerVar.get_clothes_weight()
            checkCapacity = True
            capacity = data.get_max_wear_weight()

        elif container.value == 3:

            if not object_room_name:
                await interaction.followup.send(
                    "*To add an item to an object, you must specify the room name as well. Please use `/listrooms` to see all current rooms.*"
                )
                return

            room = helpers.get_room_from_name(object_room_name)

            if room is None:
                await interaction.followup.send(f"*Room **{object_room_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
                return

            for obj in room.get_objects():
                if helpers.simplify_string(obj.get_name()) == helpers.simplify_string(container_name):
                    containerVar = obj

            ifNone = f"*Object **{container_name}** could not be found. Please use `/listobjects` to see the objects in a room.*"

            containerType = "object"
            if containerVar.get_storage() != -1:
                checkCapacity = True

        if containerVar is None:
            await interaction.followup.send(ifNone)
            return

        if checkCapacity:
            if containerType == "object":
                if (amount + len(containerVar.get_items())) > containerVar.get_storage():
                    await interaction.followup.send(f"*Could not add **{item_name}** to the object **{containerVar.get_name()}**: Maximum storage reached.*")
                    return
            else:
                addedWeight = sum(weight for _ in range(amount))
                if (addedWeight + currentWeight) > capacity:
                    await interaction.followup.send(f"*Could not add **{item_name}** to the {containerType} **{containerVar.get_name()}**: Maximum weight reached.*")
                    return

        amountStr = f"**{amount}** of the" if amount > 1 else 'the'

        if container.value == 2:
            if not wearable:
                await interaction.followup.send(f"*Could not add **{item_name}** to **{containerVar.get_name()}**'s clothes: Item must be wearable.*")
                return
            for _ in range(amount):
                item: data.Item = data.Item(item_name, weight, wearable, desc)
                containerVar.add_clothes(item)

        else:
            for _ in range(amount):
                item: data.Item = data.Item(item_name, weight, wearable, desc)
                containerVar.add_item(item)

        data.save()
        await interaction.followup.send(f"*Added {amountStr} item **{item_name}** to the {containerType} **{containerVar.get_name()}**.*")
    #endregion
    #region /delitem
    @app_commands.command(name = "delitem", description = "Delete an item from the experience.")
    @app_commands.choices(container = [
        app_commands.Choice(name = "Room", value = 0),
        app_commands.Choice(name = "Player's inventory", value = 1),
        app_commands.Choice(name = "Player's clothes", value = 2),
        app_commands.Choice(name = "Object", value = 3)
        ])
    @app_commands.describe(container_name = "The name of the container you wish to delete the item from.")
    @app_commands.describe(item_name = "The name of the item you wish to delete.")
    @app_commands.describe(amount = "The amount of the item you wish to delete.")
    @app_commands.describe(object_room_name = "Optional; if the container is an object, specify the room name.")
    @app_commands.autocomplete(container_name=autocompletes.admin_container_autocomplete)
    @app_commands.autocomplete(object_room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.autocomplete(item_name=autocompletes.admin_item_autocomplete)
    @app_commands.default_permissions()
    async def delitem(self, interaction: discord.Interaction, container: app_commands.Choice[int], container_name: str, item_name: str, amount: int = 1, object_room_name: str = ''):
        await interaction.response.defer(thinking=True)

        ifNone = ''
        containerType = ''
        containerVar = None

        if amount < 1:
            await interaction.followup.send(
                f"***{amount}** is an invalid input; please use a positive number greater than one.*"
            )
            return

        if container.value == 0:
            ifNone = f"*Room **{container_name}** could not be found. Please use `/listrooms` to see all current rooms.*"
            containerType = "room"
            containerVar = helpers.get_room_from_name(container_name)

        elif container.value == 1:
            ifNone = f"*Player **{container_name}** could not be found. Please use `/listplayers` to see all current players.*"
            containerType = "player"
            containerVar = helpers.get_player_from_name(container_name)

        elif container.value == 2:
            ifNone = f"*Player **{container_name}** could not be found. Please use `/listplayers` to see all current players.*"
            containerType = "clothes of"
            containerVar = helpers.get_player_from_name(container_name)

        elif container.value == 3:

            if not object_room_name:
                await interaction.followup.send(
                    "*To add an item to an object, you must specify the room name as well. Please use `/listrooms` to see all current rooms.*"
                )
                return

            room = helpers.get_room_from_name(object_room_name)

            if room is None:
                await interaction.followup.send(f"*Room **{object_room_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
                return

            for obj in room.get_objects():
                if helpers.simplify_string(obj.get_name()) == helpers.simplify_string(container_name):
                    containerVar = obj

            ifNone = f"*Object **{container_name}** could not be found. Please use `/listobjects` to see the objects in a room.*"

            containerType = "object"

        if containerVar is None:
            await interaction.followup.send(ifNone)
            return

        if container.value == 2:
            itemList = containerVar.get_clothes()    
        else:
            itemList = containerVar.get_items()

        if len(itemList) == 0:
            await interaction.followup.send("*No items could be found in that container.*")
            return

        searchedItem = None
        for item in itemList:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(item_name):
                searchedItem = item

        if searchedItem is None:
            await interaction.followup.send(f"*Could not find the item **{item_name}**.*")
            return

        realAmount = 0
        for _ in range(amount):
            if container.value == 2:
                for clothing in containerVar.get_clothes():
                    if clothing.name == searchedItem.name:
                        realAmount += 1
                        containerVar.del_clothes(clothing)
                        break
            else:
                for item in containerVar.get_items():
                    if item.name == searchedItem.name:
                        realAmount += 1
                        containerVar.del_item(item)
                        break


        amountStr = f'**{realAmount}** of the' if amount > 1 else 'the'
        data.save()
        await interaction.followup.send(f"*Deleted {amountStr} item **{searchedItem.get_name()}** from the {containerType} **{containerVar.get_name()}**.*")
    #endregion
    #region /listitems
    @app_commands.command(name = "listitems", description = "List the items in a container.")
    @app_commands.choices(container = [
        app_commands.Choice(name = "Room", value = 0),
        app_commands.Choice(name = "Player's inventory", value = 1),
        app_commands.Choice(name = "Player's clothes", value = 2),
        app_commands.Choice(name = "Object", value = 3)
        ])
    @app_commands.describe(container_name = "The name of the container you wish to add the item to.")
    @app_commands.describe(object_room_name = "Optional; if the container is an object, specify the room name.")
    @app_commands.autocomplete(container_name=autocompletes.admin_container_autocomplete)
    @app_commands.autocomplete(object_room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.default_permissions()
    async def listitems(self, interaction: discord.Interaction, container: app_commands.Choice[int], container_name: str, object_room_name: str = ''):
        await interaction.response.defer(thinking=True)

        endMsg = ''
        weightMsg = ''
    
        containerVar = None
        if container.value == 0:
            containerVar = helpers.get_room_from_name(container_name)

            if containerVar is None:
                await interaction.followup.send(f"*Room **{container_name}** could not be found. Please use `/listrooms` to see a list of all current rooms.*")
                return

            endMsg = f"the room **{containerVar.get_name()}**"

        elif container.value == 1:
            containerVar = helpers.get_player_from_name(container_name)

            if containerVar is None:
                await interaction.followup.send(f"*Player **{container_name}** could not be found. Please use `/listplayers` to see a list of all current players.*")
                return

            endMsg = f"**{containerVar.get_name()}**'s inventory"
            weightMsg = f"__`Weight`__: `{containerVar.get_weight()}`/`{data.get_max_carry_weight()}`\n\n"


        elif container.value == 2:
            containerVar = helpers.get_player_from_name(container_name)

            if containerVar is None:
                await interaction.followup.send(f"*Player **{container_name}** could not be found. Please use `/listplayers` to see a list of all current players.*")
                return

            endMsg = f"**{containerVar.get_name()}**'s clothes"        
            weightMsg = f"__`Weight`__: `{containerVar.get_clothes_weight()}`/`{data.get_max_carry_weight()}`\n\n"


        elif container.value == 3:

            if not object_room_name:
                await interaction.followup.send(
                    "*To look inside of an object, you must specify the room name as well. Please use `/listrooms` to see all current rooms.*"
                )
                return

            room = helpers.get_room_from_name(object_room_name)

            if room is None:
                await interaction.followup.send(f"*Room **{object_room_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
                return

            for obj in room.get_objects():
                if helpers.simplify_string(obj.get_name()) == helpers.simplify_string(container_name):
                    containerVar = obj

            if containerVar is None:
                await interaction.followup.send(f"*Object **{container_name}** could not be found. Please use `/listobjects` to see the objects in a room.*")
                return

            endMsg = f"the object **{containerVar.get_name()}** in the room **{room.get_name()}**"

        if container.value == 2:
            itemList = containerVar.get_clothes()
        else:
            itemList = containerVar.get_items()

        if len(itemList) == 0:
            await interaction.followup.send(f"*Looked inside of {endMsg}:*\n\n`No items found.`")
            return

        if container.value == 1 or container.value == 2:
            itemNames = [f"`{item.get_name()}` (weight: `{item.get_weight()}`)" for item in itemList]
            allItems = '\n'.join(itemNames)
        else:
            itemNames = [f"`{item.get_name()}`" for item in itemList]
            allItems = ', '.join(itemNames)

        await interaction.followup.send(f"*Looked inside of {endMsg}:*\n\n{weightMsg}{allItems}")
    #endregion
    #region /seeitem
    @app_commands.command(name = "seeitem", description = "Get the description of a specific item.")
    @app_commands.choices(container = [
        app_commands.Choice(name = "Room", value = 0),
        app_commands.Choice(name = "Player's inventory", value = 1),
        app_commands.Choice(name = "Player's clothes", value = 2),
        app_commands.Choice(name = "Object", value = 3)
        ])
    @app_commands.describe(container_name = "The name of the container you wish to look inside of.")
    @app_commands.describe(item_name = "The name of the item you wish to look at.")
    @app_commands.describe(object_room_name = "Optional; if the container is an object, specify the room name.")
    @app_commands.autocomplete(container_name=autocompletes.admin_container_autocomplete)
    @app_commands.autocomplete(object_room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.autocomplete(item_name=autocompletes.admin_item_autocomplete)
    @app_commands.default_permissions()
    async def seeitem(self, interaction: discord.Interaction, container: app_commands.Choice[int], container_name: str, item_name: str, object_room_name: str = ''):
        await interaction.response.defer(thinking=True)

        endMsg = ''
        containerVar = None
        if container.value == 0:
            containerVar = helpers.get_room_from_name(container_name)

            if containerVar is None:
                await interaction.followup.send(f"*Room **{container_name}** could not be found. Please use `/listrooms` to see a list of all current rooms.*")
                return

            endMsg = f"the room **{containerVar.get_name()}**"

        elif container.value == 1:
            containerVar = helpers.get_player_from_name(container_name)

            if containerVar is None:
                await interaction.followup.send(f"*Player **{container_name}** could not be found. Please use `/listplayers` to see a list of all current players.*")
                return

            endMsg = f"**{containerVar.get_name()}**'s inventory"


        elif container.value == 2:
            containerVar = helpers.get_player_from_name(container_name)

            if containerVar is None:
                await interaction.followup.send(f"*Player **{container_name}** could not be found. Please use `/listplayers` to see a list of all current players.*")
                return

            endMsg = f"**{containerVar.get_name()}**'s clothes"        


        elif container.value == 3:

            if not object_room_name:
                await interaction.followup.send(
                    "*To look inside of an object, you must specify the room name as well. Please use `/listrooms` to see all current rooms.*"
                )
                return

            room = helpers.get_room_from_name(object_room_name)

            if room is None:
                await interaction.followup.send(f"*Room **{object_room_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
                return

            for obj in room.get_objects():
                if helpers.simplify_string(obj.get_name()) == helpers.simplify_string(container_name):
                    containerVar = obj

            if containerVar is None:
                await interaction.followup.send(f"*Object **{container_name}** could not be found. Please use `/listobjects` to see the objects in a room.*")
                return

            endMsg = f"the object **{containerVar.get_name()}** in the room **{room.get_name()}**"

        if container.value == 2:
            itemList = containerVar.get_clothes()
        else:
            itemList = containerVar.get_items()

        searchedItem = None
        for item in itemList:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(item_name):
                searchedItem = item

        if searchedItem is None:
            await interaction.followup.send(f"*Could not find the item **{item_name}** in {endMsg}.*")
            return

        if searchedItem.get_desc() == '':
            await interaction.followup.send(f"*Looked at the item **{searchedItem.get_name()}**:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{str(searchedItem.get_weight())}`\n__`Wearable`__: `{str(searchedItem.get_wearable_state())}`\n\nItem has no description.")
            return

        await interaction.followup.send(f"*Looked at the item **{searchedItem.get_name()}**:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{str(searchedItem.get_weight())}`\n__`Wearable`__: `{str(searchedItem.get_wearable_state())}`\n\n{searchedItem.get_desc()}")
    #endregion
    #region /edititem
    @app_commands.command(name = "edititem", description = "Edit the value of an item.")
    @app_commands.choices(container = [
        app_commands.Choice(name = "Room", value = 0),
        app_commands.Choice(name = "Player's inventory", value = 1),
        app_commands.Choice(name = "Player's clothes", value = 2),
        app_commands.Choice(name = "Object", value = 3)
        ])
    @app_commands.describe(container_name = "The name of the container the item is in.")
    @app_commands.describe(item_name = "The name of the item you wish to edit.")
    @app_commands.describe(object_room_name = "Optional; if the container is an object, specify the room name.")
    @app_commands.describe(new_name = "The new name of the item.")
    @app_commands.describe(new_desc = "The new description of the item.")
    @app_commands.describe(is_wearable = "Whether you would like the item to be wearable.")
    @app_commands.describe(new_weight = "The new weight of the item.")
    @app_commands.autocomplete(container_name=autocompletes.admin_container_autocomplete)
    @app_commands.autocomplete(object_room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.autocomplete(item_name=autocompletes.admin_item_autocomplete)
    @app_commands.default_permissions()
    async def edititem(self, interaction: discord.Interaction, container: app_commands.Choice[int], container_name: str, item_name: str, object_room_name: str = '', new_name:str = '', new_desc: str = '', is_wearable: bool = None, new_weight: float = -1.0):
        await interaction.response.defer(thinking=True)

        endMsg = ''
        containerVar = None
        if container.value == 0:
            containerVar = helpers.get_room_from_name(container_name)

            if containerVar is None:
                await interaction.followup.send(f"*Room **{container_name}** could not be found. Please use `/listrooms` to see a list of all current rooms.*")
                return

            endMsg = f"the room **{containerVar.get_name()}**"

        elif container.value == 1:
            containerVar = helpers.get_player_from_name(container_name)

            if containerVar is None:
                await interaction.followup.send(f"*Player **{container_name}** could not be found. Please use `/listplayers` to see a list of all current players.*")
                return

            endMsg = f"**{containerVar.get_name()}**'s inventory"


        elif container.value == 2:
            containerVar = helpers.get_player_from_name(container_name)

            if containerVar is None:
                await interaction.followup.send(f"*Player **{container_name}** could not be found. Please use `/listplayers` to see a list of all current players.*")
                return

            endMsg = f"**{containerVar.get_name()}**'s clothes"        


        elif container.value == 3:

            if not object_room_name:
                await interaction.followup.send("*To edit an item inside of an object, you must specify the room name as well. Please use `/listrooms` to see all current rooms.*")
                return

            room = helpers.get_room_from_name(object_room_name)

            if room is None:
                await interaction.followup.send(f"*Room **{object_room_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
                return

            for obj in room.get_objects():
                if helpers.simplify_string(obj.get_name()) == helpers.simplify_string(container_name):
                    containerVar = obj

            if containerVar is None:
                await interaction.followup.send(f"*Object **{container_name}** could not be found. Please use `/listobjects` to see the objects in a room.*")
                return

            endMsg = f"the object **{containerVar.get_name()}** in the room **{room.get_name()}**"

        if container.value == 2:
            itemList = containerVar.get_clothes()
        else:
            itemList = containerVar.get_items()

        matchingItems = [
            i for i, item in enumerate(itemList)
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(item_name)
        ]

        if not matchingItems:
            await interaction.followup.send(f"*Could not find the item **{item_name}** in {endMsg}.*")
            return

        found_items = helpers.find_items(item_name)
        searchedItem = None

        if len(found_items) == 1:
            searchedItem = itemList[matchingItems[0]]
        else:
            indexToEdit = matchingItems[-1]
            itemList[indexToEdit] = copy.deepcopy(itemList[indexToEdit])
            searchedItem = itemList[indexToEdit]

        item_strs: typing.List[str] = []
        if new_name != '':
            searchedItem.edit_name(new_name)
            nameStr = 'name'
            item_strs.append(nameStr)
        if new_desc != '':
            new_desc = helpers.format_desc(new_desc)
            searchedItem.edit_desc(new_desc)
            descStr = 'description'
            item_strs.append(descStr)
        if is_wearable != None:
            searchedItem.switch_wearable_state(is_wearable)
            wearStr = 'wearable state'
            item_strs.append(wearStr)
        if new_weight != -1:
            searchedItem.edit_weight(new_weight)
            weightStr = 'weight'
            item_strs.append(weightStr)

        if (
            not new_name
            and not new_desc
            and is_wearable is None
            and new_weight == -1
        ):
            await interaction.followup.send(f"*Please select an option and enter a new value to edit the item **{searchedItem.get_name}**.*")
            return

        edited = ''
        if not item_strs:
            edited = ''
        elif len(item_strs) == 1:
            edited = item_strs[0]
        elif len(item_strs) == 2:
            edited = f"{item_strs[0]} and {item_strs[1]}"
        else:
            edited = ", ".join(item_strs[:-1]) + f", and {item_strs[-1]}"

        data.save()
        await interaction.followup.send(f"*Changed the item **{searchedItem.get_name()}**'s {edited}.*")
    #endregion
    #region /finditem
    @app_commands.command(name = "finditem", description = "List all items that have a given name, as well as their location.")
    @app_commands.describe(item_name = "The name of the item you wish to find.")
    @app_commands.default_permissions()
    async def finditem(self, interaction: discord.Interaction, item_name: str):
        await interaction.response.defer(thinking=True)

        found_items = helpers.find_items(item_name)

        if not found_items:
            await interaction.followup.send(f"*Could not find any items with the name **{item_name}**.*")
            return
        
        
        results = f"*Items with the name **{found_items[0][0].get_name()}** were found in the following location(s):*\n\n"
        location_count = {}

        for item, location in found_items:
            location_count[location] = location_count.get(location, 0) + 1

        for location, count in location_count.items():
            if count > 1:
                results += f"{location} **(x{count})**\n"
            else:
                results += f"{location}\n"

        await interaction.followup.send(results)
    #endregion
        

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminItemsCMDs(bot))
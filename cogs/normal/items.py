import typing

from discord.ext import commands
from discord import app_commands
import discord

import utils.data as data
import utils.helpers as helpers
import utils.autocompletes as autocompletes

class ItemCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    #region /take
    @app_commands.command(name = "take", description = "Take an item from the room.")
    @app_commands.describe(item_name = "The item you wish to take.")
    @app_commands.describe(amount = "[OPTIONAL] The amount you wish to take.")
    @app_commands.autocomplete(item_name=autocompletes.room_items_autocomplete)
    async def takeitem(self, interaction: discord.Interaction, item_name: str, amount: int = 0):
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        current_room = helpers.get_room_from_id(channel_id)

        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.check_room_exists(interaction, current_room):
            return
        if await helpers.handle_view_more(interaction, "item", item_name):
            return

        await interaction.response.defer(thinking=True)

        inv_weight = player.get_weight()
        item_list = current_room.get_items()

        if amount in {0, 1}:
            for item in item_list:
                if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                    if (inv_weight + item.get_weight()) > data.get_max_carry_weight():
                        await interaction.followup.send(f"***{player.get_name()}** tried to take the item **{item.get_name()}**, but they could not fit it into their inventory.*")
                        return
                    player.add_item(item)
                    current_room.del_item(item)
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

        items_found: typing.List[data.Item] = []
        searched_item = None
        for item in item_list:
            if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                searched_item = item
                items_found.append(searched_item)

        if not items_found or not searched_item:
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/items` to see a list of items in the current room.*")
            return
        
        if len(items_found) < amount:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}**. Please use `/items` to see a list of items in the current room.*"
            )
            return
        
        try:
            new_carry_weight = sum(items_found[i].get_weight() for i in range(amount))
            if (inv_weight + new_carry_weight) > data.get_max_carry_weight():
                await interaction.followup.send(
                    f"***{player.get_name()}** tried to take **{amount}** of the item **{searched_item.get_name()}**, but they could not fit that much into their inventory.*"
                )
                return
            for i in range(amount):
                player.add_item(items_found[i])
                current_room.del_item(items_found[i])
            data.save()
            await interaction.followup.send(
                f"***{player.get_name()}** took **{amount}** of the item **{searched_item.get_name()}***."
            )
            return
        except Exception:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}**. Please use `/items` to see a list of items in the current room.*"
            )
            return
    #endregion
    #region /takefrom
    @app_commands.command(name = "takefrom", description = "Take an item from an object in the room.")
    @app_commands.describe(object_name = "The object you wish to take an item from.")
    @app_commands.describe(item_name = "The item you wish to take.")
    @app_commands.describe(amount = "The amount of that item you wish to take.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete, item_name=autocompletes.object_contents_autocomplete)
    async def takefrom(self, interaction: discord.Interaction, object_name: str, item_name: str, amount: int = 0):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        current_room = helpers.get_room_from_id(channel_id)

        if await helpers.check_valid_player(interaction, player):
            return
        searched_obj = await helpers.check_obj_container(interaction, current_room, object_name, player)
        if searched_obj is None:
            return

        inv_weight = player.get_weight()
        item_list = searched_obj.get_items()

        if amount in {0, 1}:
            for item in item_list:
                if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                    if (inv_weight + item.get_weight()) > data.get_max_carry_weight():
                        await interaction.followup.send(f"***{player.get_name()}** tried to take the item **{item.get_name()}** from the object **{searched_obj.get_name()}**, but they could not fit it into their inventory.*")
                        return
                    player.add_item(item)
                    searched_obj.del_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** took the item **{item.get_name()}** from **{searched_obj.get_name()}***.")
                    return
            await interaction.followup.send(f"*Could not find the item **{item_name}** inside of the object **{searched_obj.get_name()}**. Please use `/contents` to see a list of items in an object.*")
            return

        if amount < 0:
            await interaction.followup.send(
                f"***{amount}** is an invalid input; please use a positive number.*"
            )
            return

        items_found: typing.List[data.Item] = []
        searched_item = None
        for item in item_list:
            if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                searched_item = item
                items_found.append(searched_item)

        if not items_found or not searched_item:
            await interaction.followup.send(f"*Could not find the item **{item_name}** inside of the object **{searched_obj.get_name()}**. Please use `/contents` to see a list of all the items in an object.*")
            return

        if len(items_found) < amount:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}** inside of the object **{searched_obj.get_name()}**. Please use `/contents` to see a list of all the items in an object.*"
            )
            return
        try:
            new_carry_weight = sum(items_found[i].get_weight() for i in range(amount))
            if (inv_weight + new_carry_weight) > data.get_max_carry_weight():
                await interaction.followup.send(
                    f"***{player.get_name()}** tried to take **{amount}** of the item **{searched_item.get_name()}** from the object **{searched_obj.get_name()}**, but they could not fit that much into their inventory.*"
                )
                return
            for i in range(amount):
                player.add_item(items_found[i])
                searched_obj.del_item(items_found[i])
            data.save()
            await interaction.followup.send(
                f"***{player.get_name()}** took **{amount}** of the item **{searched_item.get_name()}** from **{searched_obj.get_name()}***."
            )
            return
        except Exception:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}** inside of the object **{searched_obj.get_name()}**. Please use `/contents` to see a list of all the items in an object.*"
            )
            return
    #endregion
    #region /drop
    @app_commands.command(name = "drop", description = "Drop an item from your inventory into the room.")
    @app_commands.describe(item_name = "The item you wish to drop.")
    @app_commands.describe(amount = "The amount of that item you wish to drop.")
    @app_commands.autocomplete(item_name=autocompletes.user_items_autocomplete)
    async def drop(self, interaction: discord.Interaction, item_name: str, amount: int = 0):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        current_room = helpers.get_room_from_id(channel_id)

        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.check_room_exists(interaction, current_room):
            return

        item_list = player.get_items()

        if amount in {0, 1}:
            for item in item_list:
                if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                    player.del_item(item)
                    current_room.add_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** dropped the item **{item.get_name()}**.*")
                    return
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/inventory` to see a list of items in your inventory.*")
            return

        if amount < 0:
            await interaction.followup.send(
                f"***{amount}** is an invalid input; please use a positive number.*"
            )
            return

        items_found: typing.List[data.Item] = []
        searched_item = None
        for item in item_list:
            if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                searched_item = item
                items_found.append(searched_item)

        if not items_found or not searched_item:
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/inventory` to see a list of items in your inventory.*")
            return

        if len(items_found) < amount:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}**. Please use `/inventory` to see a list of items in your inventory.*"
            )
            return

        try:
            for i in range(amount):
                player.del_item(items_found[i])
                current_room.add_item(items_found[i])
            data.save()
            await interaction.followup.send(
                f"***{player.get_name()}** dropped **{amount}** of the item **{searched_item.get_name()}**.*"
            )
            return
        except Exception:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}**. Please use `/inventory` to see a list of items in your inventory.*"
            )
            return
    #endregion
    #region /dropinto
    @app_commands.command(name = "dropinto", description = "Drop an item from your inventory into an object.")
    @app_commands.describe(object_name = "The object you wish to drop the item into.")
    @app_commands.describe(item_name = "The item you wish to drop.")
    @app_commands.describe(amount = "The amount of that item you wish to drop.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete, item_name=autocompletes.user_items_autocomplete)
    async def dropinto(self, interaction: discord.Interaction, object_name: str, item_name: str, amount: int = 0):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        current_room = helpers.get_room_from_id(channel_id)

        if await helpers.check_valid_player(interaction, player):
            return
        searched_obj = await helpers.check_obj_container(interaction, current_room, object_name, player)
        if searched_obj is None:
            return

        max_storage_amt = searched_obj.get_storage()
        obj_contents = searched_obj.get_items()
        item_list = player.get_items()

        if amount in {0, 1}:
            for item in item_list:
                if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                    if (len(obj_contents) + 1) > max_storage_amt and searched_obj.get_storage() != -1:
                        await interaction.followup.send(f"***{player.get_name()}** tried to drop the item **{item.get_name()}** into the object **{searched_obj.get_name()}**, but there wasn't enough space.*")
                        return
                    player.del_item(item)
                    searched_obj.add_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** dropped the item **{item.get_name()}** into **{searched_obj.get_name()}***.")
                    return
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/inventory` to see a list of items in your inventory.*")
            return

        if amount < 0:
            await interaction.followup.send(
                f"***{amount}** is an invalid input; please use a positive number.*"
            )
            return

        items_found: typing.List[data.Item] = []
        searched_item = None
        for item in item_list:
            if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                searched_item = item
                items_found.append(searched_item)

        if not items_found or not searched_item:
            await interaction.followup.send(f"*Could not find the item **{item_name}** inside of the object **{searched_obj.get_name()}**. Please use `/inventory` to see a list of items in your inventory.*")
            return

        if len(items_found) < amount:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}** inside of the object **{searched_obj.get_name()}**. Please use `/inventory` to see a list of items in your inventory.*"
            )
            return

        try:
            new_storage_amt = len(range(amount))
            if (
                len(obj_contents) + new_storage_amt
            ) > max_storage_amt and searched_obj.get_storage() != -1:
                await interaction.followup.send(
                    f"***{player.get_name()}** tried to drop **{amount}** of the item **{searched_item.get_name()}** into the object **{searched_obj.get_name()}**, but there wasn't enough space.*"
                )
                return
            for i in range(amount):
                player.del_item(items_found[i])
                searched_obj.add_item(items_found[i])
            data.save()
            await interaction.followup.send(
                f"***{player.get_name()}** dropped **{amount}** of the item **{searched_item.get_name()}** into **{searched_obj.get_name()}***."
            )
            return
        except Exception:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}** inside of the object **{searched_obj.get_name()}**. Please use `/inventory` to see a list of items in your inventory.*"
            )
            return
    #endregion
    #region /wear
    @app_commands.command(name = "wear", description = "Wear a clothing item from your inventory or current room.")
    @app_commands.choices(container = [
        app_commands.Choice(name = "Inventory", value = 0),
        app_commands.Choice(name = "Room", value = 1)
    ])
    @app_commands.describe(container = "Where is the clothing item located?")
    @app_commands.describe(item_name = "The clothing item you wish to wear.")
    @app_commands.autocomplete(item_name=autocompletes.user_or_room_items_autocomplete)
    async def wear(self, interaction: discord.Interaction, container: app_commands.Choice[int], item_name: str):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        current_room = helpers.get_room_from_id(channel_id)

        if await helpers.check_valid_player(interaction, player):
            return

        clothes_weight = player.get_clothes_weight()
        
        if container.value == 0:
            item_list = player.get_items()

            for item in item_list:
                if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                    if item.get_wearable_state():
                        if (clothes_weight + item.get_weight()) > data.get_max_wear_weight():
                            if len(player.get_clothes()) == 0:
                                await interaction.followup.send(f"***{player.get_name()}** tried to wear the item **{item.get_name()}**, but it was too heavy.*")
                                return    
                            await interaction.followup.send(f"***{player.get_name()}** tried to wear the item **{item.get_name()}**, but they were wearing too much.*")
                            return
                        player.add_clothes(item)
                        player.del_item(item)
                        data.save()
                        await interaction.followup.send(f"***{player.get_name()}** wore the item **{item.get_name()}**.*")
                        return
                    else:
                        await interaction.followup.send(f"***{player.get_name()}** tried to wear the item **{item.get_name()}**, but it was not a piece of clothing.*")
                        return

            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/inventory` to see a list of items in your inventory.*")
            return
        
        if container.value == 1:
            if await helpers.check_room_exists(interaction, current_room):
                return

            item_list = current_room.get_items()

            for item in item_list:
                if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                    if item.get_wearable_state():
                        if (clothes_weight + item.get_weight()) > data.get_max_wear_weight():
                            if len(player.get_clothes()) == 0:
                                await interaction.followup.send(f"***{player.get_name()}** tried to take and wear the item **{item.get_name()}**, but it was too heavy.*")
                                return    
                            await interaction.followup.send(f"***{player.get_name()}** tried to take and wear the item **{item.get_name()}**, but they were wearing too much.*")
                            return
                        player.add_clothes(item)
                        current_room.del_item(item)
                        data.save()
                        await interaction.followup.send(f"***{player.get_name()}** took and wore the item **{item.get_name()}**.*")
                    else:
                        await interaction.followup.send(f"***{player.get_name()}** tried to take and wear the item **{item.get_name()}**, but it was not a piece of clothing.*")
                    return

            await interaction.followup.send(f"Could not find the item **{item_name}**. Please use `/items` to see a list of items in the current room.*")
            return
        
        await interaction.followup.send(f"Could not find the item **{item_name}**.")
    #endregion
    #region /wearfrom
    @app_commands.command(name = "wearfrom", description = "Wear a clothing item that's located in an object in the room.")
    @app_commands.describe(object_name = "The object that has the clothing item inside of it.")
    @app_commands.describe(item_name = "The clothing item you wish to wear.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete)
    @app_commands.autocomplete(item_name=autocompletes.object_contents_autocomplete)
    async def wearfrom(self, interaction: discord.Interaction, object_name: str, item_name: str):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        current_room = helpers.get_room_from_id(channel_id)

        if await helpers.check_valid_player(interaction, player):
            return
        searched_obj = await helpers.check_obj_container(interaction, current_room, object_name, player)
        if searched_obj is None:
            return
        
        clothes_weight = player.get_clothes_weight()
        item_list = searched_obj.get_items()

        for item in item_list:
            if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                if item.get_wearable_state():
                    if (clothes_weight + item.get_weight()) > data.get_max_wear_weight():
                        if len(player.get_clothes()) == 0:
                            await interaction.followup.send(f"***{player.get_name()}** tried to wear the item **{item.get_name()}** from **{searched_obj.get_name()}**, but it was too heavy.*")
                            return    
                        await interaction.followup.send(f"***{player.get_name()}** tried to wear the item **{item.get_name()}** from **{searched_obj.get_name()}**, but they were wearing too much.*")
                        return
                    player.add_clothes(item)
                    searched_obj.del_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** wore the item **{item.get_name()}** from **{searched_obj.get_name()}**.*")
                    return
                else:
                    await interaction.followup.send(f"***{player.get_name()}** tried to wear the item **{item.get_name()}** from **{searched_obj.get_name()}**, but it was not a piece of clothing.*")
                    return

        await interaction.followup.send(f"*Could not find the item **{item_name}** inside of the object **{searched_obj.get_name()}**. Please use `/contents` to see a list of all the items in an object.*")
    #endregion
    #region /undress
    @app_commands.command(name = "undress", description = "Take off a clothing item and place it into your inventory or the current room.")
    @app_commands.choices(container = [
        app_commands.Choice(name = "Inventory", value = 0),
        app_commands.Choice(name = "Room", value = 1)
    ])
    @app_commands.describe(container = "Where would you like to drop the clothing item?")
    @app_commands.describe(item_name = "The clothing item you wish to take off.")
    @app_commands.autocomplete(item_name=autocompletes.clothing_autocomplete)
    async def undress(self, interaction: discord.Interaction, container: app_commands.Choice[int], item_name: str):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        current_room = helpers.get_room_from_id(channel_id)

        if await helpers.check_valid_player(interaction, player):
            return
        
        item_list = player.get_clothes()
        
        for item in item_list:
            if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                if container.value == 0:
                    if (player.get_weight() + item.get_weight()) > data.get_max_carry_weight():
                        await interaction.followup.send(f"***{player.get_name()}** tried to take off **{item.get_name()}**, but it couldn't fit into their inventory.*")
                        return
                    player.del_clothes(item)
                    player.add_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** took off the item **{item.get_name()}**.*")
                    return

                if container.value == 1:
                    if await helpers.check_room_exists(interaction, current_room):
                        return
                        
                    player.del_clothes(item)
                    current_room.add_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** took off and dropped the item **{item.get_name()}**.*")
                    return
            
        await interaction.followup.send(f"*Could not find **{item_name}**. Please use `/clothes` to see the clothes you are wearing.*")
    #endregion
    #region /undressinto
    @app_commands.command(name = "undressinto", description = "Take off a clothing item and place it into an object.")
    @app_commands.describe(object_name = "The object you wish to drop the clothing item into.")
    @app_commands.describe(item_name = "The clothing item you wish to drop.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete)
    @app_commands.autocomplete(item_name=autocompletes.clothing_autocomplete)
    async def undressdrop(self,interaction: discord.Interaction, object_name: str, item_name: str):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        current_room = helpers.get_room_from_id(channel_id)

        if await helpers.check_valid_player(interaction, player):
            return
        searched_obj = await helpers.check_obj_container(interaction, current_room, object_name, player)
        if searched_obj is None:
            return
        
        max_storage_amt = searched_obj.get_storage()
        obj_contents = searched_obj.get_items()
        item_list = player.get_clothes()

        for item in item_list:
            if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                if (len(obj_contents) + 1) > max_storage_amt and searched_obj.get_storage() != -1:
                    await interaction.followup.send(f"***{player.get_name()}** tried to drop the item **{item.get_name()}** into the object **{searched_obj.get_name()}**, but there wasn't enough space.*")
                    return
                player.del_clothes(item)
                searched_obj.add_item(item)
                data.save()
                await interaction.followup.send(f"***{player.get_name()}** dropped the item **{item.get_name()}** into **{searched_obj.get_name()}***.")
                return
        
        await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/clothes` to see the clothes you are wearing.*")
    #endregion

async def setup(bot: commands.Bot):
    await bot.add_cog(ItemCMDs(bot))
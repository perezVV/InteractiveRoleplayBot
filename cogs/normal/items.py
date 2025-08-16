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
    async def take(self, interaction: discord.Interaction, item_name: str, amount: int = 0):
        # Get the player and room class objects for this interaction
        player = helpers.get_player_from_id(interaction.user.id)
        current_room = helpers.get_room_from_id(interaction.channel_id)

        # Validate the interaction and handle smart autocomplete cases
        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.check_room_exists(interaction, current_room):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", item_name):
            return

        # Defer the response while processing the code
        await interaction.response.defer(thinking=True)

        # Get the list of items 
        item_list = current_room.get_items()

        # Whittle the list down into matching items; return if there are none
        found_items = await helpers.find_items_in_list(interaction, item_list, item_name, amount, "take")
        if found_items is None:
            return
        
        # Check if the player has enough space to carry the items they intend to pick up
        if not await helpers.can_carry(interaction, found_items, player, "take", amount):
            return

        # Transfer the item from the room into their inventory, send confirmation message
        return await interaction.followup.send(helpers.transfer_item(current_room, player, player, found_items, "take", amount))
    #endregion
    #region /takefrom
    @app_commands.command(name = "takefrom", description = "Take an item from an object in the room.")
    @app_commands.describe(object_name = "The object you wish to take an item from.")
    @app_commands.describe(item_name = "The item you wish to take.")
    @app_commands.describe(amount = "The amount of that item you wish to take.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete, item_name=autocompletes.object_contents_autocomplete)
    async def takefrom(self, interaction: discord.Interaction, object_name: str, item_name: str, amount: int = 0):
        # Get the player and room class objects for this interaciton
        player = helpers.get_player_from_id(interaction.user.id)
        current_room = helpers.get_room_from_id(interaction.channel_id)

        # Validate the interaction and handle smart autocomplete cases
        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", item_name):
            return
        searched_obj = await helpers.check_obj_container(interaction, current_room, object_name, player)
        if searched_obj is None:
            return

        # Defer the response while processing the code
        await interaction.response.defer(thinking=True)

        # Get the list of items 
        item_list = searched_obj.get_items()

        # Whittle the list down into matching items; return if there are none
        found_items = await helpers.find_items_in_list(interaction, item_list, item_name, amount, "takefrom", searched_obj)
        if found_items is None:
            return
        
        # Check if player has enough space to carry the items they intend to pick up
        if not await helpers.can_carry(interaction, found_items, player, "takefrom", amount, searched_obj):
            return
        
        # Transfer the item from the object into their inventory, send confirmation message
        return await interaction.followup.send(helpers.transfer_item(searched_obj, player, player, found_items, "takefrom", amount, searched_obj))
    #endregion
    #region /drop
    @app_commands.command(name = "drop", description = "Drop an item from your inventory into the room.")
    @app_commands.describe(item_name = "The item you wish to drop.")
    @app_commands.describe(amount = "The amount of that item you wish to drop.")
    @app_commands.autocomplete(item_name=autocompletes.user_items_autocomplete)
    async def drop(self, interaction: discord.Interaction, item_name: str, amount: int = 0):
        # Get the player and room class objects for this interaction
        player = helpers.get_player_from_id(interaction.user.id)
        current_room = helpers.get_room_from_id(interaction.channel_id)

        # Validate the interaction and handle smart autocomplete cases
        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.check_room_exists(interaction, current_room):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", item_name):
            return

        # Defer the response while processing the code
        await interaction.response.defer(thinking=True)

        # Get the list of items 
        item_list = player.get_items()

        # Whittle the list down into matching items; return if there are none
        found_items = await helpers.find_items_in_list(interaction, item_list, item_name, amount, "drop")
        if found_items is None:
            return

        # Transfer the item from their inventory into the room
        return await interaction.followup.send(helpers.transfer_item(player, current_room, player, found_items, "drop", amount))
    #endregion
    #region /dropinto
    @app_commands.command(name = "dropinto", description = "Drop an item from your inventory into an object.")
    @app_commands.describe(object_name = "The object you wish to drop the item into.")
    @app_commands.describe(item_name = "The item you wish to drop.")
    @app_commands.describe(amount = "The amount of that item you wish to drop.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete, item_name=autocompletes.user_items_autocomplete)
    async def dropinto(self, interaction: discord.Interaction, object_name: str, item_name: str, amount: int = 0):
        # Get the player and room class objects for this interaciton
        player = helpers.get_player_from_id(interaction.user.id)
        current_room = helpers.get_room_from_id(interaction.channel_id)

        # Validate the interaction and handle smart autocomplete cases
        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", item_name):
            return
        searched_obj = await helpers.check_obj_container(interaction, current_room, object_name, player)
        if searched_obj is None:
            return

        # Defer the response while processing the code
        await interaction.response.defer(thinking=True)

        # Get the list of items 
        item_list = player.get_items()

        # Whittle the list down into matching items; return if there are none
        found_items = await helpers.find_items_in_list(interaction, item_list, item_name, amount, "dropinto")
        if found_items is None:
            return

        # Check if the object has enough space to fit the items
        if not await helpers.can_store(interaction, player, searched_obj, found_items, "dropinto", amount):
            return

        # Transfer the item from the player's inventory into the object, send confirmation message
        return await interaction.followup.send(helpers.transfer_item(player, searched_obj, player, found_items, "dropinto", amount, searched_obj))
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
        # Get the player and room class objects for this interaciton
        player = helpers.get_player_from_id(interaction.user.id)
        current_room = helpers.get_room_from_id(interaction.channel_id)

        # Validate the interaction and handle smart autocomplete cases
        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", item_name):
            return

        # Defer the response while processing the code
        await interaction.response.defer(thinking=True)
        
        # Get the list of items 
        item_list = []
        source = None
        message_type = ""
        if container.value == 0:
            item_list = player.get_items()
            source = player
            message_type = "wear"
        if container.value == 1:
            if await helpers.check_room_exists(interaction, current_room):
                return
            item_list = current_room.get_items()
            source = current_room
            message_type = "takewear"

        # Whittle the list down into matching items; return if there are none
        found_items = await helpers.find_items_in_list(interaction, item_list, item_name, 1, message_type, source, True)
        if found_items is None:
            return
        
        # Check if player has enough space to carry the items they intend to pick up
        if not await helpers.can_carry(interaction, found_items, player, message_type, 1, None, True):
            return
        
        # Transfer the item from the source into the player's clothing, send confirmation message
        return await interaction.followup.send(helpers.transfer_item(source, player, player, found_items, message_type, amount=1, is_clothes_dest=True))
    #endregion
    #region /wearfrom
    @app_commands.command(name = "wearfrom", description = "Wear a clothing item that's located in an object in the room.")
    @app_commands.describe(object_name = "The object that has the clothing item inside of it.")
    @app_commands.describe(item_name = "The clothing item you wish to wear.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete)
    @app_commands.autocomplete(item_name=autocompletes.object_contents_autocomplete)
    async def wearfrom(self, interaction: discord.Interaction, object_name: str, item_name: str):
        # Get the player and room class objects for this interaciton
        player = helpers.get_player_from_id(interaction.user.id)
        current_room = helpers.get_room_from_id(interaction.channel_id)

        # Validate the interaction and handle smart autocomplete cases
        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", item_name):
            return
        searched_obj = await helpers.check_obj_container(interaction, current_room, object_name, player)
        if searched_obj is None:
            return
        
        # Defer the response while processing the code
        await interaction.response.defer(thinking=True)

        # Get the list of items 
        item_list = searched_obj.get_items()

        # Whittle the list down into matching items; return if there are none
        found_items = await helpers.find_items_in_list(interaction, item_list, item_name, 1, "wearfrom", searched_obj, True)
        if found_items is None:
            return
        
        # Check if player has enough space to carry the items they intend to pick up
        if not await helpers.can_carry(interaction, found_items, player, "wearfrom", 1, searched_obj, True):
            return
        
        # Transfer the item from the object into their inventory, send confirmation message
        return await interaction.followup.send(helpers.transfer_item(searched_obj, player, player, found_items, "wearfrom", amount=1, obj=searched_obj, is_clothes_dest=True))
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
        # Get the player and room class objects for this interaction
        player = helpers.get_player_from_id(interaction.user.id)
        current_room = helpers.get_room_from_id(interaction.channel_id)

        # Validate the interaction and handle smart autocomplete cases
        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.check_room_exists(interaction, current_room):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", item_name):
            return

        # Defer the response while processing the code
        await interaction.response.defer(thinking=True)

        # Get variables necessary for future logic
        item_list = player.get_clothes()
        message_type = "undress"
        destination = player

        # Whittle the list down into matching items; return if there are none
        found_items = await helpers.find_items_in_list(interaction, item_list, item_name, 1, message_type)
        if found_items is None:
            return

        # Check if player is undressing into their inventory or the room
        if container.value == 0:
            if not await helpers.can_carry(interaction, found_items, player, message_type, 1):
                return
        if container.value == 1:
            message_type = "undressroom"
            destination = current_room

        # Transfer the item from their inventory into the room
        return await interaction.followup.send(helpers.transfer_item(player, destination, player, found_items, message_type, amount=1, is_clothes_source=True))
    #endregion
    #region /undressinto
    @app_commands.command(name = "undressinto", description = "Take off a clothing item and place it into an object.")
    @app_commands.describe(object_name = "The object you wish to drop the clothing item into.")
    @app_commands.describe(item_name = "The clothing item you wish to drop.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete)
    @app_commands.autocomplete(item_name=autocompletes.clothing_autocomplete)
    async def undressinto(self,interaction: discord.Interaction, object_name: str, item_name: str):
        # Get the player and room class objects for this interaciton
        player = helpers.get_player_from_id(interaction.user.id)
        current_room = helpers.get_room_from_id(interaction.channel_id)

        # Validate the interaction and handle smart autocomplete cases
        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", item_name):
            return
        searched_obj = await helpers.check_obj_container(interaction, current_room, object_name, player)
        if searched_obj is None:
            return

        # Defer the response while processing the code
        await interaction.response.defer(thinking=True)

        # Get the list of items 
        item_list = player.get_clothes()

        # Whittle the list down into matching items; return if there are none
        found_items = await helpers.find_items_in_list(interaction, item_list, item_name, 1, "undressinto", None, True)
        if found_items is None:
            return

        # Check if the object has enough space to fit the items
        if not await helpers.can_store(interaction, player, searched_obj, found_items, "undressinto", 1):
            return

        # Transfer the item from the player's inventory into the object, send confirmation message
        return await interaction.followup.send(helpers.transfer_item(player, searched_obj, player, found_items, "undressinto", 1, searched_obj, True))
    #endregion

async def setup(bot: commands.Bot):
    await bot.add_cog(ItemCMDs(bot))
import typing

from discord.ext import commands
from discord import app_commands
import discord

import utils.data as data
import utils.helpers as helpers
import utils.autocompletes as autocompletes

class LookGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="look", description="Look at something in your environment to see further details.")
    
    #region /look item
    @app_commands.command(name = "item", description = "Get the description of an item in your current room.")
    @app_commands.describe(item_name = "The name of the item you wish to look at.")
    @app_commands.autocomplete(item_name=autocompletes.room_items_autocomplete)
    async def lookitem(self, interaction: discord.Interaction, item_name: str):
        channel_id = interaction.channel_id
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        current_room = helpers.get_room_from_id(channel_id)

        if await helpers.check_paused(player, interaction):
            return
        if await helpers.check_room_exists(interaction, current_room):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", item_name):
            return

        await interaction.response.defer(thinking=True)
        
        item_list = current_room.get_items()

        if len(item_list) == 0:
            await interaction.followup.send("*No items could be found in the room.*")
            return
        
        searched_item = None
        for item in item_list:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(item_name):
                searched_item = item
        
        if searched_item is None:
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/items` to see a list of all the items in the current room.*")
            return
        
        if player is not None:
            if searched_item.get_desc() == '':
                await interaction.followup.send(f"***{player.get_name()}** looked at the item **{searched_item.get_name()}**:*\n\n__`{searched_item.get_name()}`__\n\n__`Weight`__: `{str(searched_item.get_weight())}`\n__`Wearable`__: `{str(searched_item.get_wearable_state())}`")
                return
            else:
                await interaction.followup.send(f"***{player.get_name()}** looked at the item **{searched_item.get_name()}**:*\n\n__`{searched_item.get_name()}`__\n\n__`Weight`__: `{str(searched_item.get_weight())}`\n__`Wearable`__: `{str(searched_item.get_wearable_state())}`\n\n{searched_item.get_desc()}")
            return
        
        if searched_item.get_desc() == '':
            await interaction.followup.send(f"*Looked at the item **{searched_item.get_name()}**:*\n\n__`{searched_item.get_name()}`__\n\n__`Weight`__: `{str(searched_item.get_weight())}`\n__`Wearable`__: `{str(searched_item.get_wearable_state())}`")
            return

        await interaction.followup.send(f"*Looked at the item **{searched_item.get_name()}**:*\n\n__`{searched_item.get_name()}`__\n\n__`Weight`__: `{str(searched_item.get_weight())}`\n__`Wearable`__: `{str(searched_item.get_wearable_state())}`\n\n{searched_item.get_desc()}")
    #endregion
    #region /look object
    @app_commands.command(name = "object", description = "Get the description of an object in your current room.")
    @app_commands.describe(object_name = "The name of the object you wish to look at.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete)
    async def lookobject(self, interaction: discord.Interaction, object_name: str):
        channel_id = interaction.channel_id
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        current_room = helpers.get_room_from_id(channel_id)

        if await helpers.check_paused(player, interaction):
            return
        searched_obj = await helpers.check_object_exists(interaction, current_room, object_name)
        if searched_obj is None:
            return
        if await helpers.handle_smart_autocomplete(interaction, "object", object_name):
            return

        await interaction.response.defer(thinking=True)

        is_locked = 'Locked' if searched_obj.get_locked_state() else 'Opened'
        is_display = searched_obj.get_display_state() if hasattr(searched_obj, "isDisplay") else False

        storage_amt = ''
        used_storage = ''
        if searched_obj.get_storage() == -1:
            storage_amt = '∞'
        else:
            storage_amt = str(searched_obj.get_storage())

        used_storage = f'{len(searched_obj.get_items())}/'

        if player is not None:
            if searched_obj.get_container_state():
                if searched_obj.get_desc() == '':
                    await interaction.followup.send(
                        f"***{player.get_name()}** looked at the object **{searched_obj.get_name()}**:*\n\n__`{searched_obj.get_name()}`__\n\n__`Storage`__: `{used_storage}{storage_amt}`\n__`State`__: `{is_locked}`\n__`Display`__: `{is_display}`"
                    )
                    return
                await interaction.followup.send(
                    f"***{player.get_name()}** looked at the object **{searched_obj.get_name()}**:*\n\n__`{searched_obj.get_name()}`__\n\n__`Storage`__: `{used_storage}{storage_amt}`\n__`State`__: `{is_locked}`\n__`Display`__: `{is_display}`\n\n{searched_obj.get_desc()}"
                )
                return
            if searched_obj.get_desc() == '':
                await interaction.followup.send(f"***{player.get_name()}** looked at the object **{searched_obj.get_name()}**:*\n\n__`{searched_obj.get_name()}`__")
                return
            await interaction.followup.send(f"***{player.get_name()}** looked at the object **{searched_obj.get_name()}**:*\n\n__`{searched_obj.get_name()}`__\n\n{searched_obj.get_desc()}")
            return

        container_state = searched_obj.get_container_state()
        if container_state == True:
            if searched_obj.get_desc() == '':
                await interaction.followup.send(
                    f"*Looked at the object **{searched_obj.get_name()}**:*\n\n__`{searched_obj.get_name()}`__\n\n__`Storage`__: `{storage_amt}`\n__`State`__: `{is_locked}`\n__`Display`__: `{is_display}`"
                )
                return
            await interaction.followup.send(
                f"*Looked at the object **{searched_obj.get_name()}**:*\n\n__`{searched_obj.get_name()}`__\n\n__`Storage`__: `{storage_amt}`\n__`State`__: `{is_locked}`\n__`Display`__: `{is_display}`\n\n{searched_obj.get_desc()}"
            )
            return

        if searched_obj.get_desc() == '':
            await interaction.followup.send(f"*Looked at the object **{searched_obj.get_name()}**:*\n\n__`{searched_obj.get_name()}`__")
            return
        await interaction.followup.send(f"*Looked at the object **{searched_obj.get_name()}**:*\n\n__`{searched_obj.get_name()}`__\n\n{searched_obj.get_desc()}")
        return
    #endregion
    #region /look inside
    @app_commands.command(name = "inside", description = "Get the description of an item inside of an object.")
    @app_commands.describe(object_name = "The name of the object you wish to look inside of.")
    @app_commands.describe(item_name = "The name of the item you wish to look at.")
    @app_commands.autocomplete(object_name=autocompletes.object_autocomplete, item_name=autocompletes.object_contents_autocomplete)
    async def lookinside(self, interaction: discord.Interaction, object_name: str, item_name: str):
        channel_id = interaction.channel_id
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        current_room = helpers.get_room_from_id(channel_id)

        if await helpers.check_paused(player, interaction):
            return
        searched_obj = await helpers.check_obj_container(interaction, current_room, object_name, player, True)
        if searched_obj is None:
            return
        if await helpers.handle_smart_autocomplete(interaction, "object", object_name):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", item_name):
            return

        await interaction.response.defer(thinking=True)

        item_list = searched_obj.get_items()

        if len(item_list) == 0:
            await interaction.followup.send(f"*No items could be found in the object **{searched_obj.get_name()}**.*")
            return

        searched_item = None
        for item in item_list:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(item_name):
                searched_item = item

        if searched_item is None:
            await interaction.followup.send(f"*Could not find the item **{item_name}** inside of the object **{searched_obj.get_name()}**. Please use `/contents` to see a list of all the items in an object.*")
            return

        if player is not None:
            if searched_item.get_desc() == '':
                await interaction.followup.send(f"***{player.get_name()}** looked inside of the object **{searched_obj.get_name()}** at the item **{searched_item.get_name()}**:*\n\n__`{searched_item.get_name()}`__\n\n__`Weight`__: `{searched_item.get_weight()}`\n__`Wearable`__: `{searched_item.get_wearable_state()}`")
            else:
                await interaction.followup.send(f"***{player.get_name()}** looked inside of the object **{searched_obj.get_name()}** at the item **{searched_item.get_name()}**:*\n\n__`{searched_item.get_name()}`__\n\n__`Weight`__: `{searched_item.get_weight()}`\n__`Wearable`__: `{searched_item.get_wearable_state()}`\n\n{searched_item.get_desc()}")
                return
        
            return
        
        if searched_item.get_desc() == '':
            await interaction.followup.send(f"*Looked inside of the object **{searched_obj.get_name()}** at the item **{searched_item.get_name()}**:*\n\n__`{searched_item.get_name()}`__\n\n__`Weight`__: `{searched_item.get_weight()}`\n__`Wearable`__: `{searched_item.get_wearable_state()}`")
            return

        await interaction.followup.send(f"*Looked inside of the object **{searched_obj.get_name()}** at the item **{searched_item.get_name()}**:*\n\n__`{searched_item.get_name()}`__\n\n__`Weight`__: `{searched_item.get_weight()}`\n__`Wearable`__: `{searched_item.get_wearable_state()}`\n\n{searched_item.get_desc()}")
    #endregion
    #region /look inventory
    @app_commands.command(name = "inventory", description = "Get the description of an item in your inventory.")
    @app_commands.describe(item_name = "The name of the item you wish to look at.")
    @app_commands.autocomplete(item_name=autocompletes.user_items_autocomplete)
    async def lookinv(self, interaction: discord.Interaction, item_name: str):
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)

        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", item_name):
            return

        await interaction.response.defer(thinking=True)

        item_list = player.get_items()

        if len(item_list) == 0:
            await interaction.followup.send(f"*No items could be found in **{player.get_name()}'s** inventory.*")
            return

        searched_item = None
        for item in item_list:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(item_name):
                searched_item = item

        if searched_item is None:
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/inventory` to see a list of items in your inventory.*")
            return

        if searched_item.get_desc() == '':
            await interaction.followup.send(f"***{player.get_name()}** looked at the item **{searched_item.get_name()}** in their inventory:*\n\n__`{searched_item.get_name()}`__\n\n__`Weight`__: `{searched_item.get_weight()}`\n__`Wearable`__: `{searched_item.get_wearable_state()}`\n\n`Item has no description.`")
            return

        await interaction.followup.send(f"***{player.get_name()}** looked at the item **{searched_item.get_name()}** in their inventory:*\n\n__`{searched_item.get_name()}`__\n\n__`Weight`__: `{searched_item.get_weight()}`\n__`Wearable`__: `{searched_item.get_wearable_state()}`\n\n{searched_item.get_desc()}")
    #endregion
    #region /look clothes
    @app_commands.command(name = "clothes", description = "Get the description of a specific clothing item you are currently wearing.")
    @app_commands.describe(clothes_name = "The name of the clothing item you wish to look at.")
    @app_commands.autocomplete(clothes_name=autocompletes.clothing_autocomplete)
    async def lookclothes(self, interaction: discord.Interaction, clothes_name: str):
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)

        if await helpers.check_valid_player(interaction, player):
            return
        if await helpers.handle_smart_autocomplete(interaction, "item", clothes_name):
            return

        await interaction.response.defer(thinking=True)

        clothes_list = player.get_clothes()

        if len(clothes_list) == 0:
            await interaction.followup.send(f"*No clothes could be found on **{player.get_name()}**.*")
            return

        searched_clothes = None
        for clothes in clothes_list:
            if helpers.simplify_string(clothes.get_name()) == helpers.simplify_string(clothes_name):
                searched_clothes = clothes

        if searched_clothes is None:
            await interaction.followup.send(f"*Could not find the clothing item **{clothes_name}**. Please use `/clothes` to see a list of clothes you are wearing.*")
            return

        if searched_clothes.get_desc() == '':
            await interaction.followup.send(f"***{player.get_name()}** looked at their clothing item **{searched_clothes.get_name()}**:*\n\n__`{searched_clothes.get_name()}`__\n\n__`Weight`__: `{searched_clothes.get_weight()}`\n__`Wearable`__: `{searched_clothes.get_wearable_state()}`")
            return

        await interaction.followup.send(f"***{player.get_name()}** looked at their clothing item **{searched_clothes.get_name()}**:*\n\n__`{searched_clothes.get_name()}`__\n\n__`Weight`__: `{searched_clothes.get_weight()}`\n__`Wearable`__: `{searched_clothes.get_wearable_state()}`\n\n{searched_clothes.get_desc()}")
    #endregion
    #region /look player
    @app_commands.command(name = "player", description = "Get the description of a player in your current room.")
    @app_commands.describe(player_name = "The name of the player you wish to look at.")
    @app_commands.autocomplete(player_name=autocompletes.players_autocomplete)
    async def lookplayer(self, interaction: discord.Interaction, player_name: str):
        player_id = interaction.user.id
        looking_player = helpers.get_player_from_id(player_id)

        if await helpers.check_paused(looking_player, interaction):
            return
        if await helpers.handle_smart_autocomplete(interaction, "player", player_name):
            return

        await interaction.response.defer(thinking=True)

        simplified = helpers.simplify_string(player_name)
        player = None

        for p in data.playerdata.values():
            if helpers.simplify_string(p.get_name()) == simplified:
                player = p

        if player is None:
            await interaction.followup.send(f"*Could not find player **{player_name}**. Please use `/players` to see a list of all players in the current room.*")
            return

        clothes_list = player.get_clothes()
        clothes_names = [f"`{clothing.get_name()}`" for clothing in clothes_list]
        all_clothes = ', '.join(clothes_names)

        if looking_player is None:
            if player.get_desc() == '':
                if len(clothes_list) == 0:
                    await interaction.followup.send(f"*Looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `No worn items.`")
                    return
                await interaction.followup.send(f"*Looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {all_clothes}")
                return
            if len(clothes_list) == 0:
                await interaction.followup.send(f"*Looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `No worn items.`\n\n{player.get_desc()}")
                return
            await interaction.followup.send(f"*Looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {all_clothes}\n\n{player.get_desc()}")
            return

        if looking_player is player:
            if player.get_desc() == '':
                if len(clothes_list) == 0:
                    await interaction.followup.send(f"***{looking_player.get_name()}** looked at themself:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `No worn items.`")
                    return
                await interaction.followup.send(f"***{looking_player.get_name()}** looked at themself:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {all_clothes}")
                return
            if len(clothes_list) == 0:
                await interaction.followup.send(f"***{looking_player.get_name()}** looked at themself:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `No worn items.`\n\n{player.get_desc()}")
                return
            await interaction.followup.send(f"***{looking_player.get_name()}** looked at themself:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {all_clothes}\n\n{player.get_desc()}")
            return


        if player.get_desc() == '':
                if len(clothes_list) == 0:
                    await interaction.followup.send(f"***{looking_player.get_name()}** looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `No worn items.`")
                    return
                await interaction.followup.send(f"***{looking_player.get_name()}** looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {all_clothes}")
                return

        if len(clothes_list) == 0:
            await interaction.followup.send(f"***{looking_player.get_name()}** looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: `No worn items.`\n\n{player.get_desc()}")
            return
        await interaction.followup.send(f"***{looking_player.get_name()}** looked at **{player.get_name()}**:*\n\n__`{player.get_name()}`__\n\n__`Wearing`__: {all_clothes}\n\n{player.get_desc()}")
    #endregion

class LookCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.add_command(LookGroup())

async def setup(bot: commands.Bot):
    await bot.add_cog(LookCMDs(bot))
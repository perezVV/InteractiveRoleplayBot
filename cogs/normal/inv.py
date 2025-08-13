import typing

from discord.ext import commands
from discord import app_commands
import discord

import utils.data as data
import utils.autocompletes as autocompletes
import utils.helpers as helpers

class InventoryCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
    #region /lookinv
    @app_commands.command(name = "lookinv", description = "Get the description of a specific item in your inventory.")
    @app_commands.describe(item_name = "The name of the item you wish to look at.")
    @app_commands.autocomplete(item_name=autocompletes.user_items_autocomplete)
    async def lookinv(self, interaction: discord.Interaction, item_name: str):
        await interaction.response.defer(thinking=True)
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)

        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake.*")
            return

        itemList = player.get_items()

        if len(itemList) == 0:
            await interaction.followup.send(f"*No items could be found in **{player.get_name()}'s** inventory.*")
            return

        searchedItem = None
        for item in itemList:
            if helpers.simplify_string(item.get_name()) == helpers.simplify_string(item_name):
                searchedItem = item

        if searchedItem is None:
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/inventory` to see a list of items in your inventory.*")
            return

        if searchedItem.get_desc() == '':
            await interaction.followup.send(f"***{player.get_name()}** looked at the item **{searchedItem.get_name()}** in their inventory:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{searchedItem.get_weight()}`\n\n__`Wearable`__: `{searchedItem.get_wearable_state()}`\n\n`Item has no description.`")
            return

        await interaction.followup.send(f"***{player.get_name()}** looked at the item **{searchedItem.get_name()}** in their inventory:*\n\n__`{searchedItem.get_name()}`__\n\n__`Weight`__: `{searchedItem.get_weight()}`\n\n__`Wearable`__: `{searchedItem.get_wearable_state()}`\n\n{searchedItem.get_desc()}")
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
    #region /lookclothes
    @app_commands.command(name = "lookclothes", description = "Get the description of a specific clothing item you are currently wearing.")
    @app_commands.describe(clothes_name = "The name of the clothing item you wish to look at.")
    @app_commands.autocomplete(clothes_name=autocompletes.clothing_autocomplete)
    async def lookclothes(self, interaction: discord.Interaction, clothes_name: str):
        await interaction.response.defer(thinking=True)
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)

        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake.*")
            return

        clothesList = player.get_clothes()

        if len(clothesList) == 0:
            await interaction.followup.send(f"*No clothes could be found on **{player.get_name()}**.*")
            return

        searchedClothes = None
        for clothes in clothesList:
            if helpers.simplify_string(clothes.get_name()) == helpers.simplify_string(clothes_name):
                searchedClothes = clothes

        if searchedClothes is None:
            await interaction.followup.send(f"*Could not find the clothing item **{clothes_name}**. Please use `/clothes` to see a list of clothes you are wearing.*")
            return

        if searchedClothes.get_desc() == '':
            await interaction.followup.send(f"***{player.get_name()}** looked at their clothing item **{searchedClothes.get_name()}**:*\n\n__`{searchedClothes.get_name()}`__\n\n__`Weight`__: `{searchedClothes.get_weight()}`\n\n`Clothing item has no description.`")
            return

        await interaction.followup.send(f"***{player.get_name()}** looked at their clothing item **{searchedClothes.get_name()}**:*\n\n__`{searchedClothes.get_name()}`__\n\n__`Weight`__: `{searchedClothes.get_weight()}`\n\n{searchedClothes.get_desc()}")
    #endregion

async def setup(bot: commands.Bot):
    await bot.add_cog(InventoryCMDs(bot))
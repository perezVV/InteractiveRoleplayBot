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

async def setup(bot: commands.Bot):
    await bot.add_cog(InventoryCMDs(bot))
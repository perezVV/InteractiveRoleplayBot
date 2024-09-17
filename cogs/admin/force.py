import typing

from discord.ext import commands
from discord import app_commands
import discord

import utils.helpers as helpers
import utils.data as data

class AdminForceCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #region /forcetake
    @app_commands.command(name = "forcetake", description = "Force a player to take an item from their room.")
    @app_commands.describe(player_name = "The name of the player you wish to take an item.")
    @app_commands.describe(item_name = "The item you wish the player to take.")
    @app_commands.describe(amount = "The amount of that item you wish the player to take.")
    @app_commands.default_permissions()
    async def forcetake(self, interaction: discord.Interaction, player_name: str, item_name: str, amount: int = 0):
        await interaction.response.defer(thinking=True)
        player = helpers.get_player_from_name(player_name)
        currRoom = player.get_room()

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send(f"***{player_name}** is not a valid player. Please use `/listplayers` to see a list of all the current players.*.")
            return

        if currRoom is None:
            await interaction.followup.send(f"***{player_name}** is not currently in a room. Please use `/drag` to bring them into a room first.*.")
            return

        invWeight = player.get_weight()
        itemList = currRoom.get_items()

        if amount in {0, 1}:
            for item in itemList:
                if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                    if (invWeight + item.get_weight()) > data.max_carry_weight:
                        await interaction.followup.send(f"***{player.get_name()}** tried to take the item **{item_name}**, but they could not fit it into their inventory.*")
                        return
                    player.add_item(item)
                    currRoom.del_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** took the item **{item_name}***.")
                    return
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/listitems` to see a list of items in the player's room.*")
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
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/listitems` to see a list of items in the player's room.*")
            return

        if len(itemsFound) < amount:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}**. Please use `/listitems` to see a list of items in the player's room.*"
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
                f"*Could not find **{amount}** of the item **{item_name}**. Please use `/listitems` to see a list of items in the player's room.*"
            )
            return
    #endregion
    #region /forcedrop
    @app_commands.command(name = "forcedrop", description = "Drop an item from a player's inventory into their current room.")
    @app_commands.describe(player_name = "The name of the player you wish to drop an item.")
    @app_commands.describe(item_name = "The item you wish for the player to drop.")
    @app_commands.describe(amount = "The amount of that item you wish for the player to drop.")
    @app_commands.default_permissions()
    async def forcedrop(self, interaction: discord.Interaction, player_name: str, item_name: str, amount: int = 0):
        await interaction.response.defer(thinking=True)
        player = helpers.get_player_from_name(player_name)
        currRoom = player.get_room()

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send(f"***{player_name}** is not a valid player. Please use `/listplayers` to see a list of all the current players.*.")
            return

        if currRoom is None:
            await interaction.followup.send(f"***{player_name}** is not currently in a room. Please use `/drag` to bring them into a room first.*.")
            return

        itemList = player.get_items()

        if amount in {0, 1}:
            for item in itemList:
                if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                    player.del_item(item)
                    currRoom.add_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** dropped the item **{item.get_name()}**.*")
                    return
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/listitems` to see a list of items in a player's inventory.*")
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
            await interaction.followup.send(f"*Could not find the item **{item_name}**. Please use `/listitems` to see a list of items in a player's inventory.*")
            return

        if len(itemsFound) < amount:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}**. Please use `/listitems` to see a list of items in a player's inventory.*"
            )
            return

        try:
            for i in range(amount):
                player.del_item(itemsFound[i])
                currRoom.add_item(itemsFound[i])
            data.save()
            await interaction.followup.send(
                f"***{player.get_name()}** dropped **{amount}** of the item **{searchedItem.get_name()}**.*"
            )
            return
        except Exception:
            await interaction.followup.send(
                f"*Could not find **{amount}** of the item **{item_name}**. Please use `/listitems` to see a list of items in a player's inventory.*"
            )
            return
    #endregion
    #region /forcewear
    @app_commands.command(name = "forcewear", description = "Make a player wear a clothing item that is currently available to them.")
    @app_commands.describe(player_name = "The name of the player you wish to wear a clothing item.")
    @app_commands.choices(container = [
        app_commands.Choice(name = "From the room", value = 0),
        app_commands.Choice(name = "From the player's inventory", value = 1)
        ])
    @app_commands.describe(item_name = "The clothing item you wish for the player to wear.")
    @app_commands.default_permissions()
    async def forcewear(self, interaction: discord.Interaction, player_name: str, container: app_commands.Choice[int], item_name: str):
        await interaction.response.defer(thinking=True)
        player = helpers.get_player_from_name(player_name)
        currRoom = player.get_room()

        midStr = ''
        midStr2 = ''
        containerVar = None

        if container.value == 0:
            containerVar = currRoom
            midStr = 'take and wear'
            midStr2 = 'took and wore'

            if containerVar is None:
                await interaction.followup.send(f"***{player_name}** is not currently in a room. Please use `/drag` to bring them into a room first.*.")
                return

        elif container.value == 1:
            containerVar = player
            midStr = 'wear'
            midStr2 = 'wore'

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send(f"***{player_name}** is not a valid player. Please use `/listplayers` to see a list of all the current players.*.")
            return

        clothesWeight = player.get_clothes_weight()
        itemList = containerVar.get_items()

        for item in itemList:
            if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                if item.get_wearable_state():
                    if (clothesWeight + item.get_weight()) > data.max_wear_weight:
                        if len(player.get_clothes()) == 0:
                            await interaction.followup.send(f"***{player.get_name()}** tried to {midStr} the item **{item.get_name()}**, but it was too heavy.*")
                            return    
                        await interaction.followup.send(f"***{player.get_name()}** tried to {midStr} the item **{item.get_name()}**, but they were wearing too much already.*")
                        return
                    player.add_clothes(item)
                    containerVar.del_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** {midStr2} the item **{item.get_name()}**.*")
                else:
                    await interaction.followup.send(f"***{player.get_name()}** tried to {midStr} the item **{item.get_name()}**, but it was not a piece of clothing.*")
                return
            
        await interaction.followup.send(f"Could not find the item **{item_name}**. Please use `/listitems` to see a list of items in a container.*")
    #endregion
    #region /forceundress
    @app_commands.command(name = "forceundress", description = "Make a player take off a clothing item they are currently wearing.")
    @app_commands.describe(player_name = "The name of the player you wish to drop a clothing item.")
    @app_commands.choices(container = [
        app_commands.Choice(name = "Drop into the room", value = 0),
        app_commands.Choice(name = "Drop into the player's inventory", value = 1)
        ])
    @app_commands.describe(item_name = "The clothing item you wish for a player to drop.")
    @app_commands.default_permissions()
    async def forceundress(self, interaction: discord.Interaction, player_name: str, container: app_commands.Choice[int], item_name: str):
        await interaction.response.defer(thinking=True)
        player = helpers.get_player_from_name(player_name)
        currRoom = player.get_room()

        midStr = ''
        midStr2 = ''
        containerVar = None

        if container.value == 0:
            containerVar = currRoom
            midStr = 'take off and drop'
            midStr2 = 'took off and dropped'

            if containerVar is None:
                await interaction.followup.send(f"***{player_name}** is not currently in a room. Please use `/drag` to bring them into a room first.*.")
                return

        elif container.value == 1:
            containerVar = player
            midStr = 'take off'
            midStr2 = 'took off'


        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send(f"***{player_name}** is not a valid player. Please use `/listplayers` to see a list of all the current players.*.")
            return

        if currRoom is None:
            await interaction.followup.send(f"***{player_name}** is not currently in a room. Please use `/drag` to bring them into a room first.*.")
            return

        itemList = player.get_clothes()

        for item in itemList:
            if helpers.simplify_string(item_name) == helpers.simplify_string(item.get_name()):
                if item.get_wearable_state():
                    if container.value == 1 and (player.get_weight() + item.get_weight()) > damax_carry_weight:
                        await interaction.followup.send(f"***{player.get_name()}** tried to take off **{item.get_name()}**, but they could not fit into their inventory.*")
                        return
                    player.del_clothes(item)
                    containerVar.add_item(item)
                    data.save()
                    await interaction.followup.send(f"***{player.get_name()}** {midStr2} the item **{item.get_name()}**.*")
                else:
                    await interaction.followup.send(f"***{player.get_name()}** tried to {midStr} **{item.get_name()}**, but it was not a piece of clothing... how are they wearing it?*")
                return

        await interaction.followup.send(f"*Could not find **{item_name}**. Please use `/listclothes` to see the clothes a player is wearing.*")
    #endregion

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminForceCMDs(bot))
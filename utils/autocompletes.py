import discord
from discord import app_commands
import typing

import utils.data as data
import utils.helpers as helpers

#region exits autocomplete
async def exit_name_autocomplete(interaction: discord.Interaction, room_name: str) -> typing.List[app_commands.Choice[str]]:
    id = interaction.user.id
    channel_id = interaction.channel_id
    player = helpers.get_player_from_id(id)
    currRoom = helpers.get_room_from_id(channel_id)

    if await helpers.check_paused(player, interaction):
        return []

    if player is None or player.get_name() not in data.playerdata.keys():
        return []

    if currRoom is None:
        return []

    exits = currRoom.get_exits()

    if len(exits) == 0:
        return []

    choices: typing.List[app_commands.Choice[str]] = []

    for exit in exits:
        currExit = ''
        locked_state = ''
        if exit.get_room1() == currRoom.get_name():
            currExit = exit.get_room2()
        else:
            currExit = exit.get_room1()
        if exit.get_locked_state():
            locked_state = ' (Locked)'

        choices.append(app_commands.Choice(name = currExit + locked_state, value = currExit))

    if not room_name:
        return choices

    return [choice for choice in choices if room_name.lower() in choice.name.lower()][:25]
#endregion

#region room items autocomplete
async def room_items_autocomplete(interaction: discord.Interaction, item_name: str) -> typing.List[app_commands.Choice[str]]:
    channel_id = interaction.channel_id
    player_id = interaction.user.id
    player = helpers.get_player_from_id(player_id)
    currRoom = helpers.get_room_from_id(channel_id)

    if await helpers.check_paused(player, interaction):
        return []

    if currRoom is None:
        return []

    itemList = currRoom.get_items()

    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=item.get_name(), value=item.get_name())
        for item in itemList
    ]
    if not item_name:
        return choices

    return [choice for choice in choices if item_name.lower() in choice.name.lower()][:25]
#endregion

#region players autocomplete
async def players_autocomplete(interaction: discord.Interaction, player_name: str) -> typing.List[app_commands.Choice[str]]:
    channel_id = interaction.channel_id
    player_id = interaction.user.id
    player = helpers.get_player_from_id(player_id)
    currRoom = helpers.get_room_from_id(channel_id)

    if await helpers.check_paused(player, interaction):
        return []
    
    playerList: typing.List[data.Player] = []
    for thisPlayer in data.playerdata.values():
        if room := thisPlayer.get_room():
            if room.get_name() == currRoom.get_name():
                playerList.append(thisPlayer)
    
    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=thisPlayer.get_name(), value=thisPlayer.get_name())
        for thisPlayer in playerList
    ]
    if not player_name:
        return choices
    
    return[choice for choice in choices if player_name.lower() in choice.name.lower()][:25]
#endregion

#region user items autocomplete
async def user_items_autocomplete(interaction: discord.Interaction, item_name: str) -> typing.List[app_commands.Choice[str]]:
    id = interaction.user.id
    player = helpers.get_player_from_id(id)

    if await helpers.check_paused(player, interaction):
        return []

    if player is None or player.get_name() not in data.playerdata.keys():
        return []

    playerItems = player.get_items()

    if len(playerItems) == 0:
        return []

    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=item.get_name(), value=item.get_name())
        for item in playerItems
    ]
    return [choice for choice in choices if item_name.lower() in choice.name.lower()][:25]
#endregion

#region clothing autocomplete
async def clothing_autocomplete(interaction: discord.Interaction, item_name: str) -> typing.List[app_commands.Choice[str]]:
    id = interaction.user.id
    player = helpers.get_player_from_id(id)

    if await helpers.check_paused(player, interaction):
        return []

    if player is None or player.get_name() not in data.playerdata.keys():
        return []

    playerClothes = player.get_clothes()

    if len(playerClothes) == 0:
        return []

    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=clothes.get_name(), value=clothes.get_name())
        for clothes in playerClothes
    ]
    return [choice for choice in choices if item_name.lower() in choice.name.lower()][:25]
#endregion

#region object autocomplete
async def object_autocomplete(interaction: discord.Interaction, object_name: str) -> typing.List[app_commands.Choice[str]]:
    channel_id = interaction.channel_id
    player_id = interaction.user.id
    player = helpers.get_player_from_id(player_id)
    currRoom = helpers.get_room_from_id(channel_id)

    if await helpers.check_paused(player, interaction):
        return []

    if currRoom is None:
        return []

    objList = currRoom.get_objects()

    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=obj.get_name(), value=obj.get_name())
        for obj in objList
    ]
    return [choice for choice in choices if object_name.lower() in choice.name.lower()][:25]
#endregion

#region object contents autocomplete
async def object_contents_autocomplete(interaction: discord.Interaction, item_name: str) -> typing.List[app_commands.Choice[str]]:
    if "object_name" not in interaction.namespace:
        return []
    object_name: str = interaction.namespace["object_name"]

    channel_id = interaction.channel_id
    player_id = interaction.user.id
    player = helpers.get_player_from_id(player_id)
    currRoom = helpers.get_room_from_id(channel_id)

    if await helpers.check_paused(player, interaction):
        return []

    if currRoom is None:
        return []

    searchedObj = None
    for object in currRoom.get_objects():
        if helpers.simplify_string(object.get_name()) == helpers.simplify_string(object_name):
            searchedObj = object

    if searchedObj is None:
        return []

    if not searchedObj.get_container_state():
        return []

    if searchedObj.get_locked_state():
        return []

    itemList = searchedObj.get_items()
    if len(itemList) == 0:
        return []

    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=item.get_name(), value=item.get_name())
        for item in itemList
    ]
    return [choice for choice in choices if item_name.lower() in choice.name.lower()][:25]
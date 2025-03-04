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

    is_display = searchedObj.get_display_state() if hasattr(searchedObj, "isDisplay") else False

    if searchedObj is None:
        return []

    if not searchedObj.get_container_state():
        return []

    if searchedObj.get_locked_state() and not is_display:
        return []

    itemList = searchedObj.get_items()
    if len(itemList) == 0:
        return []

    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=item.get_name(), value=item.get_name())
        for item in itemList
    ]
    return [choice for choice in choices if item_name.lower() in choice.name.lower()][:25]
#endregion

#region admin players autocomplete
async def admin_players_autocomplete(interaction: discord.Interaction, player_name: str) -> typing.List[app_commands.Choice[str]]:
    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=player.get_name(), value=player.get_name())
        for player in data.playerdata.values()
    ]
    if not player_name:
        return choices
    
    return[choice for choice in choices if player_name.lower() in choice.name.lower()][:25]
#endregion

#region admin rooms autocomplete
async def admin_rooms_autocomplete(interaction: discord.Interaction, room_name: str) -> typing.List[app_commands.Choice[str]]:
    room_names = [room.get_name() for room in data.roomdata.values()]

    sorted_rooms = sorted(
        (name for name in room_names if room_name.lower() in name.lower()),
        key=lambda name: (name.lower() != room_name.lower(), not name.lower().startswith(room_name.lower()))
    )

    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=name, value=name) for name in sorted_rooms[:25]
    ][:25]
    
    return choices
#endregion

#region admin exit autocomplete
async def admin_exit_autocomplete(interaction: discord.Interaction, room_two_name: str) -> typing.List[app_commands.Choice[str]]:
    room_one_name = interaction.namespace.room_one_name
    room_one = helpers.get_room_from_name(room_one_name)
    if not room_one:
        return []
    
    exits = room_one.get_exits()
    if len(exits) == 0:
        return []

    exit_names = []
    for exit in exits:
        currExit = ''
        locked_state = ''
        if exit.get_room1() == room_one.get_name():
            currExit = exit.get_room2()
        else:
            currExit = exit.get_room1()
        if exit.get_locked_state():
            locked_state = ' (Locked)'

        exit_names.append(currExit + locked_state)

    sorted_exits = sorted(
        (name for name in exit_names if room_two_name.lower() in name.lower()),
        key=lambda name: (name.lower() != room_two_name.lower(), not name.lower().startswith(room_two_name.lower()))
    )

    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=name, value=name.split(" (Locked)")[0]) for name in sorted_exits[:25]
    ]
    
    return choices
#endregion

#region admin object autocomplete
async def admin_object_autocomplete(interaction: discord.Interaction, object_name: str) -> typing.List[app_commands.Choice[str]]:
    room_name = getattr(interaction.namespace, 'room_name', getattr(interaction.namespace, 'object_room_name', None))
    if not room_name:
        return []
    
    room = helpers.get_room_from_name(room_name)
    if not room:
        return []
    
    
    objList = room.get_objects()

    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=obj.get_name(), value=obj.get_name())
        for obj in objList
    ]
    return [choice for choice in choices if object_name.lower() in choice.name.lower()][:25]

#endregion

#region admin item autocomplete
async def admin_item_autocomplete(interaction:discord.Interaction, item_name: str) -> typing.List[app_commands.Choice[str]]:
    container_type = interaction.namespace.container
    container_name = interaction.namespace.container_name
    object_room_name = getattr(interaction.namespace, "object_room_name", None)

    items = []

    if container_type == 0:
        room = helpers.get_room_from_name(container_name)
        if room:
            items = room.get_items()
    
    elif container_type == 1:
        player = helpers.get_player_from_name(container_name)
        if player:
            items = player.get_items()

    elif container_type == 2:
        player = helpers.get_player_from_name(container_name)
        if player:
            items = player.get_clothes()

    elif container_type == 3:
        if not object_room_name:
            return []
        room = helpers.get_room_from_name(object_room_name)
        if room:
            searchedObj = None
            for object in room.get_objects():
                if helpers.simplify_string(object.get_name()) == helpers.simplify_string(container_name):
                    searchedObj = object
            if searchedObj and searchedObj.get_container_state() and not searchedObj.get_locked_state():
                items = searchedObj.get_items()
    
    item_names = [item.get_name() for item in items]
    sorted_items = sorted(
        (name for name in item_names if item_name.lower() in name.lower()),
        key=lambda name: (name.lower() != item_name.lower(), not name.lower().startswith(item_name.lower()))
    )

    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=name, value=name) for name in sorted_items[:25]
    ]

    return choices
#endregion

#region admin item container autocomplete
async def admin_container_autocomplete(interaction:discord.Interaction, container_name: str) -> typing.List[app_commands.Choice[str]]:
    container_type = interaction.namespace.container

    if container_type == 0:
        return await admin_rooms_autocomplete(interaction, container_name)
    
    elif container_type == 1 or container_type == 2:
        return await admin_players_autocomplete(interaction, container_name)

    elif container_type == 3:
        if not hasattr(interaction.namespace, "object_room_name"):
            return []
        return await admin_object_autocomplete(interaction, container_name)

    return []
#endregion

#region admin force item autocomplete TODO: room.get_items() doesn't work somehow??
async def admin_force_item_autocomplete(interaction:discord.Interaction, item_name: str) -> typing.List[app_commands.Choice[str]]:
    container = getattr(interaction.namespace, "container", None)
    if container is None:
        container = 0
    player_name = interaction.namespace.player_name
    player = helpers.get_player_from_name(player_name)
    if not player:
        return []

    if container == 0:
        room = player.get_room()
        if room is None:
            return []
        itemList = room.get_items()

    elif container == 1:
        itemList = player.get_items()
    else:
        itemList = []
    
    itemNames = [item.get_name() for item in itemList]
    print(itemNames)

    choices: typing.List[app_commands.Choice[str]] = [
        app_commands.Choice(name=item.get_name(), value=item.get_name())
        for item in itemNames
    ]
    if not item_name:
        return choices

    return [choice for choice in choices if item_name.lower() in choice.name.lower()][:25]

#endregion
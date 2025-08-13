import typing
import discord
import asyncio

from discord import app_commands
from collections import defaultdict
from utils.data import Player, Room, Item, Object, playerdata, roomdata

# maximum number of choices discord allows in an autocomplete list
MAX_CHOICES = 25
# autocomplete helper for viewing more items
hidden_items_cache = defaultdict(list)
hidden_items_lock = asyncio.Lock()

#region Get Player methods

#region Get player from ID
def get_player_from_id(player_id: typing.Union[str, int, None]) -> typing.Optional[Player]:
    for player in playerdata.values():
        if player.get_id() == player_id:
            return player
#endregion
#region Get player from name
def get_player_from_name(name: str) -> typing.Optional[Player]:
    for player in playerdata.values():
        if simplify_string(player.get_name()) == simplify_string(name):
            return player
#endregion

#endregion


#region Get Room methods

#region Get room from ID
def get_room_from_id(room_id: typing.Union[str, int, None]) -> typing.Optional[Room]:
    for room in roomdata.values():
        if room.get_id() == room_id:
            return room
#endregion
#region Get room from name
def get_room_from_name(name: str) -> typing.Optional[Room]:
    for room in roomdata.values():
        if simplify_string(room.get_name()) == simplify_string(name):
            return room
#endregion

#endregion


#region Miscellaneous methods

#region Find items with shared name
def find_items(name: str) -> typing.List[typing.Tuple[Item, str]]:
    
    searched_name = simplify_string(name)
    foundItems = []
    
    for room in roomdata.values():
        foundItems.extend(
            (item, f"Room: `{room.get_name()}`") for item in room.get_items() if simplify_string(item.get_name()) == searched_name
        )

        for object in room.get_objects():
            if object.get_container_state():
                foundItems.extend(
                    (item, f"Object: `{object.get_name()}` in the room `{room.get_name()}`") for item in object.get_items() if simplify_string(item.get_name()) == searched_name
                )
                
    for player in playerdata.values():
        foundItems.extend(
            (item, f"Player inventory: `{player.get_name()}`") for item in player.get_items() if simplify_string(item.get_name()) == searched_name
        )

    for player in playerdata.values():
                foundItems.extend(
            (item, f"Player clothing: `{player.get_name()}`") for item in player.get_clothes() if simplify_string(item.get_name()) == searched_name
        )
    
    return foundItems
#endregion
#region Simplify string
def simplify_string(string: str) -> str:
    return string.replace(' ', '').lower()
#endregion
#region Format description
def format_desc(desc: str) -> str:
    lines = desc.split('\\n')
    formattedDesc = ''
    for line in lines:
        formattedDesc += (line + '\n')
    return formattedDesc
#endregion
#region Autocomplete limit workaround
async def choice_limit(interaction: discord.Interaction, element_type: str, choices: list[app_commands.Choice[str]]) -> list[app_commands.Choice[str]]:
    if len(choices) <= MAX_CHOICES:
        return choices
    
    visible = choices[:MAX_CHOICES - 1]
    hidden = choices[MAX_CHOICES - 1:]

    more_label = f"[View {len(hidden)} more {element_type}s...]"
    visible.append(app_commands.Choice(name=more_label, value="__SHOW_MORE__"))

    async with hidden_items_lock:
        hidden_items_cache[(interaction.user.id, interaction.channel_id)] = hidden

    return visible
#endregion
#region Handle "view more" choice
async def handle_view_more(interaction: discord.Interaction, element_type: str, value: str) -> bool:
    if value != "__SHOW_MORE__":
        return False
    
    async with hidden_items_lock:
        hidden = hidden_items_cache.get((interaction.user.id, interaction.channel_id), [])
    
    if not hidden:
        await interaction.response.send_message("*No more {element_type}s to show.*", ephemeral=True)
        return True
    
    hidden_names = "\n- ".join(f"`{choice.name}`" for choice in hidden)
    await interaction.response.send_message(f"*Remaining {element_type}s:*\n\n- {hidden_names}", ephemeral=True)

    async with hidden_items_lock:
        hidden_items_cache.pop((interaction.user.id, interaction.channel_id), None)
    
    return True
#endregion

#endregion


#region Validation methods

#region Check if player is paused TODO: swap interaction/player; currently many commands still just use this command so it would break a lot to swap them rn
async def check_paused(player: typing.Optional[Player], interaction: discord.Interaction) -> bool:
    if player is not None and player.is_paused():
        await interaction.followup.send(content="*Player commands are currently paused. Please wait until the admin unpauses your ability to use player commands.*", ephemeral=True)
        return True
    return False
#endregion
#region Check if player exists
async def check_player_exists(interaction: discord.Interaction, player: typing.Optional[Player]) -> bool:
    if player == None or not player.get_name() in playerdata.keys():
        await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake.")
        return True
    return False
#endregion
#region Check if this is a valid player interaction
async def check_valid_player(interaction: discord.Interaction, player: Player) -> bool:
    if await check_paused(player, interaction):
        return True
    if await check_player_exists(interaction, player):
        return True
    return False
#endregion

#region Check if the player is in a room
async def check_room_exists(interaction: discord.Interaction, room: typing.Optional[Room]) -> bool:
    if room is None:
        await interaction.followup.send("*You are not currently in a room. Please contact an admin if you believe this is a mistake.*")
        return True
    return False
#endregion
#region Check if object exists
async def check_object_exists(interaction: discord.Interaction, room: typing.Optional[Room], object_name: str) -> typing.Optional[Object]:
    if await check_room_exists(interaction, room):
        return None
    
    searched_obj = None
    for obj in room.get_objects():
        if simplify_string(obj.get_name()) == simplify_string(object_name):
            searched_obj = obj
            break
    
    if searched_obj is None:
        await interaction.followup.send(f"*Could not find the object **{object_name}**. Please use `/objects` to see a list of all the objects in the current room.*")
        return None
    
    return searched_obj
#endregion
#region Check if object is a container
async def check_obj_container(interaction: discord.Interaction, room: typing.Optional[Room], object_name: str, player: Player) -> typing.Optional[Object]:
    
    searched_obj = await check_object_exists(interaction, room, object_name)

    if searched_obj is None:
        return None
    
    if not searched_obj.get_container_state():
            await interaction.followup.send(f"***{player.get_name()}** tried to use the object **{searched_obj.get_name()}**, but it was not a container.*")
            return None

    if searched_obj.get_locked_state():
        await interaction.followup.send(f"***{player.get_name()}** tried to use the object **{searched_obj.get_name()}**, but it was locked.*")
        return None
    
    return searched_obj
#endregion

#endregion
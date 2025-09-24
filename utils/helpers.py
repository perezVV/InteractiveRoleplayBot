import typing
import discord
import asyncio

from typing import Union, Optional
from discord import app_commands
from collections import defaultdict
from utils.data import Player, Room, Item, Object, playerdata, roomdata, save, get_max_carry_weight, get_max_wear_weight
from utils.messages import ITEM_MESSAGES, INVALID_MESSAGES

# maximum number of choices discord allows in an autocomplete list
MAX_CHOICES = 25
# autocomplete helper for viewing more items
hidden_items_cache = defaultdict(list)
hidden_items_lock = asyncio.Lock()

Container = Union["Room", "Object", "Player"]

#region Get Class methods

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


#region Validation methods

#region Check if player is paused TODO: swap interaction/player for parity; currently many commands still just use this command so it would break a lot to swap them rn. wait until the end
async def check_paused(player: typing.Optional[Player], interaction: discord.Interaction) -> bool:
    if player is not None and player.is_paused():
        await interaction.response.send_message(content="*Player commands are currently paused. Please wait until an admin unpauses.*", ephemeral=True)
        return True
    return False
#endregion
#region Check if player exists
async def check_player_exists(interaction: discord.Interaction, player: typing.Optional[Player]) -> bool:
    if player == None or not player.get_name() in playerdata.keys():
        await interaction.response.send_message("*You are not a valid player. Please contact an admin if you believe this is a mistake.", ephemeral=True)
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
        await interaction.response.send_message("*You are not currently in a room. Please contact an admin if you believe this is a mistake.*")
        return True
    return False
#endregion
#region Check if object exists
async def check_object_exists(interaction: discord.Interaction, room: typing.Optional[Room], object_name: str) -> typing.Optional[Object]:
    if await check_room_exists(interaction, room):
        return None
    
    if len(room.get_objects()) == 0:
        await interaction.response.send_message("*No objects could be found in the room.*")
        return

    searched_obj = None
    for obj in room.get_objects():
        if simplify_string(obj.get_name()) == simplify_string(object_name):
            searched_obj = obj
            break
    
    if searched_obj is None:
        await interaction.response.send_message(f"*Could not find the object **{object_name}**. Please use `/objects` to see a list of all the objects in the current room.*")
        return None
    
    return searched_obj
#endregion
#region Check if object is a container
async def check_obj_container(interaction: discord.Interaction, room: typing.Optional[Room], object_name: str, player: Player, display_matters: bool = False) -> typing.Optional[Object]:
    
    searched_obj = await check_object_exists(interaction, room, object_name)

    if searched_obj is None:
        return None
    
    if not searched_obj.get_container_state():
            await interaction.response.send_message(f"***{player.get_name()}** tried to use the object **{searched_obj.get_name()}**, but it was not a container.*")
            return None

    is_display = False
    if display_matters:
        is_display = searched_obj.get_display_state() if hasattr(searched_obj, "isDisplay") else False

    if searched_obj.get_locked_state():
        if display_matters and is_display:
            return searched_obj
        await interaction.response.send_message(f"***{player.get_name()}** tried to use the object **{searched_obj.get_name()}**, but it was locked.*")
        return None
    
    return searched_obj
#endregion

#endregion


#region Miscellaneous methods

#region Find all global items with a shared name
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
#region Find all local items with a shared name
async def find_items_in_list(
        interaction: discord.Interaction, 
        item_list: typing.List[Item], 
        item_name: str, 
        amount: int = 0, 
        message_type: str = "None", 
        source: typing.Optional[Container] = None,
        is_clothing: bool = False
        ) -> typing.List[Item]:
    found_items = [item for item in item_list if simplify_string(item.get_name()) == simplify_string(item_name)]

    if amount < 0:
        await interaction.followup.send(INVALID_MESSAGES["items"]["negative"](amount=amount))
        return None

    if not found_items:
        await interaction.followup.send(ITEM_MESSAGES[message_type]["not_found"](item_name=item_name, obj=source))
        return None
    
    if len(found_items) < amount and not is_clothing:
        await interaction.followup.send(ITEM_MESSAGES[message_type]["not_enough"](amount=amount, item_name=item_name, obj=source))
        return None

    if is_clothing:
        wearable_item = next((item for item in found_items if item.get_wearable_state()), None)
        if not wearable_item:
            await interaction.followup.send(ITEM_MESSAGES[message_type]["not_wearable"](player=get_player_from_id(interaction.user.id), item=found_items[0], obj=source))
            return None
        return [wearable_item]

    if amount in (0, 1):
        return found_items[:1]
    else:
        return found_items[:amount]
#endregion

#region Check if an item can fit into the player's inventory/clothes
async def can_carry(
        interaction: discord.Interaction, 
        item_list: typing.List[Item], 
        player: Player, 
        message_type: str, 
        amount: int = 0, 
        source: typing.Optional[Container] = None,
        is_clothing: bool = False,
        ) -> bool:
    current_weight = player.get_clothes_weight() if is_clothing else player.get_weight()
    max_weight = get_max_wear_weight() if is_clothing else get_max_carry_weight()

    if amount in (0, 1):
        if (current_weight + item_list[0].get_weight() > max_weight):
            if is_clothing and item_list[0].get_weight() > max_weight:
                await interaction.followup.send(ITEM_MESSAGES[message_type]["heavy"](player=player, item=item_list[0], obj=source))
                return False
            await interaction.followup.send(ITEM_MESSAGES[message_type]["full"](player=player, item=item_list[0], obj=source))
            return False
        return True

    if amount > 1:
        accumulated_weight = sum(item_list[i].get_weight() for i in range(amount))
        if (current_weight + accumulated_weight) > max_weight:
            await interaction.followup.send(ITEM_MESSAGES[message_type]["full_multiple"](player=player, item=item_list[0], amount=amount, obj=source))
            return False
        return True
#endregion
#region Check if an item can fit into an object
async def can_store(
        interaction: discord.Interaction,
        player: Player,
        obj: Object,
        item_list: typing.List[Item],
        message_type: str,
        amount: int = 0
        ) -> bool:
    max_storage_amt = obj.get_storage()
    obj_contents = obj.get_items()

    if amount in (0, 1):
        if (len(obj_contents) + 1) > max_storage_amt and obj.get_storage() != -1:
            await interaction.followup.send(ITEM_MESSAGES[message_type]["full"](player=player, item=item_list[0], obj=obj))
            return False
        return True
    
    if amount > 1:
        accumulated_storage = len(range(amount))
        if (len(obj_contents) + accumulated_storage) > max_storage_amt and obj.get_storage() != -1:
            await interaction.followup.send(ITEM_MESSAGES[message_type]["full_multiple"](player=player, amount=amount, item=item_list[0], obj=obj))
            return False
        return True
#endregion
#region Transfer an item between containers
def transfer_item(
    source: Container, 
    dest: Container, 
    player: Player,
    item_list: typing.List[Item], 
    message_type: str, 
    amount: int = 0, 
    obj: Object = None,
    is_clothes_source: bool = False, 
    is_clothes_dest: bool = False
    ) -> str:
    
    def add_to(c: Container, item: Item, is_clothing: bool):
        return c.add_clothes(item) if is_clothing else c.add_item(item)
    
    def delete_from(c: Container, item: Item, is_clothing: bool):
        return c.del_clothes(item) if is_clothing else c.del_item(item)
    
    if amount in (0, 1):
        add_to(dest, item_list[0], is_clothes_dest)
        delete_from(source, item_list[0], is_clothes_source)
        save()
        return ITEM_MESSAGES[message_type]["single"](player=player, item=item_list[0], obj=obj)
    
    if amount > 1:
        for i in range(amount):
            add_to(dest, item_list[i], is_clothes_dest)
            delete_from(source, item_list[i], is_clothes_source)
            save()
        return ITEM_MESSAGES[message_type]["multiple"](player=player, item=item_list[0], amount=amount, obj=obj)
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
        hidden_items_cache[(interaction.user.id, interaction.channel_id)] = {
            "hidden": hidden,
            "element_type": element_type
        }

    return visible
#endregion
#region Handle smart autocomplete
async def handle_smart_autocomplete(interaction: discord.Interaction, value: str, extra_value: str = "") -> bool:
    if value and extra_value != "__SHOW_MORE__":
        return False
    
    async with hidden_items_lock:
        cache = hidden_items_cache.get((interaction.user.id, interaction.channel_id), [])
    
    if not cache:
        await interaction.response.send_message("*No more options to show.*", ephemeral=True)
        return True
    
    hidden = cache["hidden"]
    element_type = cache["element_type"]

    hidden_names = "\n- ".join(f"`{choice.name}`" for choice in hidden)
    await interaction.response.send_message(f"*Remaining {element_type}s:*\n\n- {hidden_names}", ephemeral=True)

    async with hidden_items_lock:
        hidden_items_cache.pop((interaction.user.id, interaction.channel_id), None)
    
    return True
#endregion

#endregion
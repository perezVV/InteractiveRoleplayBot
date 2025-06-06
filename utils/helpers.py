import typing
import discord

from utils.data import Player, Room, Item, playerdata, roomdata




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
#region Check if player is paused
async def check_paused(player: typing.Optional[Player], interaction: discord.Interaction) -> bool:
    if player is not None and player.is_paused():
        await interaction.followup.send(content="*Player commands are currently paused. Please wait until the admin unpauses your ability to use player commands.*", ephemeral=True)
        return True
    return False
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

#endregion
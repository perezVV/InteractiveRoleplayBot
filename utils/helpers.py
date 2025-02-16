import typing
import discord

from utils.data import Player, Room, playerdata, roomdata

def simplify_string(string: str) -> str:
    return string.replace(' ', '').lower()
#endregion

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

#region Check if player is paused
async def check_paused(player: typing.Optional[Player], interaction: discord.Interaction) -> bool:
    if player is not None and player.is_paused():
        await interaction.followup.send(content="*Player commands are currently paused. Please wait until the admin unpauses your ability to use player commands.*", ephemeral=True)
        return True
    return False
#endregion
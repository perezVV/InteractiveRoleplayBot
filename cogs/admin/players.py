from discord.ext import commands
from discord import app_commands
import discord

import utils.autocompletes as autocompletes
import utils.helpers as helpers
import utils.data as data

class AdminPlayerCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #region /addplayer
    @app_commands.command(name = "addplayer", description = "Add a new player to the experience.")
    @app_commands.describe(player_name = "The new player's name.")
    @app_commands.describe(player_id = "The Discord ID of the user that controls the player.")
    @app_commands.describe(desc = "The description of the player you wish to add to the experience.")
    @app_commands.default_permissions()
    async def addplayer(self, interaction: discord.Interaction, player_name: str, player_id: str, desc: str = ''):
        await interaction.response.defer(thinking=True)

        if player_name in data.playerdata.keys():
            await interaction.followup.send(f"*Player **{player_name}** already exists. Please use a different name.*")
            return

        try:
            player_id = int(player_id)
        except ValueError:
            await interaction.followup.send(
                "*A user ID must be made up entirely of integers. Please enter a valid user ID.*"
            )
            return

        if interaction.guild.get_member(player_id) is None:
            await interaction.followup.send(
                f"*Could not find <@{player_id}>. Please enter a valid user ID.*"
            )
            return

        if player := helpers.get_player_from_id(player_id):
            await interaction.followup.send(
                f"*<@{player_id}> is already connected to the player **{player.get_name()}**.*"
            )
            return

        data.playerdata[player_name] = data.Player(player_name, player_id, desc)
        data.save()
        await interaction.followup.send(
            f"*Player **{player_name}** connected to <@{player_id}>.*"
        )
    #endregion
    #region /delplayer
    @app_commands.command(name = "delplayer", description = "Remove a player from the experience.")
    @app_commands.describe(player_name = "The player you wish to remove's name.")
    @app_commands.autocomplete(player_name=autocompletes.admin_players_autocomplete)
    @app_commands.default_permissions()
    async def delplayer(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer(thinking=True)

        simplified_player = helpers.simplify_string(player_name)
        simplified_player_keys = {helpers.simplify_string(key): key for key in data.playerdata.keys()}

        if simplified_player in simplified_player_keys:
            original_key = simplified_player_keys[simplified_player]
            try:
                del data.playerdata[original_key]
                data.save()
                await interaction.followup.send(f"*Deleted player **{original_key}***.")
                return
            except Exception:
                await interaction.followup.send(f"*Failed to delete **{original_key}**. Please contact the bot's developer.*")
                return
        else:
            await interaction.followup.send(f"*Could not find player **{player_name}**. Please use `/listplayers` to see all current players.*")
    #endregion
    #region /listplayers
    @app_commands.command(name = "listplayers", description = "List all the current players added to the experience.")
    @app_commands.default_permissions()
    async def listplayers(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        if len(data.playerdata) == 0:
            await interaction.followup.send("*There are currently no players.*")
            return

        playerList = ''
        for key in data.playerdata:
            currPlayer = data.playerdata[key]
            nextPlayer = ("`", currPlayer.get_name(), "`: <@", str(currPlayer.get_id()), ">")
            nextPlayer = ''.join(nextPlayer)
            playerList = playerList + "\n" + nextPlayer

        await interaction.followup.send(playerList)
    #endregion
    #region /editplayer
    @app_commands.command(name = "editplayer", description = "Edit the value of a player.")
    @app_commands.describe(player_name = "The player you wish to edit.")
    @app_commands.describe(new_name = "The new name you wish to give the player.")
    @app_commands.describe(new_desc = "The new description you wish to give the player.")
    @app_commands.autocomplete(player_name=autocompletes.admin_players_autocomplete)
    @app_commands.default_permissions()
    async def editplayer(self, interaction: discord.Interaction, player_name: str, new_name: str = '', new_desc: str = ''):
        await interaction.response.defer(thinking=True)
        player = helpers.get_player_from_name(player_name)

        if player is None:
            await interaction.followup.send(f"*Could not find the player **{player_name}**. Please use `/listplayers` to get a list of all current players.*")

        player_id = player.get_id()

        edited = ''

        if new_name != '':
            old_name = player.get_name()
            player.edit_name(new_name)
            data.playerdata[new_name] = data.playerdata[old_name]
            del data.playerdata[old_name]
            edited += f" name to **{new_name}**"
        if new_desc != '':
            player.edit_desc(new_desc)
            if edited == '':
                edited = f'{edited} description'
            else:
                edited = f'{edited} and edited their description'

        edited = f"{edited}."

        if not new_name and not new_desc:
            await interaction.followup.send(f"*Please enter a value for either `new_name` or `new_desc` to edit the player **{player.get_name}**.*")
            return

        data.save()
        await interaction.followup.send(f"*Changed <@{player_id}>'s player{edited}*")
    #endregion
    #region /pause
    @app_commands.command(name = "pause", description = "Pause all player commands.")
    @app_commands.default_permissions()
    async def pause(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        for player in data.playerdata.values():
            player.pause()
        data.save()
        await interaction.followup.send("*Game paused.*")
    #endregion
    #region /pauseplayer
    @app_commands.command(name = "pauseplayer", description = "Pause all player commands for a certain player.")
    @app_commands.describe(player_name = "The name of the player you wish to pause.")
    @app_commands.autocomplete(player_name=autocompletes.admin_players_autocomplete)
    @app_commands.default_permissions()
    async def pauseplayer(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer(thinking=True)
        player = helpers.get_player_from_name(player_name) 
        player.pause()
        data.save()
        await interaction.followup.send(f"***{player.get_name()}** paused.*")
    #endregion
    #region /unpause
    @app_commands.command(name = "unpause", description = "Unpause all player commands.")
    @app_commands.default_permissions()
    async def unpause(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        for player in data.playerdata.values():
            player.unpause()
        data.save()
        await interaction.followup.send("*Game unpaused.*")
    #endregion
    #region /unpauseplayer
    @app_commands.command(name = "unpauseplayer", description = "Unpause all player commands for a certain player.")
    @app_commands.describe(player_name = "The name of the player you wish to unpause.")
    @app_commands.autocomplete(player_name=autocompletes.admin_players_autocomplete)
    @app_commands.default_permissions()
    async def unpauseplayer(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer(thinking=True)
        player = helpers.get_player_from_name(player_name) 
        player.unpause()
        data.save()
        await interaction.followup.send(f"***{player.get_name()}** unpaused.*")
    #endregion
    #region /findplayer 
    @app_commands.command(name = "findplayer", description = "Tells which room a player is currently in.")
    @app_commands.describe(player_name = "The name of the player you wish to find.")
    @app_commands.autocomplete(player_name=autocompletes.admin_players_autocomplete)
    @app_commands.default_permissions()
    async def findplayer(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer(thinking=True)

        simplified_player = helpers.simplify_string(player_name)
        simplified_player_keys = {helpers.simplify_string(key): key for key in data.playerdata.keys()}

        if simplified_player not in simplified_player_keys:
            await interaction.followup.send(f"*Player **{player_name}** could not be found. Please use `/listplayers` to see all current players.*")
            return

        player = helpers.get_player_from_name(player_name)
        room = player.get_room()

        if room is None:
            await interaction.followup.send(f"***{player.get_name()}** is not yet in a room.*")
            return

        await interaction.followup.send(
            f"***{player.get_name()}** is currently in the room **{room.get_name()}**.*\n\n`Jump`: <#{str(room.get_id())}>"
        )
    #endregion
    #region /drag 
    @app_commands.command(name = "drag", description = "Drag a player into a room.")
    @app_commands.describe(player_name = "The name of the player that you wish to drag.")
    @app_commands.describe(room_name = "The name of the room you wish to drag the player into.")
    @app_commands.autocomplete(player_name=autocompletes.admin_players_autocomplete)
    @app_commands.autocomplete(room_name=autocompletes.admin_rooms_autocomplete)
    @app_commands.default_permissions()
    async def drag(self, interaction: discord.Interaction, player_name: str, room_name: str):
        await interaction.response.defer(thinking=True)

        simplified_player = helpers.simplify_string(player_name)
        simplified_player_keys = {helpers.simplify_string(key): key for key in data.playerdata.keys()}

        simplified_room = helpers.simplify_string(room_name)
        simplified_room_keys = {helpers.simplify_string(key): key for key in data.roomdata.keys()}

        if simplified_player not in simplified_player_keys:
            await interaction.followup.send(f"*Player **{player_name}** could not be found. Please use `/listplayers` to see all current players.*")
            return

        if simplified_room not in simplified_room_keys:
            await interaction.followup.send(f"*Room `{room_name}` could not be found. Please use `/listrooms` to see all current rooms.*")
            return

        player = helpers.get_player_from_name(player_name)
        prevRoom = player.get_room()
        room = helpers.get_room_from_name(room_name)

        if room is None:
            await interaction.followup.send(f"*Room **{room_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
            return

        player.set_room(room)
        data.save()

        if prevRoom is not None:
            prevChannel = self.bot.get_channel(int(prevRoom.get_id()))
        else:
            prevChannel = None

        channel = self.bot.get_channel(int(room.get_id()))
        user = self.bot.get_user(int(player.get_id()))

        if channel is None:
            await interaction.followup.send(f"*Could not find the channel for **{room_name}**. Is there an error in the ID?*")

        if prevRoom is not None and prevChannel is None:
            await interaction.followup.send(f"*Could not find the channel for **{prevRoom.get_name()}**. Is there an error in the ID?*")

        if user is None:
            await interaction.followup.send(f"*Could not find the user <@{player.get_id()}>. Is there an error in the ID?*")

        await interaction.followup.send(f"*Dragged **{player.get_name()}** to **{room.get_name()}**.*")

        if prevChannel is not None:
            await prevChannel.send(f"***{player.get_name()}** was dragged to **{room.get_name()}**.*")
            await channel.send(f"***{player.get_name()}** entered from **{prevRoom.get_name()}**.*")
        else:
            await channel.send(f"***{player.get_name()}** entered the room.*")

        if prevChannel is not None:
            await prevChannel.set_permissions(user, read_messages = False)

        await channel.set_permissions(user, read_messages = True)
    #endregion 
    #region /dragall
    @app_commands.command(name = "dragall", description = "Drag all players into a room.")
    @app_commands.describe(room_name = "The name of the room you wish to drag the player into.")
    @app_commands.default_permissions()
    async def dragall(self, interaction: discord.Interaction, room_name: str):
        await interaction.response.defer(thinking=True)
        room = helpers.get_room_from_name(room_name)
        for player in data.playerdata.values():
            prevRoom = player.get_room()

            if room is None:
                await interaction.followup.send(f"*Room **{room_name}** could not be found. Please use `/listrooms` to see all current rooms.*")
                return
            
            player.set_room(room)
            data.save()

            if prevRoom is not None:
                prevChannel = self.bot.get_channel(int(prevRoom.get_id()))
            else:
                prevChannel = None

            channel = self.bot.get_channel(int(room.get_id()))
            user = self.bot.get_user(int(player.get_id()))

            if channel is None:
                await interaction.followup.send(f"*Could not find the channel for **{room_name}**. Is there an error in the ID?*")
            
            if prevRoom is not None and prevChannel is None:
                await interaction.followup.send(f"*Could not find the channel for **{prevRoom.get_name()}**. Is there an error in the ID?*")

            if user is None:
                await interaction.followup.send(f"*Could not find the user <@{player.get_id()}>. Is there an error in the ID?*")

            if prevChannel is not None:
                await prevChannel.set_permissions(user, read_messages = False)
            
            await channel.set_permissions(user, read_messages = True)
        
        await interaction.followup.send(f"*All players dragged to **{room.get_name()}**.*")
    #endregion
    #region /killplayer TODO: remove once /goto is fixed post-AA. currently a workaround
    @app_commands.command(name = "killplayer", description = "Gives a player the ability to see every room. Usually used when swapping from player to spectator.")
    @app_commands.describe(player_name = "The player you wish to add as a spectator.")
    @app_commands.autocomplete(player_name=autocompletes.admin_players_autocomplete)
    @app_commands.default_permissions()
    async def killplayer(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer(thinking=True)
        if len(data.roomdata) == 0:
            await interaction.followup.send("There are currently no rooms.")
            return
        
        player = helpers.get_player_from_name(player_name)

        if player is None:
            await interaction.followup.send(f"*Could not find the player **{player_name}**. Please use `/listplayers` to get a list of all current players.*")
        
        user = self.bot.get_user(int(player.get_id()))

        for key in data.roomdata:
            currRoom = data.roomdata[key]
            channel = self.bot.get_channel(int(currRoom.get_id()))
            await channel.set_permissions(user, read_messages = True)
        
        await interaction.followup.send(f"*Killed player **{player_name}**.*")
    #endregion
    #region /reviveplayer TODO: remove once /goto is fixed post-AA. currently a workaround
    @app_commands.command(name = "reviveplayer", description = "Removes a player's ability to see every room. Usually used when swapping from spectator to player.")
    @app_commands.describe(player_name = "The player you wish to bring back to the experience.")
    @app_commands.autocomplete(player_name=autocompletes.admin_players_autocomplete)
    @app_commands.default_permissions()
    async def reviveplayer(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer(thinking=True)
        if len(data.roomdata) == 0:
            await interaction.followup.send("There are currently no rooms.")
            return
        
        player = helpers.get_player_from_name(player_name)

        if player is None:
            await interaction.followup.send(f"*Could not find the player **{player_name}**. Please use `/listplayers` to get a list of all current players.*")
        
        user = self.bot.get_user(int(player.get_id()))

        for key in data.roomdata:
            currRoom = data.roomdata[key]
            if currRoom.get_id() == player.get_room().get_id():
                continue
            channel = self.bot.get_channel(int(currRoom.get_id()))
            await channel.set_permissions(user, read_messages = False)
        
        await interaction.followup.send(f"*Revived player **{player_name}**.*")
    #endregion
    #region /editcarryweight
    @app_commands.command(name = "editcarryweight", description = "Change the maximum carry weight for every player's inventory or clothes.")
    @app_commands.choices(weight_to_change = [
        app_commands.Choice(name = "Inventory", value = 0),
        app_commands.Choice(name = "Clothing", value = 1),
        ])
    @app_commands.describe(new_weight = "The new maximum weight.")
    @app_commands.default_permissions()
    async def editcarryweight(self, interaction: discord.Interaction, weight_to_change: app_commands.Choice[int], new_weight: int):
        await interaction.response.defer(thinking=True)

        changedContainer = ''

        if new_weight < 0:
            await interaction.followup.send(
                f"***{amount}** is an invalid input; please use a positive number.*"
            )
            return
        
        if weight_to_change.value == 0:
            changedContainer = "inventory"
            data.set_max_carry_weight(new_weight)

        elif weight_to_change.value == 1:
            changedContainer = "clothing"
            data.set_max_wear_weight(new_weight)
        
        data.save()
        await interaction.followup.send(f"*Changed the maximum player {changedContainer} weight to **{new_weight}**.*")
    #endregion
async def setup(bot: commands.Bot):
    await bot.add_cog(AdminPlayerCMDs(bot))
    
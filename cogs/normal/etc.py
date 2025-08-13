import io
import os
import random
import datetime
import zoneinfo

import chat_exporter
from discord.ext import commands
from discord import app_commands
import discord

import utils.autocompletes as autocompletes
import utils.data as data
import utils.helpers as helpers


class ChatHistoryButton(discord.ui.View):
    def __init__(self, link: str):
        super().__init__()

        self.add_item(discord.ui.Button(label="View in Browser", url=link))


class ETCCMDs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #region /move TODO: check for exits (once they have names!), not adjacent rooms
    @app_commands.command(name = "move", description = "Move to the room that you specify.")
    @app_commands.describe(exit_name = "The name of the exit you would like to move through.")
    @app_commands.autocomplete(exit_name=autocompletes.exit_name_autocomplete)
    async def move(self, interaction: discord.Interaction, exit_name: str):
        await interaction.response.defer(thinking=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        currRoom = None

        if await helpers.check_paused(player, interaction):
            return

        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake.*")
            return

        room = helpers.get_room_from_name(exit_name)

        if exit_name is None or exit_name.startswith("\\"):
            await interaction.followup.send(f"*You did not enter a valid room name. Please use `/exits` to see a list of exits in the current room.*")
            return

        if room is None:
            await interaction.followup.send(f"*Could not find the exit **{exit_name}**. Please use `/exits` to see a list of exits in the current room.*")
            return

        for newRoom in data.roomdata.values():
            if newRoom.get_id() == channel_id:
                currRoom = newRoom

        if currRoom is None:
            await interaction.followup.send(
                "*You are not currently in a room. Please contact an admin if you believe this is a mistake.*"
            )
            return

        exits = currRoom.get_exits()

        if len(exits) == 0:
            await interaction.followup.send(f"*There are no exits in the room **{str(currRoom.get_name())}**.*")
            return

        currExitName = None
        currExit = None
        for exit in exits:
            if exit.get_room1() == currRoom.get_name():
                if helpers.simplify_string(exit.get_room2()) == helpers.simplify_string(exit_name):
                    currExitName = exit.get_room2()
                    currExit = exit
            else:
                if helpers.simplify_string(exit.get_room1()) == helpers.simplify_string(exit_name):
                    currExitName = exit.get_room1()
                    currExit = exit

        if currExitName is None:
            await interaction.followup.send(f"*There is no exit to the room **{exit_name}** from **{currRoom.get_name()}**. Please use `/exits` to see a list of exits in the current room.*")
            return

        if currExit.get_locked_state():
            await interaction.followup.send(f"***{player.get_name()}** tried to enter the room **{currExitName}**, but the exit was locked.*")
            return

        player.set_room(room)
        data.save()

        currChannel = self.bot.get_channel(int(currRoom.get_id()))

        channel = self.bot.get_channel(int(room.get_id()))
        user = self.bot.get_user(int(player.get_id()))

        if channel is None:
            await interaction.followup.send(f"*Could not find the channel for **{exit_name}**. The room may need to be fixed — please contact an admin.*")

        if currRoom is not None and currChannel is None:
            await interaction.followup.send(f"*Could not find the channel for **{currChannel.get_name()}**. The room may need to be fixed — please contact an admin.*")

        if user is None:
            await interaction.followup.send(f"*Could not find the user <@{player.get_id()}>. The player may need to be fixed — please contact an admin.*")

        await interaction.followup.send(f"***{player.get_name()}** moved to **{currExitName}**.*")

        if currChannel is not None:
            await channel.send(f"***{player.get_name()}** entered from **{currRoom.get_name()}**.*")
        else:
            await channel.send(f"***{player.get_name()}** entered.*")

        if currChannel is not None:
            await currChannel.set_permissions(user, read_messages = None)

        await channel.set_permissions(user, read_messages = True)
    #endregion
    #region /description
    @app_commands.command(name = "description", description = "Get the room's description.")
    async def desc(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        channel_id = interaction.channel_id
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        room = helpers.get_room_from_id(channel_id)

        if await helpers.check_paused(player, interaction):
            return

        if room is None:
            await interaction.followup.send("*You are not currently in a room. Please contact an admin if you believe this is a mistake*.")
            return

        lookedAt = f"Looked around the room **{room.get_name()}**"
        topic = interaction.channel.topic

        if player is not None:
            lookedAt = f"**{player.get_name()}** looked around the room **{room.get_name()}**"
        if topic is None:
            topic = f"`{room.get_name()} has no description.`"

        await interaction.followup.send(f"*{lookedAt}*:\n\n{topic}")
    #endregion
    #region /roll
    @app_commands.command(name = "roll", description = "Roll for a random number.")
    @app_commands.describe(max_num = "The maximum number for the roll.")
    @app_commands.describe(passing_roll = "Optional; The number that the roll must be more than to be considered a passing roll.")
    async def roll(self, interaction: discord.Interaction, max_num: int, passing_roll: int = -1):
        await interaction.response.defer(thinking=True)
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)
        rollNum = random.randint(1, max_num)
        passingString = '.'

        if passing_roll != -1:
            passingString = (
                f', attempting to beat **{passing_roll}**. Roll **succeeded**!'
                if rollNum >= passing_roll
                else f', attempting to beat **{passing_roll}**. Roll **failed**.'
            )
            
        if player is not None:
            await interaction.followup.send(
                f"***{player.get_name()}** rolled **{rollNum}** out of **{max_num}**{passingString}*"
            )
            return

        if passing_roll == -1:
            passingString = ''
            
        await interaction.followup.send(
            f"*Rolled **{rollNum}** out of **{max_num}**{passingString}*"
        )
        return
    #endregion
    #region /time
    @app_commands.command(name = "time", description = "Check the current time in roleplay.")
    async def time(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        player_id = interaction.user.id
        player = helpers.get_player_from_id(player_id)

        if os.environ.get("IANA_TIMEZONE") is not None:
            t = datetime.datetime.now(zoneinfo.ZoneInfo(os.environ["IANA_TIMEZONE"]))
        else:
            t = datetime.datetime.now()
        current_time = t.strftime("%I:%M %p")

        if player is not None:
            await interaction.followup.send(f"***{player.get_name()}** checked the time:*\n`{current_time }`")
            return

        await interaction.followup.send(f"`{current_time}`")
    #endregion
    #region /chathistory
    @app_commands.command(name="chathistory", description="Get the chat history of the last 5 minutes for the current room.")
    async def chathistory(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        id = interaction.user.id
        channel_id = interaction.channel_id
        player = helpers.get_player_from_id(id)
        currRoom = None

        if await helpers.check_paused(player, interaction):
            return
        
        if player is None or player.get_name() not in data.playerdata.keys():
            await interaction.followup.send("*You are not a valid player. Please contact the admin if you believe this is a mistake.*")
            return
        
        # we don't actually need the room, but we do need to check for it
        for newRoom in data.roomdata.values():
            if newRoom.get_id() == channel_id:
                currRoom = newRoom

        if currRoom is None:
            await interaction.followup.send(
                "*You are not currently in a room. Please contact an admin if you believe this is a mistake.*"
            )
            return
        
        now = discord.utils.utcnow().replace(microsecond=0)
        messages: list[discord.Message] = []
        
        async for message in interaction.channel.history(limit=100, after=now - datetime.timedelta(minutes=5), oldest_first=False):
            messages.append(message)
            if message.author == self.bot.user and message.content.startswith(f"***{player.get_name()}** entered"):
                break  # player has entered the room, so let's stop here

        if not messages:
            await interaction.followup.send("*No messages found in the last 5 minutes.*")
            return

        
        transcript = await chat_exporter.raw_export(interaction.channel, messages, bot=self.bot)
        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"chathistory-{interaction.channel.name}-{now.isoformat()}.html",
        )

        try:
            reply = await interaction.user.send(f"Here is the chat history for the last 5 minutes in {interaction.channel.mention}.", file=transcript_file)
            link = f"{os.environ['CHATHISTORY_BASE_URL']}{reply.attachments[0].url}"
            await reply.edit(view=ChatHistoryButton(link))

            await interaction.followup.send("*Chat history sent to your DMs.*")
        except discord.Forbidden:
            await interaction.followup.send("*Could not send you the chat history. Please make sure your DMs are open.*")
        #endregion

async def setup(bot: commands.Bot):
    await bot.add_cog(ETCCMDs(bot))
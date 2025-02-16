import discord
from discord.ext import commands
from discord import app_commands

help_page_one = ("**Player Commands (Page 1/6):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/goto <room_name>`\n Allows you to move to a room that is connected to your current room.\n" +
    "`/desc`\n Shows the room's description.\n" + 
    "`/take <item_name> [amount]`\n Takes any amount of a specific item in your current room. Will not pick up an item if it goes over your inventory's weight limit.\n" + 
    "`/drop <item_name> [amount]`\n Drops any amount of a specific item you are currently holding into your current room.\n" + 
    "`/wear <item_name>`\n Allows you to wear any clothing item in your inventory. Will not let you wear a clothing item if it goes over your clothing weight limit.\n")

help_page_two = ("**Player Commands (Page 2/6):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/undress <item_name>`\n Drops any clothing item you are currently wearing into your inventory. Will not let you drop the clothing item if it goes over your inventory's weight limit.\n" + 
    "`/takewear <item_name>`\n Allows you to wear any clothing item in your current room. Will not let you wear a clothing item if it goes over your clothing weight limit.\n" + 
    "`/undressdrop <item_name>`\n Drops any clothing item you are currently wearing into your current room.\n" + 
    "`/takefrom <object_name> <item_name> [amount]`\n Takes any amount of a specific item from an object in your current room. Will not pick up an item if it goes over your inventory's weight limit.\n" + 
    "`/dropin <object_name> <item_name> [amount]`\n Drops any amount of a specific item you are currently holding into an object in your current room. Will not let you drop the item if it goes over the object's maximum storage.\n"
    )

    
help_page_three = ("**Player Commands (Page 3/6):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/items`\n Shows a list of all items in your current room.\n" +
    "`/inventory`\n Shows a list of all the items in your inventory.\n" +
    "`/clothes`\n Shows a list of all the clothes you are wearing.\n" +
    "`/objects`\n Shows a list of all the objects in your current room.\n" +
    "`/players`\n Shows a list of all the players in your current room."
    )
    
help_page_four = ("**Player Commands (Page 4/6):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/exits`\n Shows a list of all the exits in your current room.\n" +
    "`/contents <object_name>`\n Shows a list of all the items in an object in your current room.\n" +
    "`/lookitem <item_name>`\n Shows details of a specific item in your current room.\n" +
    "`/lookinv <item_name>`\n Shows details of a specific item in your inventory.\n" +
    "`/lookclothes <item_name>`\n Shows details of a specific clothing item that you are currently wearing."
    )
    
help_page_five = ("**Player Commands (Page 5/6):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/lookinside <object_name> <item_name>`\n Shows details of a specific item inside an object in your current room.\n" +
    "`/lookobject <object_name>`\n Shows details of a specific object in your current room.\n" +
    "`/lookplayer <player_name>`\n Shows details of a specific player in your current room.\n" + 
    "`/lockobject <object_name> <key_name>`\n Locks an object in your current room using the specified key from your inventory.\n" +
    "`/unlockobject <object_name> <key_name>`\n Unlocks an object in your current room using the specified key from your inventory."
    )

help_page_six = ("**Player Commands (Page 6/6):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/lockexit <exit_name> <key_name>`\n Locks an exit in your current room using the specified key from your inventory.\n" +
    "`/unlockexit <exit_name> <key_name>`\n Unlocks an exit in your current room using the specified key from your inventory.\n" +
    "`/roll <max_num> [passing_roll]`\n Rolls for a number between 1 and whatever you would like. If a passing roll is specified, also states whether the roll succeeds.\n" +
    "`/time`\n Checks the current time in roleplay.\n"
    "`/chathistory`\n Gets the chat history of the last 5 minutes for the current room.\n"
    )

helpPages = [help_page_one, help_page_two, help_page_three, help_page_four, help_page_five, help_page_six]

class Help(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.currentHelpPage = 0

    @discord.ui.button(label = 'Back', style = discord.ButtonStyle.gray, emoji = "◀️", disabled = True, custom_id = 'back', row = 0)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentHelpPage > 0:
            self.currentHelpPage -= 1
        emby = discord.Embed(description=helpPages[self.currentHelpPage])
        self.children[0].disabled = self.currentHelpPage == 0
        self.children[1].disabled = self.currentHelpPage == 5
        await interaction.response.edit_message(embed=emby, view=self)

    @discord.ui.button(label = 'Next', style = discord.ButtonStyle.gray, emoji = "▶️", disabled = False, custom_id = 'next', row = 0)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentHelpPage < 5:
            self.currentHelpPage += 1
        emby = discord.Embed(description=helpPages[self.currentHelpPage])
        self.children[0].disabled = self.currentHelpPage == 0
        self.children[1].disabled = self.currentHelpPage == 5
        await interaction.response.edit_message(embed=emby, view=self)

#endregion

#region Admin Help

adminhelp1 = ("**Admin Commands (Page 1/7):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/addplayer <player_name> <player_id> [desc]`\n Connects a new player to a user.\n" +
    "`/delplayer <player_name>`\n Deletes an existing player.\n" +
    "`/addroom <room_name> <room_id> [desc]`\n Connects a new room to a channel.\n" +
    "`/delroom <room_name>`\n Deletes an existing channel.\n" +
    "`/addexit <first_room_name> <second_room_name> [is_locked] [key_name]`\n Adds an exit between two rooms that can be locked and have a key to open or close it." 
    )

adminhelp2 = ("**Admin Commands (Page 2/7):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/delexit <first_room_name> <second_room_name>`\n Deletes an existing exit.\n" +
    "`/additem <container> <container_name> <item_name> <weight> [wearable] [desc] [amount] [object_room_name]`\n Adds an item into either a room, object, player's inventory, or player's clothes.\n" +
    "`/delitem <container> <container_name> <item_name> [object_room_name]`\n Deletes an existing item.\n" +
    "`/addobject <room_name> <object_name> <is_container> [is_locked] [key_name] [storage] [desc]`\n Adds an object to a room that can be locked and have a key to open or close it.\n" +
    "`/delobject <room_name> <object_name>`\n Deletes an existing object." 
    )

adminhelp3 = ("**Admin Commands (Page 3/7):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/listplayers`\n Lists all current players in the experience.\n" +
    "`/listrooms`\n Lists all current rooms in the experience.\n" +
    "`/listexits <room_name>`\n Lists all exits in a room from anywhere.\n" +
    "`/listitems <container> <container_name> [object_room_name]`\n Lists all items in a container from anywhere.\n" +
    "`/listobjects <room_name>`\n Lists all objects in a room from anywhere." 
    )

adminhelp4 = ("**Admin Commands (Page 4/7):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/drag <player_name> <room_name>`\n Moves a player to the room you specify.\n" +
    "`/dragall <room_name>`\n Moves all players to the room you specify.\n" +
    "`/findplayer <player_name>`\n Finds what room a player is currently in and sends a link.\n" +
    "`/findroom <room_name>` \nFinds the channel for a certain room and sends a link.\n" +
    "`/pause`\n Stops all player commands from being registered." 
    )

adminhelp5 = ("**Admin Commands (Page 5/7):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/pauseplayer <player_name>`\n Stops a specific player's commands from being registered.\n" +
    "`/unpause`\n Allows all player commands to be registered once again.\n" +
    "`/unpauseplayer <player_name>`\n Allows a specific player's commands to be registered once again.\n" +
    "`/forcetake <player_name> <item_name> [amount]`\n Places a specific item into a player's inventory.\n" +
    "`/forcedrop <player_name> <item_name> [amount]`\n Drops a specific item from a player's inventory." 
    )

adminhelp6 = ("**Admin Commands (Page 6/7):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/forcewear <player_name> <container> <item_name> [amount]`\n Makes a player wear a specific clothing item.\n" +
    "`/forceundress <player_name> <container> <item_name> [amount]`\n Makes a player undress a specific clothing item.\n" +
    "`/seeitem <container> <container_name> <item_name> [object_room_name]`\n See details on a specific item from anywhere.\n" +
    "`/seeobject <room_name> <object_name>`\n See details on a specific object from anywhere, including admin details such as the key name.\n" +
    "`/seeexit <room_one_name> <room_two_name>`\n See details on a specific exit from anywhere, including admin details such as the key name." 
    )

adminhelp7 = ("**Admin Commands (Page 7/7):**\n\n" +
    "*Inputs in angle brackets (`<>`) are required. Inputs in square brackets (`[]`) are optional.*\n\n" +
    "`/editplayer <player_name> [new_name] [new_desc]`\n Edits a player's name or description.\n" +
    "`/editroom <room_name> [new_name] [new_desc]`\n Edits a room's name or description.\n" +
    "`/editexit <room_one_name> <room_two_name> [new_locked_state] [new_key]`\n Edits an exit's locked state or key name.\n" +
    "`/edititem <container> <container_name> <item_name> [object_room_name] [new_name] [new_desc] [is_wearable] [new_weight]`\n Edits an item's name, description, wearable state, or weight.\n" +
    "`/editobject <room_name> <object_name> [new_name] [new_desc] [new_container_state] [new_locked_state] [new_key] [new_storage]`\n Edits an object's name, description, container state, locked state, key name, or storage amount." 
    )

adminHelpPages = [adminhelp1, adminhelp2, adminhelp3, adminhelp4, adminhelp5, adminhelp6, adminhelp7]

class AdminHelp(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.currentHelpPage = 0

    @discord.ui.button(label = 'Back', style = discord.ButtonStyle.gray, emoji = "◀️", disabled = True, custom_id = 'back', row = 0)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentHelpPage > 0:
            self.currentHelpPage -= 1
        emby = discord.Embed(description=adminHelpPages[self.currentHelpPage])
        self.children[0].disabled = self.currentHelpPage == 0
        self.children[1].disabled = self.currentHelpPage == 6
        await interaction.response.edit_message(embed=emby, view=self)

    @discord.ui.button(label = 'Next', style = discord.ButtonStyle.gray, emoji = "▶️", disabled = False, custom_id = 'next', row = 0)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentHelpPage < 6:
            self.currentHelpPage += 1
        emby = discord.Embed(description=adminHelpPages[self.currentHelpPage])
        self.children[0].disabled = self.currentHelpPage == 0
        self.children[1].disabled = self.currentHelpPage == 6
        await interaction.response.edit_message(embed=emby, view=self)

class HelpCMD(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = "help", description = "Gives descriptions of every player command.")
    async def help(self, interaction: discord.Interaction):
        emby = discord.Embed(description=help_page_one)
        await interaction.response.send_message(embed=emby, view = Help(), ephemeral=True)

    @app_commands.command(name = "adminhelp", description = "Gives descriptions of every admin command.")
    @app_commands.default_permissions()
    async def adminhelp(self, interaction: discord.Interaction):
        emby = discord.Embed(description=adminhelp1)
        await interaction.response.send_message(embed=emby, view = AdminHelp(), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCMD(bot))
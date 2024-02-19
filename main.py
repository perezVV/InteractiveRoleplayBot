import discord
from discord import app_commands
from discord import AppCommandOptionType
from dotenv import load_dotenv
import os
import pickle

def configure():
    load_dotenv()

GUILD = discord.Object(id=int(os.getenv('guild_id')))

class Item:
    def __init__(self, name: str, desc: str = ''):
        self.name = name
        self.desc = desc
    
    def get_name(self):
        return self.name
    
    def get_desc(self):
        return self.desc

class Object:
    def __init__(self, name: str, isContainer: bool, desc: str = ''):
        self.name = name
        self.desc = desc
        self.isContainer = isContainer
        self.objItems = []

    def get_name(self):
        return self.name
    
    def get_desc(self):
        return self.desc

    def get_items(self):
        return self.objItems

    def switch_state(self):
        self.isContainer = not self.isContainer
        return

    def add_item(self, item: Item):
        self.objItems.append(item)
        return

    def del_item(self, item: Item):
        self.objItems.remove(item)
        return



class Exit:
    def __init__(self, room1: str, room2: str):
        self.room1 = room1
        self.room2 = room2

    def get_room1(self):
        return self.room1
    
    def get_room2(self):
        return self.room2

class Room:
    def __init__(self, name: str, id: int, desc: str = ''):
        self.name = name
        self.id = id
        self.roomItems = []
        self.roomObjects = []
        self.roomExits = []
        self.desc = desc

    def get_name(self):
        return self.name
    
    def get_id(self):
        return self.id
    
    def get_exits(self):
        return self.roomExits
    
    def get_items(self):
        return self.roomItems
    
    def get_objects(self):
        return self.roomObjects
    
    def get_desc(self):
        return desc

    def add_exit(self, exit: Exit):
        self.roomExits.append(exit)
        return
    
    def add_item(self, item: Item):
        self.roomItems.append(item)
        return
    
    def add_object(self, object: Object):
        self.roomObjects.append(object)
        return
    
    def edit_desc(self, desc: str):
        self.desc = desc
        return

    def del_item(self, item: Item):
        self.roomItems.remove(item)
        return
    
    def del_object(self, object: Object):
        self.roomObjects.remove(object)
        return
    
    def del_exit(self, exit: Exit):
        self.roomExits.remove(exit)
        return


class Player:
    def __init__(self, name: str, id: int, desc: str = ''):
        self.name = name
        self.id = id
        self.playerItems = []
        self.room = None
        self.desc = desc
    
    def get_name(self):
        return self.name
    
    def get_id(self):
        return self.id
    
    def get_items(self):
        return self.playerItems
    
    def get_room(self):
        return self.room
    
    def get_desc(self):
        return self.desc
    
    def add_item(self, item: Item):
        self.playerItems.append(item)
        return
    
    def set_room(self, newRoom: Room):
        self.room = newRoom
        return
    
    def edit_desc(self, desc: str):
        self.desc = desc

try:
    playerdata_in = open('playerdata.pickle', 'rb')
    playerdata = pickle.load(playerdata_in)
except:
    print('No player data found; creating player data file.')
    playerdata = {}
    playerdata_out = open('playerdata.pickle', 'wb')
    pickle.dump(playerdata, playerdata_out)
    playerdata_out.close()

try:
    roomdata_in = open('roomdata.pickle', 'rb')
    roomdata = pickle.load(roomdata_in)
except:
    print('No room data found; creating room data file.')
    roomdata = {}
    roomdata_out = open('roomdata.pickle', 'wb')
    pickle.dump(roomdata, roomdata_out)
    roomdata_out.close()

def save():
    playerdata_out = open('playerdata.pickle', 'wb')
    pickle.dump(playerdata, playerdata_out)
    playerdata_out.close()

    roomdata_out = open('roomdata.pickle', 'wb')
    pickle.dump(roomdata, roomdata_out)
    roomdata_out.close()

def simplify_string(str):
    str = str.replace(' ', '')
    str = str.lower()
    return str

def get_player_name(id):
    name = ''
    for player in playerdata.values():
        if player.get_id() == id:
            name = player.name
    return name

def get_player_from_id(id):
    for player in playerdata.values():
        if player.get_id() == id:
            return player
        
def get_player_from_name(name):
    for player in playerdata.values():
        if simplify_string(player.get_name()) == simplify_string(name):
            return player

def get_room_from_name(name):
    for room in roomdata.values():
        if simplify_string(room.get_name()) == simplify_string(name):
            return room

class Client(discord.Client):
    def __init__(self, *, intents:discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)

intents = discord.Intents.all()
client = Client(intents=intents)

@client.event
async def on_ready():
    configure()
    print(f'Logged on as {client.user}!')



# # # # # # # # # # # # # # # # # # #
#          PLAYER COMMANDS          #
# # # # # # # # # # # # # # # # # # #
    
@client.tree.command(name = "desc", description = "Get the room's description.", guild=GUILD)
async def desc(interaction: discord.Interaction):
    id = interaction.channel_id
    topic = interaction.channel.topic
    if (topic == None):
        await interaction.response.send_message("`Channel description is empty.`")
    else: 
        await interaction.response.send_message("`" + topic + "`")


@client.tree.command(name = "take", description = "Take an item from the room.", guild=GUILD)
@app_commands.describe(item_name = "The item you wish to take.")
async def take(interaction: discord.Interaction, item_name: str):
    id = interaction.user.id
    channel_id = interaction.channel_id
    player = get_player_from_id(id)
    currRoom = None

    if player == None or not player.get_name() in playerdata.keys():
        await interaction.response.send_message("You are not a valid player. Please contact the admin if you believe this is a mistake.")
        return

    for room in roomdata.values():
        if room.get_id() == channel_id:
            currRoom = room

    if currRoom is None:
        await interaction.response.send_message("You are not currently in a room. Please contact an admin if you believe this is a mistake.")
        return

    itemList = currRoom.get_items()
    
    for item in itemList:
        if simplify_string(item_name) == simplify_string(item.get_name()):
            player.add_item(item)
            currRoom.del_item(item)
            save()
            await interaction.response.send_message("`" + player.get_name() + "` picked up `" + item.get_name() + "`.")
            return

    await interaction.response.send_message("Could not find `" + item_name + "`. Please use `/items` to see a list of items in the current room.")
        
@client.tree.command(name = "items", description = "List all of the items in the current room.", guild=GUILD)
async def items(interaction: discord.Interaction):
    id = interaction.channel_id
    currRoom = None

    for room in roomdata.values():
        if room.get_id() == id:
            currRoom = room

    if currRoom is None:
        await interaction.response.send_message("You are not currently in a room. Please contact an admin if you believe this is a mistake.")
        return

    itemList = currRoom.get_items()

    if len(itemList) == 0:
        await interaction.response.send_message("No items could be found in the room.")
        return
    
    itemNames = []
    for item in itemList:
        itemNames.append("`" + item.get_name() + "`")

    allItems = ', '.join(itemNames)
    await interaction.response.send_message("Items found in `" + str(currRoom.get_name()) + "`: \n" + allItems)

@client.tree.command(name = "lookitem", description = "Get the description of a specific item in the current room.", guild=GUILD)
@app_commands.describe(item_name = "The name of the item you wish to look at.")
async def lookitem(interaction: discord.Interaction, item_name: str):
    id = interaction.channel_id
    player_id = interaction.user.id
    player = get_player_from_id(player_id)
    currRoom = None

    for room in roomdata.values():
        if room.get_id() == id:
            currRoom = room

    if currRoom is None:
        await interaction.response.send_message("You are not currently in a room. Please contact an admin if you believe this is a mistake.")
        return
    
    itemList = currRoom.get_items()

    if len(itemList) == 0:
        await interaction.response.send_message("No items could be found in the room.")
        return
    
    searchedItem = None
    for item in itemList:
        if simplify_string(item.get_name()) == simplify_string(item_name):
            searchedItem = item
    
    if searchedItem is None:
        await interaction.response.send_message("Could not find the item `" + item_name + "`. Please use `/items` to see a list of all the items in the current room.")
        return
    
    if player is not None:
        if searchedItem.get_desc() == '':
            await interaction.response.send_message("`" + player.get_name() + "` looked at the item `" + searchedItem.get_name() + "`.")
            return
        else:
            await interaction.response.send_message("`" + player.get_name() + "` looked at the item `" + searchedItem.get_name() + "`:\n" + "`" + searchedItem.get_desc() + "`")
        return
    
    await interaction.response.send_message("`" + searchedItem.get_name() + "`:\n" + "`" + searchedItem.get_desc() + "`")


@client.tree.command(name = "objects", description = "List all of the objects in the current room.", guild=GUILD)
async def objects(interaction: discord.Interaction):
    id = interaction.channel_id
    currRoom = None

    for room in roomdata.values():
        if room.get_id() == id:
            currRoom = room

    if currRoom is None:
        await interaction.response.send_message("You are not currently in a room. Please contact an admin if you believe this is a mistake.")
        return

    objList = currRoom.get_objects()

    if len(objList) == 0:
        await interaction.response.send_message("No objects could be found in the room.")
        return
    
    objNames = []
    for obj in objList:
        objNames.append("`" + obj.get_name() + "`")

    allObjs = ', '.join(objNames)
    await interaction.response.send_message("Objects found in `" + str(currRoom.get_name()) + "`: \n" + allObjs)

@client.tree.command(name = "lookobject", description = "Get the description of a specific object in the current room.", guild=GUILD)
@app_commands.describe(object_name = "The name of the object you wish to look at.")
async def lookitem(interaction: discord.Interaction, object_name: str):
    id = interaction.channel_id
    player_id = interaction.user.id
    player = get_player_from_id(player_id)
    currRoom = None

    for room in roomdata.values():
        if room.get_id() == id:
            currRoom = room

    if currRoom is None:
        await interaction.response.send_message("You are not currently in a room. Please contact an admin if you believe this is a mistake.")
        return
    
    objList = currRoom.get_objects()

    if len(objList) == 0:
        await interaction.response.send_message("No objects could be found in the room.")
        return
    
    searchedObj = None
    for obj in objList:
        if simplify_string(obj.get_name()) == simplify_string(object_name):
            searchedObj = obj
    
    if searchedObj is None:
        await interaction.response.send_message("Could not find the object `" + object_name + "`. Please use `/objects` to see a list of all the items in the current room.")
        return
    
    if player is not None:
        if searchedObj.get_desc() == '':
            await interaction.response.send_message("`" + player.get_name() + "` looked at the object `" + searchedObj.get_name() + "`.")
            return
        await interaction.response.send_message("`" + player.get_name() + "` looked at the object `" + searchedObj.get_name() + "`:\n" + "`" + searchedObj.get_desc() + "`")
        return
    
    if searchedObj.get_desc() == '':
        await interaction.response.send_message("``" + searchedObj.get_name() + "`.")
        return
    
    await interaction.response.send_message("`" + searchedObj.get_name() + "`:\n" + "`" + searchedObj.get_desc() + "`")

@client.tree.command(name = "inventory", description = "List all of the items in your inventory.")
async def inv(interaction: discord.Interaction):
    id = interaction.user.id
    player = get_player_from_id(id)

    if player == None or not player.get_name() in playerdata.keys():
        await interaction.response.send_message("You are not a valid player. Please contact the admin if you believe this is a mistake.")
        return
    
    playerItems = player.get_items()

    if len(playerItems) == 0:
            await interaction.response.send_message("No items found in `" + player.get_name() + "`'s inventory.")
            return

    itemNames = []
    for item in playerItems:
        itemNames.append("`" + item.get_name() + "`")

    allItems = ', '.join(itemNames)
    await interaction.response.send_message("Items found in `" + player.get_name() + "`'s inventory: \n" + allItems)

@client.tree.command(name = "lookinv", description = "Get the description of a specific item in your inventory.", guild=GUILD)
@app_commands.describe(item_name = "The name of the item you wish to look at.")
async def lookitem(interaction: discord.Interaction, item_name: str):
    player_id = interaction.user.id
    player = get_player_from_id(player_id)

    if player == None or not player.get_name() in playerdata.keys():
        await interaction.response.send_message("You are not a valid player. Please contact the admin if you believe this is a mistake.")
        return
    
    itemList = player.get_items()

    if len(itemList) == 0:
        await interaction.response.send_message("No items could be found in `" + player.get_name() + "`'s inventory.")
        return
    
    searchedItem = None
    for item in itemList:
        if simplify_string(item.get_name()) == simplify_string(item_name):
            searchedItem = item
    
    if searchedItem is None:
        await interaction.response.send_message("Could not find the item `" + item_name + "`. Please use `/inventory` to see a list of all the items in your inventory.")
        return
    
    if searchedItem.get_desc() == '':
        await interaction.response.send_message("`" + player.get_name() + "` looked at the item `" + searchedItem.get_name() + "` in their inventory.")
        return

    await interaction.response.send_message("`" + player.get_name() + "` looked at the item `" + searchedItem.get_name() + "` in their inventory:\n" + "`" + searchedItem.get_desc() + "`")

@client.tree.command(name = "goto", description = "Move to the room that you specify.")
@app_commands.describe(room_name = "The name of the room you wish the move to.")
async def goto(interaction: discord.Interaction, room_name: str):
    id = interaction.user.id
    channel_id = interaction.channel_id
    player = get_player_from_id(id)
    currRoom = None

    if player == None or not player.get_name() in playerdata.keys():
        await interaction.response.send_message("You are not a valid player. Please contact the admin if you believe this is a mistake.")
        return
    
    simplified_room = simplify_string(room_name)
    simplified_keys = [simplify_string(key) for key in roomdata.keys()]

    if simplified_room not in simplified_keys:
        await interaction.response.send_message("Could not find `" + room_name + "`. Did you mistype? Please use `/exits` to see the current connected rooms.")
        return
    
    room = get_room_from_name(room_name)

    if room is None:
        await interaction.response.send_message("Could not find `" + room_name + "`. The room may need to be fixed — please contact an admin.")
        return

    for newRoom in roomdata.values():
        if newRoom.get_id() == channel_id:
            currRoom = newRoom

    if currRoom is None:
            await interaction.response.send_message("You are not currently in a room. Please contact an admin if you believe this is a mistake.")
            return

    exits = currRoom.get_exits()

    if len(exits) == 0:
        await interaction.response.send_message("There are no exits in `" + str(currRoom.get_name()) + "`.")
        return

    currExit = None
    for exit in exits:
        if exit.get_room1() == currRoom.get_name():
            if simplify_string(exit.get_room2()) == simplify_string(room_name):
                currExit = exit.get_room2()
        else:
            if simplify_string(exit.get_room1()) == simplify_string(room_name):
                currExit = exit.get_room1()

    if currExit is None:
        await interaction.response.send_message("There is no exit to `" + room_name + "` from `" + str(currRoom.get_name()) + "`.")
        return

    player.set_room(room)
    save()
    
    currChannel = client.get_channel(int(currRoom.get_id()))

    channel = client.get_channel(int(room.get_id()))
    user = client.get_user(int(player.get_id()))

    if channel is None:
        await interaction.response.send_message("Could not find the channel for `" + room_name + "`. The room may need to be fixed — please contact an admin.")
    
    if currRoom is not None and currChannel is None:
        await interaction.response.send_message("Could not find the channel for `" + currRoom.get_name() + "`. The room may need to be fixed — please contact an admin.")

    if user is None:
        await interaction.response.send_message("Could not find the user <@" + player.get_id() + ">. The player may need to be fixed — please contact an admin.")

    await interaction.response.send_message("`" + player.get_name() + "` moved to `" + room.get_name() + "`.")

    if currChannel is not None:
        await channel.send("`" + player.get_name() + "` entered from `" + currRoom.get_name() + "`.")
    else:
        await channel.send("`" + player.get_name() + "` entered.")

    if currChannel is not None:
        await currChannel.set_permissions(user, read_messages = False)
    
    await channel.set_permissions(user, read_messages = True)
    

@client.tree.command(name = "exits", description = "List all locations that are connected to your current room.")
async def exits(interaction: discord.Interaction):
    id = interaction.channel_id
    currRoom = None

    for room in roomdata.values():
        if room.get_id() == id:
            currRoom = room
    
    if currRoom is None:
        await interaction.response.send_message("You are not currently in a room. Please contact an admin if you believe this is a mistake.")
        return
    
    exits = currRoom.get_exits()

    if len(exits) == 0:
        await interaction.response.send_message("No exits could be found.")
        return
    
    exitNames = []
    for exit in exits:
        currExit = ''
        if exit.get_room1() == currRoom.get_name():
            currExit = exit.get_room2()
        else:
            currExit = exit.get_room1()
        exitNames.append("`" + currExit + "`")
    
    allExits = ', '.join(exitNames)
    await interaction.response.send_message("Exits available in `" + currRoom.get_name() + "`: \n" + allExits)

@client.tree.command(name = "lookplayer", description = "Get the description of a specific player in the current room.")
@app_commands.describe(player_name = "The list of players in the current room.")
async def lookplayer(interaction: discord.Interaction, player_name: str):
    player_id = interaction.user.id
    lookingPlayer = get_player_from_id(player_id)
    
    simplified = simplify_string(player_name)
    player = None

    for p in playerdata.values():
        if simplify_string(p.get_name()) == simplified:
            player = p
    
    if player is None:
        await interaction.response.send_message("Could not find player `" + player_name + "`. Please use `/players` to see a list of all players in the current room.")
        return
    
    if lookingPlayer is None:
        await interaction.response.send_message("`" + player.get_name() + "`:\n" + "`" + player.get_desc() + "`")
        return

    if lookingPlayer is player:
        if player.get_desc() == '':
            await interaction.response.send_message("`" + lookingPlayer.get_name() + "` looked at themself.")
            return
        await interaction.response.send_message("`" + lookingPlayer.get_name() + "` looked at themself:\n" + "`" + lookingPlayer.get_desc() + "`")
        return

    if player.get_desc() == '':
            await interaction.response.send_message("`" + lookingPlayer.get_name() + "` looked at `" + player.get_name() + "`.")
            return

    await interaction.response.send_message("`" + lookingPlayer.get_name() + "` looked at `" + player.get_name() + "`:\n" + "`" + player.get_desc() + "`")
    return

# # # # # # # # # # # # # # # # #  #
#          ADMIN COMMANDS          #
# # # # # # # # # # # # # # # # #  #
        
@client.tree.command(name = "addplayer", description = "Add a new player to the experience.", guild=GUILD)
@app_commands.describe(player_name = "The new player's name.")
@app_commands.describe(player_id = "The Discord ID of the user that controls the player.")
@app_commands.describe(desc = "The description of the player you wish to add to the experience.")
async def addplayer(interaction: discord.Interaction, player_name: str, player_id: str, desc: str = ''):
    
    if player_name in playerdata.keys():
        await interaction.response.send_message("Player `" + player_name + "` already exists. Please use a different name.")
        return

    try:
        player_id = int(player_id)
    except:
        await interaction.response.send_message("A user ID must be made up entirely of integers. Please enter a valid user ID.")
        return
    
    if interaction.guild.get_member(player_id) == None:
        await interaction.response.send_message("Could not find <@" + str(player_id) + ">. Please enter a valid user ID.")
        return

    if get_player_from_id(player_id) != None:
        await interaction.response.send_message("<@" + str(player_id) + "> is already connected to the player `" + get_player_name(player_id) + "`.")
        return

    playerdata[player_name] = Player(player_name, player_id, desc)
    save()
    await interaction.response.send_message("Player `" + player_name + "` connected to <@" + str(player_id) + ">.")



@client.tree.command(name = "delplayer", description = "Remove a player from the experience.", guild=GUILD)
@app_commands.describe(player_name = "The player you wish to remove's name.")
async def delplayer(interaction: discord.Interaction, player_name: str):

    simplified_player = simplify_string(player_name)
    simplified_player_keys = {simplify_string(key): key for key in playerdata.keys()}

    if simplified_player in simplified_player_keys:
        original_key = simplified_player_keys[simplified_player]
        try:
            del playerdata[original_key]
            save()
            await interaction.response.send_message("Deleted player `" + original_key + "`.")
            return
        except:
            await interaction.response.send_message("Failed to delete `" + original_key + "`. Please contact the bot's developer.")
            return
    else:
        await interaction.response.send_message("Could not find player `" + player_name + "`. Did you mistype? Please use `/listplayers` to see all current players.")

@client.tree.command(name = "listplayers", description = "List all the current players added to the experience.", guild=GUILD)
async def listplayers(interaction: discord.Interaction):

    if len(playerdata) == 0:
        await interaction.response.send_message("There are currently no players.")
        return

    playerList = ''
    for key in playerdata:
        currPlayer = playerdata[key]
        nextPlayer = ("`", currPlayer.get_name(), ":` <@", str(currPlayer.get_id()), ">")
        nextPlayer = ''.join(nextPlayer)
        playerList = playerList + "\n" + nextPlayer

    await interaction.response.send_message(playerList)

@client.tree.command(name = "addroom", description = "Add a room to the experience.")
@app_commands.describe(room_name = "The name of the room you wish to create.")
@app_commands.describe(room_id = "The Discord ID of the channel you wish to connect the room to.")
@app_commands.describe(desc = "The description of the room you wish to add to the experience.")
async def addroom(interaction: discord.Interaction, room_name: str, room_id: str, desc: str = ''):
    
    try:
        room_id = int(room_id)
    except:
        await interaction.response.send_message("A room ID must be made up entirely of integers. Please enter a valid room ID.")
        return

    if interaction.guild.get_channel(int(room_id)) == None:
        await interaction.response.send_message("Could not find <#" + str(room_id) + ">. Did you mistype?")
        return

    for room in roomdata.values():
        if simplify_string(room_name) == simplify_string(room.get_name()):
            await interaction.response.send_message("Room name `" + room_name + "` is already in use. Please give the room a separate name.")
            return
        if room.get_id() == room_id:
            await interaction.response.send_message("The channel <#" + str(room_id) + "> is already in use. Please give the room a separate channel.")
            return

    roomdata[room_name] = Room(room_name, room_id, desc)
    save()

    await interaction.response.send_message("Room `" + room_name + "` connected to <#" + str(room_id) + ">.")

@client.tree.command(name = "delroom", description = "Remove a room from the experience.")
@app_commands.describe(room_name = "The name of the room you wish to remove.")
async def delroom(interaction: discord.Interaction, room_name: str):
    simplified_room = simplify_string(room_name)
    simplified_keys = {simplify_string(key): key for key in roomdata.keys()}
    if simplified_room in simplified_keys:
        original_key = simplified_keys[simplified_room]
        try:
            del roomdata[original_key]
            for room in roomdata.values():
                exits = room.get_exits()
                for exit in exits:
                    if exit.get_room1() == original_key or exit.get_room2() == original_key:
                        room.del_exit(exit)
            save()
            await interaction.response.send_message("Deleted room `" + original_key + "`.")
            return
        except:
            await interaction.response.send_message("Failed to delete room `" + original_key + "`. Please contact the bot's developer.")
            return
    
    else:
        await interaction.response.send_message("Could not find room `" + room_name + "`. Did you mistype? Please use `/listrooms` to see all current rooms.")


@client.tree.command(name = "listrooms", description = "List all rooms that have been added to the experience.")
async def listrooms(interaction: discord.Interaction):
    if len(roomdata) == 0:
        await interaction.response.send_message("There are currently no rooms.")
        return
    
    roomList = ''
    for key in roomdata:
        currRoom = roomdata[key]
        nextRoom = ("`", currRoom.get_name(), ":` <#", str(currRoom.get_id()), ">.")
        nextRoom = ''.join(nextRoom)
        roomList = roomList + "\n" + nextRoom
    
    await interaction.response.send_message(roomList)


@client.tree.command(name = "addexit", description = "Add a connection between two rooms.")
@app_commands.describe(first_room_name = "The first of the two rooms you wish to add a connection between.")
@app_commands.describe(second_room_name = "The second of the two rooms you wish to add a connection between.")
async def addexit(interaction: discord.Interaction, first_room_name: str, second_room_name: str):

    simplified_room_one = simplify_string(first_room_name)
    simplified_room_two = simplify_string(second_room_name)
    simplified_keys = {simplify_string(key): key for key in roomdata.keys()}

    if simplified_room_one not in simplified_keys:
        await interaction.response.send_message("Room `" + first_room_name + "` count not be found. Did you mistype? Please use `/listrooms` to see all current rooms.")
        return
    if simplified_room_two not in simplified_keys:
        await interaction.response.send_message("Room `" + second_room_name + "` count not be found. Did you mistype? Please use `/listrooms` to see all current rooms.")
        return
    
    room_one = get_room_from_name(simplified_room_one)
    room_two = get_room_from_name(simplified_room_two)
    original_room_one = simplified_keys[simplified_room_one]
    original_room_two = simplified_keys[simplified_room_two]

    exit: Exit = Exit(original_room_one, original_room_two)

    room_one.add_exit(exit)
    room_two.add_exit(exit)

    save()

    await interaction.response.send_message("Connection created between `" + original_room_one + "` and `" + original_room_two + "`.")
    


@client.tree.command(name = "drag", description = "Drag a player into a room.")
@app_commands.describe(player_name = "The name of the player that you wish to drag.")
@app_commands.describe(room_name = "The name of the room you wish to drag the player into.")
async def drag(interaction: discord.Interaction, player_name: str, room_name: str):

    simplified_player = simplify_string(player_name)
    simplified_player_keys = {simplify_string(key): key for key in playerdata.keys()}

    simplified_room = simplify_string(room_name)
    simplified_room_keys = {simplify_string(key): key for key in roomdata.keys()}

    if simplified_player not in simplified_player_keys:
        await interaction.response.send_message("Player `" + player_name + "` could not be found. Did you mistype? Please use `/listplayers` to see all current players.")
        return
    
    if simplified_room not in simplified_room_keys:
        await interaction.response.send_message("Room `" + room_name + "` could not be found. Did you mistype? Please use `/listrooms` to see all current rooms.")
        return

    player = get_player_from_name(player_name)
    prevRoom = player.get_room()
    room = get_room_from_name(room_name)

    if room is None:
        await interaction.response.send_message("Room `" + room_name + "` could not be found. Did you mistype? Please use `/listrooms` to see all current rooms.")
        return
    
    player.set_room(room)
    save()

    if prevRoom is not None:
        prevChannel = client.get_channel(int(prevRoom.get_id()))
    else:
        prevChannel = None

    channel = client.get_channel(int(room.get_id()))
    user = client.get_user(int(player.get_id()))

    if channel is None:
        await interaction.response.send_message("Could not find the channel for `" + room_name + "`. Is there an error in the ID?")
    
    if prevRoom is not None and prevChannel is None:
        await interaction.response.send_message("Could not find the channel for `" + prevRoom.get_name() + "`. Is there an error in the ID?")

    if user is None:
        await interaction.response.send_message("Could not find the user <@" + player.get_id() + ">. Is there an error in the ID?")

    await interaction.response.send_message("Dragged `" + player_name + "` to `" + room.get_name() + "`.")
    
    if prevChannel is not None:
        await prevChannel.send("`" + player.get_name() + "` was dragged to `" + room.get_name() + "`.")
        await channel.send("`" + player_name + "` entered from `" + prevRoom.get_name() + "`.")
    else:
        await channel.send("`" + player_name + "` entered.")

    if prevChannel is not None:
        await prevChannel.set_permissions(user, read_messages = False)
    
    await channel.set_permissions(user, read_messages = True)
    
    

@client.tree.command(name = "findplayer", description = "Tells which room a player is currently in.")
@app_commands.describe(player_name = "The name of the player you wish to find.")
async def findplayer(interaction: discord.Interaction, player_name: str):
    
    simplified_player = simplify_string(player_name)
    simplified_player_keys = {simplify_string(key): key for key in playerdata.keys()}

    if simplified_player not in simplified_player_keys:
        await interaction.response.send_message("Player `" + player_name + "` could not be found. Did you mistype? Please use `/listplayers` to see all current players.")
        return

    player = get_player_from_name(player_name)
    room = player.get_room()

    if room is None:
        await interaction.response.send_message("`" + player.get_name() + "` is not yet in a room.")
        return

    await interaction.response.send_message("`" + player.get_name() + "` is currently in `" + room.get_name() + "`.\nJump?: <#" + str(room.get_id()) + ">")

@client.tree.command(name = "additem", description = "Add an item into a room.", guild=GUILD)
@app_commands.describe(room_name = "The room you wish to add the item to.")
@app_commands.describe(item_name = "The name of the item you wish to add to the room.")
@app_commands.describe(desc = "The description of the item you wish to add to the room.")
async def additem(interaction: discord.Interaction, room_name: str, item_name: str, desc: str = ''):
    
    room = get_room_from_name(room_name)

    if room is None:
        await interaction.response.send_message("Room `" + room_name + "` could not be found. Did you mistype? Please use `/listrooms` to see all current rooms.")
        return
    
    item: Item = Item(item_name, desc)
    room.add_item(item)

    save()
    await interaction.response.send_message("Added `" + item_name + "` to room `" + room_name + "`.")

@client.tree.command(name = "addobject", description = "Add an object into a room.", guild=GUILD)
@app_commands.describe(room_name = "The room you wish to add the object to.")
@app_commands.describe(object_name = "The name of the object you wish to add to the room.")
@app_commands.describe(is_container = "True or false; whether or not you wish the object to be able to store items.")
@app_commands.describe(desc = "The description of the object you wish to add to the room.")
async def addobject(interaction: discord.Interaction, room_name: str, object_name: str, is_container: bool, desc: str = ''):

    room = get_room_from_name(room_name)

    if room is None:
        await interaction.response.send_message("Room `" + room_name + "` could not be found. Did you mistype? Please use `/listrooms` to see all current rooms.")
        return
    
    object: Object = Object(object_name, is_container, desc)
    room.add_object(object)

    save()
    await interaction.response.send_message("Added `" + object_name + "` to room `" + room_name + "`.")

client.run(os.getenv('token'))
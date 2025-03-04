import typing
import pickle
import configparser
import os

__all__ = ("Item", "Object", "Exit", "Room", "Player", "preferences", "playerdata", "roomdata", "save", "get_max_carry_weight", "set_max_carry_weight", "get_max_wear_weight", "set_max_wear_weight")

class Item:
    def __init__(self, name: str, weight: float, wearable: bool, desc: str = ''):
        self.name = name
        self.weight = weight
        self.wearable = wearable
        self.desc = desc
    
    def get_name(self):
        return self.name
    
    def get_desc(self):
        return self.desc
    
    def get_wearable_state(self):
        return self.wearable
    
    def get_weight(self):
        return self.weight
    
    def edit_name(self, name: str):
        self.name = name
        return
    
    def edit_desc(self, desc: str):
        self.desc = desc
        return
    
    def edit_weight(self, weight: float):
        self.weight = weight
        return
    
    def switch_wearable_state(self, wearable: bool):
        self.wearable = wearable
        return

#endregion
#region Object
class Object:
    def __init__(self, name: str, isContainer: bool, isLocked: bool, keyName: str = '', storage: int = -1, desc: str = ''):
        self.name = name
        self.desc = desc
        self.isContainer = isContainer
        self.isLocked = isLocked
        self.keyName = keyName
        self.storage = storage
        self.objItems: typing.List[Item] = []

    def get_name(self):
        return self.name
    
    def get_desc(self):
        return self.desc

    def get_items(self):
        return self.objItems

    def get_locked_state(self):
        return self.isLocked
    
    def get_container_state(self):
        return self.isContainer

    def get_key_name(self):
        return self.keyName
    
    def get_storage(self):
        return self.storage

    def switch_locked_state(self, locked: bool):
        self.isLocked = locked
        return

    def switch_container_state(self, container: bool):
        self.isContainer = container
        return

    def add_item(self, item: Item):
        self.objItems.append(item)
        return

    def edit_name(self, name: str):
        self.name = name
        return

    def edit_item(self, origItem: Item, item: Item):
        self.objItems[self.objItems.index(origItem)] = item
        return

    def edit_key_name(self, keyName: str):
        self.keyName = keyName
        return

    def edit_desc(self, desc: str):
        self.desc = desc
        return
    
    def set_storage(self, newStorageAmt: int):
        self.storage = newStorageAmt
        return

    def del_item(self, item: Item):
        self.objItems.remove(item)
        return
#endregion
#region Exit
class Exit:
    def __init__(self, room1: str, room2: str, isLocked: bool, keyName: str = ''):
        self.room1 = room1
        self.room2 = room2
        self.isLocked = isLocked
        self.keyName = keyName

    def get_room1(self):
        return self.room1
    
    def get_room2(self):
        return self.room2
    
    def get_locked_state(self):
        return self.isLocked

    def get_key_name(self):
        return self.keyName

    def edit_room1(self, newRoom1: str):
        self.room1 = newRoom1
        return
    
    def edit_room2(self, newRoom2: str):
        self.room2 = newRoom2
        return

    def edit_key_name(self, keyName: str):
        self.keyName = keyName
        return
    
    def switch_locked_state(self, isLocked: bool):
        self.isLocked = isLocked
        return
#endregion
#region Room
class Room:
    def __init__(self, name: str, id: int, desc: str = ''):
        self.name = name
        self.id = id
        self.roomItems: typing.List[Item] = []
        self.roomObjects: typing.List[Object] = []
        self.roomExits: typing.List[Exit] = []
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
        return self.desc

    def add_exit(self, exit: Exit):
        self.roomExits.append(exit)
        return
    
    def add_item(self, item: Item):
        self.roomItems.append(item)
        return
    
    def add_object(self, object: Object):
        self.roomObjects.append(object)
        return
    
    def edit_item(self, origItem: Item, item: Item):
        self.roomItems[self.roomItems.index(origItem)] = item
        return

    def edit_name(self, name: str):
        self.name = name
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
#endregion
#region Player
class Player:
    def __init__(self, name: str, id: int, desc: str = ''):
        self.name = name
        self.id = id
        self.playerItems: typing.List[Item] = []
        self.playerClothes: typing.List[Item] = []
        self.room = None
        self.paused = None
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
    
    def get_clothes(self):
        return self.playerClothes

    def get_weight(self):
        return sum(item.get_weight() for item in self.playerItems)

    def get_clothes_weight(self):
        return sum(clothes.get_weight() for clothes in self.playerClothes)
    
    def is_paused(self):
        return self.paused
    
    def pause(self):
        self.paused = True
        return
    
    def unpause(self):
        self.paused = False
        return

    def add_item(self, item: Item):
        self.playerItems.append(item)
        return
    
    def add_clothes(self, clothes: Item):
        self.playerClothes.append(clothes)

    def set_room(self, newRoom: Room):
        self.room = newRoom
        return
    
    def edit_item(self, origItem: Item, item: Item):
        self.playerItems[self.playerClothes.index(origItem)] = item
        return

    def edit_name(self, name: str):
        self.name = name
        return

    def edit_desc(self, desc: str):
        self.desc = desc
        return

    def del_item(self, item: Item):
        self.playerItems.remove(item)
        return
    
    def del_clothes(self, item: Item):
        self.playerClothes.remove(item)
        return
#endregion

class CustomUnpickle(pickle.Unpickler):
    def find_class(self, module, name):
        # silly hack to allow unpickling of classes previously defined in the main module
        if module == '__main__':
            module = 'utils.data'
        return super().find_class(module, name)
    
def save():
    with open(f'{os.environ["BASE_PATH"]}/playerdata.pickle', 'wb') as playerdata_out:
        pickle.dump(playerdata, playerdata_out)

    with open(f'{os.environ["BASE_PATH"]}/roomdata.pickle', 'wb') as roomdata_out:
        pickle.dump(roomdata, roomdata_out)

def data(file):
    try:
        with open(f"{os.environ['BASE_PATH']}/{file}", 'rb') as f:
            datafile = CustomUnpickle(f).load()
    except FileNotFoundError:
        print(f'No {file} found; creating data file.')
        datafile = {}
        with open(f"{os.environ['BASE_PATH']}/{file}", 'wb') as f:
            pickle.dump(datafile, f)
    return datafile

def load_preferences():
    config = configparser.ConfigParser()
    pref_path = f"{os.environ['BASE_PATH']}/preferences.ini"
    if not os.path.exists(pref_path):
        print(f'No preferences.ini found; creating default preferences file.')
        config['WEIGHT'] = {
            'max_carry_weight': '10',
            'max_wear_weight': '15'
        }
        with open(pref_path, 'w') as new_preferences:
            config.write(new_preferences)
    else:
        config.read(pref_path)
    return config

def save_preferences():
    with open(f"{os.environ['BASE_PATH']}/preferences.ini", 'w') as new_preferences:
        preferences.write(new_preferences)

playerdata: dict[str, Player] = data('playerdata.pickle')
roomdata: dict[str, Room] = data('roomdata.pickle')
preferences = load_preferences()

def get_max_carry_weight():
    return int(preferences['WEIGHT']['max_carry_weight'])

def set_max_carry_weight(new_max: int):
    preferences['WEIGHT']['max_carry_weight'] = str(new_max)
    save_preferences()

def get_max_wear_weight():
    return int(preferences['WEIGHT']['max_wear_weight'])

def set_max_wear_weight(new_max: int):
    preferences['WEIGHT']['max_wear_weight'] = str(new_max)
    save_preferences()
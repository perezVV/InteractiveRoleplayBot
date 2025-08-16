ITEM_MESSAGES = {
    "take": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took the item **{kwargs.get('item').get_name()}***.",
        
        "multiple": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took **{kwargs.get('amount')}** of the item **{kwargs.get('item').get_name()}***.",
        
        "not_found": lambda **kwargs:
            f"*Could not find the item **{kwargs.get('item_name')}** to take. Please use `/items` to see a list of items in the current room.*",

        "not_enough": lambda **kwargs:
            f"*Could not find **{kwargs.get('amount')}** of the item **{kwargs.get('item_name')}** to take. Please use `/items` to see a list of items in the current room.*",

        "full": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take the item **{kwargs.get('item').get_name()}**, but they could not fit it into their inventory.*",

        "full_multiple": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take **{kwargs.get('amount')}** of the item **{kwargs.get('item').get_name()}**, but they could not fit that much into their inventory.*",
    },

    "takefrom": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took the item **{kwargs.get('item').get_name()}** from the object **{kwargs.get('obj').get_name()}***.",
        
        "multiple": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took **{kwargs.get('amount')}** of the item **{kwargs.get('item').get_name()}** from the object **{kwargs.get('obj').get_name()}***.",
        
        "not_found": lambda **kwargs:
            f"*Could not find the item **{kwargs.get('item_name')}** inside of the object **{kwargs.get('obj').get_name()}** to take. Please use `/contents` to see a list of all the items in an object.*",

        "not_enough": lambda **kwargs:
            f"*Could not find **{kwargs.get('amount')}** of the item **{kwargs.get('item_name')}** inside of the object **{kwargs.get('obj').get_name()}** to take. Please use `/contents` to see a list of all the items in an object.*",

        "full": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take the item **{kwargs.get('item').get_name()}** from the object **{kwargs.get('obj').get_name()}**, but they could not fit it into their inventory.*",

        "full_multiple": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take **{kwargs.get('amount')}** of the item **{kwargs.get('item').get_name()}** from the object **{kwargs.get('obj').get_name()}**, but they could not fit that much into their inventory.*",
    },

    "wear": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** wore the item **{kwargs.get('item').get_name()}**.*",
        "not_found": lambda **kwargs:
            f"*Could not find the item **{kwargs.get('item_name')}** to wear. Please use `/inventory` to see a list of items in your inventory.*",
        "not_wearable": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to wear the item **{kwargs.get('item').get_name()}**, but it was not a piece of clothing.*",
        "full": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to wear the item **{kwargs.get('item').get_name()}**, but they were wearing too much.*",
        "heavy": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to wear the item **{kwargs.get('item').get_name()}**, but it was too heavy.*",
    },

    "wearfrom": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** wore the item **{kwargs.get('item').get_name()}** from the object **{kwargs.get('obj').get_name()}**.*",
        "not_found": lambda **kwargs:
            f"*Could not find the item **{kwargs.get('item_name')}** inside of the object **{kwargs.get('obj').get_name()}**. Please use `/contents` to see a list of all the items in an object.*",
        "not_wearable": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to wear the item **{kwargs.get('item').get_name()}** from the object **{kwargs.get('obj').get_name()}**, but it was not a piece of clothing.*",
        "full": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to wear the item **{kwargs.get('item').get_name()}** from the object **{kwargs.get('obj').get_name()}**, but they were wearing too much.*",
        "heavy": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to wear the item **{kwargs.get('item').get_name()}** from the object **{kwargs.get('obj').get_name()}**, but it was too heavy.*",
    },

    "takewear": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took and wore the item **{kwargs.get('item').get_name()}**.*",
        "not_found": lambda **kwargs:
            f"*Could not find the item **{kwargs.get('item_name')}** to take and wear. Please use `/items` to see a list of items in the current room.*",
        "not_wearable": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take and wear the item **{kwargs.get('item').get_name()}**, but it was not a piece of clothing.*",
        "full": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take and wear the item **{kwargs.get('item').get_name()}**, but they were wearing too much.*",
        "heavy": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take and wear the item **{kwargs.get('item').get_name()}**, but it was too heavy.*",
    },

    "drop": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** dropped the item **{kwargs.get('item').get_name()}**.*",
        "multiple": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** dropped **{kwargs.get('amount')}** of the item **{kwargs.get('item').get_name()}**.*",
        "not_found": lambda **kwargs:
            f"*Could not find the item **{kwargs.get('item_name')}** to drop. Please use `/inventory` to see a list of items in your inventory.*",
        "not_enough": lambda **kwargs:
            f"*Could not find **{kwargs.get('amount')}** of the item **{kwargs.get('item_name')}** to drop. Please use `/inventory` to see a list of items in your inventory.*",
    },

    "dropinto": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** dropped the item **{kwargs.get('item').get_name()}** into the object **{kwargs.get('obj').get_name()}***.",
        "multiple": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** dropped **{kwargs.get('amount')}** of the item **{kwargs.get('item').get_name()}** into the object **{kwargs.get('obj').get_name()}***.",
        "not_found": lambda **kwargs:
            f"*Could not find the item **{kwargs.get('item_name')}**. Please use `/inventory` to see a list of items in your inventory.*",
        "not_enough": lambda **kwargs:
            f"*Could not find **{kwargs.get('amount')}** of the item **{kwargs.get('item_name')}** inside of the object **{kwargs.get('obj').get_name()}**. Please use `/inventory` to see a list of items in your inventory.*",
        "full": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to drop the item **{kwargs.get('item').get_name()}** into the object **{kwargs.get('obj').get_name()}**, but there wasn't enough space.*",
        "full_multiple": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to drop **{kwargs.get('amount')}** of the item **{kwargs.get('item').get_name()}** into the object **{kwargs.get('obj').get_name()}**, but there wasn't enough space.*",
    },

    "undress": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took off the item **{kwargs.get('item').get_name()}**.*",
        "full": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take off the item **{kwargs.get('item').get_name()}**, but it couldn't fit into their inventory.*",
        "not_found": lambda **kwargs:
            f"*Could not find the item **{kwargs.get('item_name')}**. Please use `/clothes` to see the clothes you are wearing.*",
    },

    "undressroom": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took off and dropped the item **{kwargs.get('item').get_name()}**.*",
    },

    "undressinto": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took off and dropped the item **{kwargs.get('item').get_name()}** into the object **{kwargs.get('obj').get_name()}**.*",
        "not_found": lambda **kwargs:
            f"*Could not find the item **{kwargs.get('item_name')}**. Please use `/clothes` to see the clothes you are wearing.*",
        "full": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take off and drop the item **{kwargs.get('item').get_name()}** into the object **{kwargs.get('obj').get_name()}**, but there wasn't enough space.*",
    }
}

INVALID_MESSAGES = {
    "items": {
        "negative": lambda amount:
            f"***{amount}** is an invalid input; please use a positive number.*"
    }
}
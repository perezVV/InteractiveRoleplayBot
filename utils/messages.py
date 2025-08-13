ITEM_MESSAGES = {
    "take": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took the item **{kwargs.get('item').get_name()}***.",
        
        "multiple": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took **{kwargs.get('amount')}** of the item **{kwargs.get('item').get_name()}***.",
        
        "not_found": lambda **kwargs:
            f"*Could not find the item **{kwargs.get('item_name')}**. Please use `/items` to see a list of items in the current room.*",

        "not_enough": lambda **kwargs:
            f"*Could not find **{kwargs.get('amount')}** of the item **{kwargs.get('item_name')}**. Please use `/items` to see a list of items in the current room.*",

        "full": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take the item **{kwargs.get('item').get_name()}**, but they could not fit it into their inventory.*",

        "full_multiple": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take **{kwargs.get('amount')}** of the item **{kwargs.get('item').get_name()}**, but they could not fit that much into their inventory.*",
    },

    "takefrom": {
        "single": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took the item **{kwargs.get('item').get_name()}** from **{kwargs.get('obj').get_name()}***.",
        
        "multiple": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** took **{kwargs.get('amount')}** of the item **{kwargs.get('item').get_name()}** from **{kwargs.get('obj').get_name()}***.",
        
        "not_found": lambda **kwargs:
            f"*Could not find the item **{kwargs.get('item_name')}** inside of the object **{kwargs.get('obj').get_name()}**. Please use `/contents` to see a list of all the items in an object.*",

        "not_enough": lambda **kwargs:
            f"*Could not find **{kwargs.get('amount')}** of the item **{kwargs.get('item_name')}** inside of the object **{kwargs.get('obj').get_name()}**. Please use `/contents` to see a list of all the items in an object.*",

        "full": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take the item **{kwargs.get('item').get_name()}** from the object **{kwargs.get('obj').get_name()}**, but they could not fit it into their inventory.*",

        "full_multiple": lambda **kwargs:
            f"***{kwargs.get('player').get_name()}** tried to take **{kwargs.get('amount')}** of the item **{kwargs.get('item').get_name()}** from the object **{kwargs.get('obj').get_name()}**, but they could not fit that much into their inventory.*",
    }
}

INVALID_MESSAGES = {
    "items": {
        "negative": lambda amount:
            f"***{amount}** is an invalid input; please use a positive number.*"
    }
}
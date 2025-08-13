ITEM_MESSAGES = {
    "take": {
        "single": lambda player, item:
            f"***{player.get_name()}** took the item **{item.get_name()}***.",
        
        "multiple": lambda player, item, amount:
            f"***{player.get_name()}** took **{amount}** of the item **{item.get_name()}***.",
        
        "not_found": lambda item_name:
            f"*Could not find the item **{item_name}**. Please use `/items` to see a list of items in the current room.*",

        "not_enough": lambda amount, item_name:
            f"*Could not find **{amount}** of the item **{item_name}**. Please use `/items` to see a list of items in the current room.*",

        "full": lambda player, item:
            f"***{player.get_name()}** tried to take the item **{item.get_name()}**, but they could not fit it into their inventory.*",

        "full_multiple": lambda player, item, amount:
            f"***{player.get_name()}** tried to take **{amount}** of the item **{item.get_name()}**, but they could not fit that much into their inventory.*",
    }
}

INVALID_MESSAGES = {
    "items": {
        "negative": lambda amount:
            f"***{amount}** is an invalid input; please use a positive number.*"
    }
}
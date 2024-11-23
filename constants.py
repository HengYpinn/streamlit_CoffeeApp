# constants.py

# Mapping of database keys to display names
ITEM_DISPLAY_NAMES = {
    'coffee_beans': 'Coffee Beans',
    'milk': 'Milk',
    'sugar': 'Sugar',
    'cup': 'Cup',
    # Add other items if necessary
}

# Reverse mapping from display names to database keys
DISPLAY_NAME_TO_ITEM = {v: k for k, v in ITEM_DISPLAY_NAMES.items()}

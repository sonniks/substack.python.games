import json
import os
import zlib
import argparse
from cryptography.fernet import Fernet

# Default savegame structure
DEFAULT_SAVEGAME = {
    "player": {
        "position": [0, 0, 0],  # Starting position
        "health": 100,
        "inventory": []
    },
    "visited_rooms": []
}

# Direction translator
DIRECTION_MAP = {
    "NORTH": "N",
    "SOUTH": "S",
    "EAST": "E",
    "WEST": "W",
    "UP": "U",
    "DOWN": "D"
}


def load_or_create_key(key_path):
    """Load encryption key from file or create a new one if it doesn't exist."""
    if os.path.exists(key_path):
        with open(key_path, 'rb') as key_file:
            key = key_file.read()
        print(f"Using existing encryption key from '{key_path}'.")
    else:
        key = Fernet.generate_key()
        with open(key_path, 'wb') as key_file:
            key_file.write(key)
        print(f"Generated new encryption key and saved to '{key_path}'.")
    return Fernet(key)


def compress_and_encrypt(data, cipher):
    """Compress and encrypt JSON data."""
    json_string = json.dumps(data)
    compressed_data = zlib.compress(json_string.encode('utf-8'))
    encrypted_data = cipher.encrypt(compressed_data)
    return encrypted_data


def decrypt_and_decompress(encrypted_data, cipher):
    """Decrypt and decompress JSON data."""
    decrypted_data = cipher.decrypt(encrypted_data)
    decompressed_data = zlib.decompress(decrypted_data)
    return json.loads(decompressed_data.decode('utf-8'))


def load_json(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file '{file_path}': {e}")
        return None


def save_game(save_path, save_data, cipher):
    """Save game progress to a file using compression and encryption."""
    encrypted_data = compress_and_encrypt(save_data, cipher)
    with open(save_path, 'wb') as file:
        file.write(encrypted_data)
    print(f"Game saved to '{save_path}' (compressed & encrypted).")


def load_or_create_savegame(save_path, world_data, cipher):
    """Load an existing savegame or create a new one if it doesn't exist."""
    if os.path.exists(save_path):
        print(f"Loading existing savegame from '{save_path}'...")
        try:
            with open(save_path, 'rb') as file:
                encrypted_data = file.read()
            return decrypt_and_decompress(encrypted_data, cipher)
        except Exception as e:
            print(f"Error loading savegame: {e}")
            print("Creating a new savegame...")
    else:
        print("No savegame found. Creating a new one...")
    save_data = {
        "player": {
            "position": world_data["metadata"]["starting_position"],
            "health": 100,
            "inventory": []
        },
        "visited_rooms": []
    }
    save_game(save_path, save_data, cipher)  # Save new game immediately
    return save_data


def validate_world(world_data):
    """Basic validation of the world JSON structure."""
    required_keys = ["metadata", "rooms", "objects"]
    for key in required_keys:
        if key not in world_data:
            print(f"Error: Missing required key '{key}' in world JSON.")
            return False
    return True


def game_loop(world_data, save_data, cipher, save_file):
    """Main game loop to handle player input and movement."""
    while True:
        user_input = input("\nWhat do you want to do? ").strip().upper()
        # Exit game without applying health modifier
        if user_input in ["EXIT", "QUIT"]:
            print("Saving game and exiting...")
            save_game(save_file, save_data, cipher)
            break
        # Apply health modifier before processing command
        apply_health_modifier(world_data, save_data)
        if user_input == "LOOK":
            display_room_description(world_data, save_data)
        elif user_input == "INVENTORY":
            display_inventory(world_data, save_data)
        elif user_input.startswith("GO "):
            direction = user_input[3:]
            move_player(world_data, save_data, direction)
        elif user_input.startswith("TAKE "):
            object_name = user_input[5:]
            take_object(world_data, save_data, object_name)
        elif user_input.startswith("USE "):
            object_name = user_input[4:]
            use_object(world_data, save_data, object_name)
        else:
            print("Invalid command. Try 'LOOK', 'INVENTORY', 'TAKE <object>', 'USE <object>', or 'GO <direction>'.")


def display_inventory(world_data, save_data):
    """Show the player's current inventory."""
    inventory = save_data["player"]["inventory"]
    if not inventory:
        print("You are carrying nothing.")
        return
    item_names = [world_data["objects"][item]["name"] for item in inventory if item in world_data["objects"]]
    print("You are carrying: " + ", ".join(item_names))


def get_current_room(world_data, player_position):
    """Retrieve the current room based on the player's position."""
    position_key = ",".join(map(str, player_position))
    return world_data["rooms"].get(position_key, None)


def move_player(world_data, save_data, direction):
    """Attempt to move the player in the given direction, ensuring the target room exists."""
    direction = direction.upper().strip()
    direction = DIRECTION_MAP.get(direction, direction)  # Convert full word to short form if needed

    current_position = save_data["player"]["position"]
    current_room = get_current_room(world_data, current_position)

    if not current_room:
        print("Error: Current room not found!")
        return

    # Check if movement is blocked due to darkness
    if not current_room.get("light", True):
        if "torch" not in save_data["player"]["inventory"]:
            print("It's too dark to move! You need a light source.")
            return
    # Validate if direction exists
    if direction not in current_room.get("exits", {}):
        print("You can't go that way.")
        return
    # Check if the destination room actually exists before moving
    new_position_key = current_room["exits"][direction]
    if new_position_key not in world_data["rooms"]:
        print("You try to go that way, but there's nothing there.")
        return
    # Move player to new position
    new_position = list(map(int, new_position_key.split(",")))
    save_data["player"]["position"] = new_position
    print(f"You move {direction}.")
    # Check if the new room is a win room
    new_room = world_data["rooms"].get(new_position_key, {})
    if new_room.get("win_room", False):
        print("You have found the exit! YOU WIN!")
        exit()  # End the game immediately
    # Display the room description
    display_room_description(world_data, save_data)


def apply_health_modifier(world_data, save_data):
    """Adjust the player's health based on the room's health modifier and display it."""
    current_position = save_data["player"]["position"]
    current_room = get_current_room(world_data, current_position)
    if not current_room:
        print("Error: Current room not found!")
        return
    health_modifier = current_room.get("health_modifier", 0)  # Default to 0 if missing
    save_data["player"]["health"] += health_modifier  # Apply health change
    # Display current health after applying damage/healing
    print(f"Health: {save_data['player']['health']} HP")
    # Check for game over condition
    if save_data["player"]["health"] <= 0:
        print("You have run out of health. GAME OVER.")
        exit()  # End the game


def display_room_description(world_data, save_data):
    """Display the room description, marking it as visited only after first display."""
    current_position = save_data["player"]["position"]
    position_key = ",".join(map(str, current_position))
    current_room = get_current_room(world_data, current_position)
    if not current_room:
        print("Error: Room data not found!")
        return
    # Check if the room has been visited before
    if position_key in save_data["visited_rooms"]:
        print(f"You are in {current_room['description']} (visited before).")
    else:
        print(f"{current_room['description']} (first time here).")
        save_data["visited_rooms"].append(position_key)  # Mark as visited
    # Show objects in the room
    objects_in_room = [obj["name"] for obj in world_data["objects"].values() if obj["location"] == position_key]
    if objects_in_room:
        print(f"You see: {', '.join(objects_in_room)}")



def take_object(world_data, save_data, object_name):
    """Allow the player to pick up an object if it's in the room."""
    current_position = ",".join(map(str, save_data["player"]["position"]))
    for obj_id, obj in world_data["objects"].items():
        if obj["location"] == current_position and obj["name"].upper() == object_name:
            save_data["player"]["inventory"].append(obj_id)  # Add to inventory
            obj["location"] = "INVENTORY"  # Mark as taken
            print(f"You take the {obj['name']}.")
            return
    print(f"There is no {object_name} here to take.")


def use_object(world_data, save_data, object_name):
    """Allow the player to use an object from inventory."""
    for obj_id in save_data["player"]["inventory"]:
        obj = world_data["objects"].get(obj_id)
        if obj and obj["name"].upper() == object_name:
            if obj_id == "torch":
                current_position = ",".join(map(str, save_data["player"]["position"]))
                world_data["rooms"][current_position]["light"] = True  # Light up room
                print("You light the torch. The room is now illuminated.")
                return
            elif obj_id == "medicine":
                save_data["player"]["health"] = 100  # Restore health
                save_data["player"]["inventory"].remove(obj_id)  # Remove medicine after use
                print("You take the medicine and feel fully restored.")
                return
            elif obj_id == "portalkey":
                print("You activate the Portal Key... a bright light surrounds you!")
                print("YOU WIN!")
                exit()  # End the game immediately
    print(f"You don't have a {object_name} to use.")


def main():
    """Main function to load the game world and handle savegame loading."""
    parser = argparse.ArgumentParser(description="Load a text-based adventure game world.")
    parser.add_argument("world_file", help="Path to the world definition JSON file.")
    parser.add_argument("save_file", help="Path to the savegame file.")
    parser.add_argument("key_file", help="Path to the encryption key file.")

    args = parser.parse_args()

    # Load the encryption key (or create one if it doesn't exist)
    cipher = load_or_create_key(args.key_file)

    # Load the world JSON
    world_data = load_json(args.world_file)
    if not world_data or not validate_world(world_data):
        print("World file is invalid. Exiting.")
        return
    # Load or create the savegame
    save_data = load_or_create_savegame(args.save_file, world_data, cipher)
    # Show initial health
    print(f"Health: {save_data['player']['health']} HP")
    # Show initial room description
    display_room_description(world_data, save_data)
    # Start game loop
    game_loop(world_data, save_data, cipher, args.save_file)

if __name__ == "__main__":
    main()


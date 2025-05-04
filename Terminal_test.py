# Additional tests for final_destination_terminal.py

import pytest
from final_destination_terminal import (
    randomize_item_locations, evidence, keys, rooms, player, use_item, find_canonical_name
)

def test_randomize_item_locations_resets_found_status():
    # Mark all as found, then randomize and check reset
    for d in [evidence, keys]:
        for v in d.values():
            v['found'] = True
    randomize_item_locations()
    for d in [evidence, keys]:
        for v in d.values():
            assert v['found'] is False

def test_find_canonical_name_case_insensitive():
    collection = ["Brick", "boarded window", "Crate"]
    assert find_canonical_name("brick", collection) == "Brick"
    assert find_canonical_name("BOARDed WINDOW", collection) == "boarded window"
    assert find_canonical_name("crate", collection) == "Crate"
    assert find_canonical_name("notfound", collection) is None

def test_use_item_case_insensitive_inventory(monkeypatch, capsys):
    player['inventory'] = ["Brick"]
    player['location'] = "Kitchen"
    rooms["Kitchen"]["objects"] = ["boarded window"]
    use_item(["use", "bRiCk", "on", "BoArDeD", "WiNdOw"])
    out = capsys.readouterr().out
    assert "smash the heavy brick" in out

def test_use_item_case_insensitive_object(monkeypatch, capsys):
    player['inventory'] = ["Brick"]
    player['location'] = "Attic"
    rooms["Attic"]["objects"] = ["crate"]
    use_item(["use", "brick", "on", "CRATE"])
    out = capsys.readouterr().out
    assert "bring the heavy brick down hard" in out

def test_use_item_missing_inventory(monkeypatch, capsys):
    player['inventory'] = []
    player['location'] = "Kitchen"
    rooms["Kitchen"]["objects"] = ["boarded window"]
    use_item(["use", "brick", "on", "boarded", "window"])
    out = capsys.readouterr().out
    assert "don't have a brick" in out.lower()

def test_use_item_missing_object(monkeypatch, capsys):
    player['inventory'] = ["Brick"]
    player['location'] = "Kitchen"
    rooms["Kitchen"]["objects"] = []
    use_item(["use", "brick", "on", "boarded", "window"])
    out = capsys.readouterr().out
    assert "don't see a boarded window" in out.lower()

def test_use_item_wrong_room(monkeypatch, capsys):
    player['inventory'] = ["Brick"]
    player['location'] = "Living Room"
    rooms["Living Room"]["objects"] = ["fireplace"]
    use_item(["use", "brick", "on", "boarded", "window"])
    out = capsys.readouterr().out
    assert "no boarded window here" in out.lower()

def test_use_item_on_crate_when_no_evidence(monkeypatch, capsys):
    player['inventory'] = ["Brick"]
    player['location'] = "Attic"
    rooms["Attic"]["objects"] = ["crate"]
    # Remove evidence from crate
    if "Newspaper Clipping" in rooms["Attic"].get("revealed_items", []):
        rooms["Attic"]["revealed_items"].remove("Newspaper Clipping")
    evidence["Newspaper Clipping"]["location"] = "SomewhereElse"
    use_item(["use", "brick", "on", "crate"])
    out = capsys.readouterr().out
    assert "doesn't seem to be anything significant" in out

def test_use_item_invalid_command(monkeypatch, capsys):
    player['inventory'] = ["Brick"]
    player['location'] = "Kitchen"
    rooms["Kitchen"]["objects"] = ["boarded window"]
    use_item(["use", "brick"])
    out = capsys.readouterr().out
    assert "use which item on what" in out.lower()

def test_everything_passes_message():
    # This is a meta-test: if all tests pass, pytest will exit 0 and print a summary.
    # You can add a print or log here if you want a custom message.
    assert True

# Packaging for distribution:
# If all tests pass, you can package your project using setuptools.
# Create a setup.py or pyproject.toml, include your modules and dependencies,
# and run `python -m build` or `python setup.py sdist bdist_wheel`.
# See: https://packaging.python.org/en/latest/tutorials/packaging-projects/
    current_room = player['location']
    room_data = rooms[current_room]

    # Use case-insensitive lookup for inventory and objects
    item_to_use = find_case_insensitive(item_to_use_input, player['inventory'])
    target_object = find_case_insensitive(target_object_input, room_data.get('objects', []))

    if not item_to_use:
        print(f"You don't have a {item_to_use_input}.")
        player['turns_left'] -= 1
        return False

    if not target_object:
        print(f"You don't see a {target_object_input} here to use the {item_to_use_input} on.")
        player['turns_left'] -= 1
        return False

    # Now use item_to_use and target_object for all further logic, preserving original case for display.
    # ...rest of use_item logic, replacing all direct string comparisons with .lower() as needed...

# Apply the same pattern in take, examine, drop, and any other function that matches items/objects by name.# In use_item, take, and similar functions, replace all direct string comparisons like:
# if item_to_use == "Brick":
# with:
# if item_to_use.lower() == "brick":

# For inventory and object checks, use a helper to find the canonical name:
def find_case_insensitive(name, collection):
    """Return the actual key from collection matching name (case-insensitive), or None."""
    for item in collection:
        if item.lower() == name.lower():
            return item
    return None

# Example usage in use_item:
item_to_use_input = command[1]
target_object_input = " ".join(command[3:])
item_to_use = find_case_insensitive(item_to_use_input, player['inventory'])
target_object = find_case_insensitive(target_object_input, room_data.get('objects', []))

if not item_to_use:
    print(f"You don't have a {item_to_use_input}.")
    player['turns_left'] -= 1
    return False

if not target_object:
    print(f"You don't see a {target_object_input} here to use the {item_to_use_input} on.")
    player['turns_left'] -= 1
    return False

# Now use item_to_use and target_object for all further logic, preserving original case for display.

# Apply this pattern to all relevant functions: use_item, take, examine, drop, etc.def use_item(command):
    if len(command) < 4 or command[2].lower() != 'on':
        print("Use which item on what? (e.g., 'use brick on window')")
        player['turns_left'] -= 1
        return False
    item_to_use = command[1]
    target_object = " ".join(command[3:])
    current_room = player['location']
    room_data = rooms[current_room]

    # Case-insensitive inventory check
    inventory_lower = [i.lower() for i in player['inventory']]
    if item_to_use.lower() not in inventory_lower:
        print(f"You don't have a {item_to_use}.")
        player['turns_left'] -= 1
        return False

    # Case-insensitive object check
    objects_lower = [obj.lower() for obj in room_data.get('objects', [])]
    if target_object.lower() not in objects_lower:
        print(f"You don't see a {target_object} here to use the {item_to_use} on.")
        player['turns_left'] -= 1
        return False

    # Find the actual object names for mutation
    def find_actual_name(name, candidates):
        for c in candidates:
            if c.lower() == name.lower():
                return c
        return name

    item_to_use_actual = find_actual_name(item_to_use, player['inventory'])
    target_object_actual = find_actual_name(target_object, room_data.get('objects', []))

    # Now use item_to_use_actual and target_object_actual for all mutations/removals/adds
    # ... rest of your logic ...from final_destination_terminal import display_objectives, player, rooms, escape_mode

# test_final_destination_terminal.py


def test_objectives_incomplete_evidence_and_locked_rooms(monkeypatch, capsys):
    player['found_evidence'] = 1
    player['turns_left'] = 60
    rooms['Attic Entrance']['locked'] = True
    rooms['Basement Stairs']['locked'] = True
    rooms['Storage Room']['locked'] = True
    monkeypatch.setattr('final_destination_terminal.escape_mode', False)
    display_objectives()
    out = capsys.readouterr().out
    assert "Find evidence" in out
    assert "1/3 pieces" in out
    assert "Find key for" in out
    assert "Attic Entrance" in out
    assert "Basement Stairs" in out
    assert "Storage Room" in out
    assert "ESCAPE THE HOUSE" not in out

def test_objectives_all_evidence_and_unlocked(monkeypatch, capsys):
    player['found_evidence'] = 3
    player['turns_left'] = 60
    rooms['Attic Entrance']['locked'] = False
    rooms['Basement Stairs']['locked'] = False
    rooms['Storage Room']['locked'] = False
    monkeypatch.setattr('final_destination_terminal.escape_mode', False)
    display_objectives()
    out = capsys.readouterr().out
    assert "✓ Found all required evidence" in out
    assert "✓ Unlocked Attic Entrance" in out
    assert "✓ Unlocked Basement Stairs" in out
    assert "✓ Unlocked Storage Room" in out

def test_objectives_escape_mode(monkeypatch, capsys):
    player['found_evidence'] = 3
    player['turns_left'] = 10
    monkeypatch.setattr('final_destination_terminal.escape_mode', True)
    display_objectives()
    out = capsys.readouterr().out
    assert "ESCAPE THE HOUSE" in out
    assert "WARNING: Demolition imminent" in out

def test_objectives_time_warning_yellow(monkeypatch, capsys):
    player['found_evidence'] = 2
    player['turns_left'] = 25
    monkeypatch.setattr('final_destination_terminal.escape_mode', False)
    display_objectives()
    out = capsys.readouterr().out
    assert "CAUTION: Time is running out" in out

def test_objectives_time_warning_none(monkeypatch, capsys):
    player['found_evidence'] = 0
    player['turns_left'] = 50
    monkeypatch.setattr('final_destination_terminal.escape_mode', False)
    display_objectives()
    out = capsys.readouterr().out
    assert "WARNING: Demolition imminent" not in out
    assert "CAUTION: Time is running out" not in out# 1. Reserve ("Attic", "crate") for Newspaper Clipping in randomize_item_locations
def randomize_item_locations():
    global evidence, keys

    # Reset locations, containers, and found status for all items
    for item_dict in [evidence, keys]:
        for item_name, item_info in item_dict.items():
            item_info['found'] = False
            item_info['location'] = None
            item_info['container'] = None

    # Identify all possible container slots
    all_container_slots = []
    for room_name, room_data in rooms.items():
        for container_obj in room_data.get('possible_containers', []):
            if container_obj in room_data.get('objects', []):
                all_container_slots.append((room_name, container_obj))

    # Reserve ("Attic", "crate") for Newspaper Clipping
    reserved_slot = ("Attic", "crate")
    if reserved_slot in all_container_slots:
        all_container_slots.remove(reserved_slot)
    evidence["Newspaper Clipping"]['location'] = "Attic"
    evidence["Newspaper Clipping"]['container'] = "crate"

    key_names = list(keys.keys())
    placeable_evidence_names = [
        e for e in evidence.keys()
        if e not in ("Newspaper Clipping", "Brick")
    ]

    num_slots_available = len(all_container_slots)
    num_keys_to_place = len(key_names)
    if num_keys_to_place > num_slots_available:
        raise ValueError(f"Not enough container slots ({num_slots_available}) to place all keys ({num_keys_to_place}). Check room definitions.")

    num_evidence_slots = num_slots_available - num_keys_to_place
    num_evidence_to_select = min(len(placeable_evidence_names), num_evidence_slots)
    selected_evidence = random.sample(placeable_evidence_names, num_evidence_to_select)
    items_to_place = key_names + selected_evidence
    random.shuffle(all_container_slots)

    used_slots = set()
    for item_name in items_to_place:
        if not all_container_slots:
            break
        room_name, container_name = all_container_slots.pop()
        slot = (room_name, container_name)
        if slot in used_slots:
            continue
        used_slots.add(slot)
        if item_name in keys:
            keys[item_name]['location'] = room_name
            keys[item_name]['container'] = container_name
        elif item_name in evidence:
            evidence[item_name]['location'] = room_name
            evidence[item_name]['container'] = container_name

    # Place Basement Key in Living Room fireplace
    slot = ("Living Room", "fireplace")
    keys["Basement Key"]['location'] = "Living Room"
    keys["Basement Key"]['container'] = "fireplace"

# 2. Case-insensitive inventory and object checks in use_item
def use_item(command):
    if len(command) < 4 or command[2].lower() != 'on':
        print("Use which item on what? (e.g., 'use brick on window')")
        player['turns_left'] -= 1
        return False
    item_to_use = command[1]
    target_object = " ".join(command[3:])
    current_room = player['location']
    room_data = rooms[current_room]

    # Case-insensitive inventory check
    inventory_lower = [i.lower() for i in player['inventory']]
    if item_to_use.lower() not in inventory_lower:
        print(f"You don't have a {item_to_use}.")
        player['turns_left'] -= 1
        return False

    # Case-insensitive object check
    objects_lower = [obj.lower() for obj in room_data.get('objects', [])]
    if target_object.lower() not in objects_lower:
        print(f"You don't see a {target_object} here to use the {item_to_use} on.")
        player['turns_left'] -= 1
        return False

    # Use Brick on Boarded Window (case-insensitive)
    if item_to_use.lower() == "brick" and target_object.lower() == "boarded window":
        if current_room == "Kitchen":
            print("You smash the heavy brick against the boarded-up window.")
            print("With a splintering crack, the boards break, revealing the outside... but also dislodging a loose gas pipe fitting near the window frame.")
            print(f"{COLOR_RED}Gas begins to hiss loudly into the room!{COLOR_RESET}")
            # Remove "boarded window", add "broken window"
            for idx, obj in enumerate(room_data['objects']):
                if obj.lower() == "boarded window":
                    room_data['objects'][idx] = "broken window"
                    break
            else:
                if "broken window" not in room_data['objects']:
                    room_data['objects'].append("broken window")
            # Add hazard
            room_data['hazard'] = "gas leak"
            room_data['hazard_info'] = {
                "description": "The room is filling with gas from a broken pipe!",
                "death_message": "A spark ignites the gas, causing a massive explosion!",
                "trigger_chance": 0.2
            }
            room_data['hazard_description'] = room_data['hazard_info']['description']
            room_data['hazard_death'] = room_data['hazard_info']['death_message']
            room_data['hazard_chance'] = room_data['hazard_info']['trigger_chance']
            player['turns_left'] -= 1
            return False
        else:
            print("There's no boarded window here to use the brick on.")
            player['turns_left'] -= 1
            return False

    # Use Brick on Crate (case-insensitive)
    if item_to_use.lower() == "brick" and target_object.lower() == "crate":
        if current_room == "Attic":
            print("You bring the heavy brick down hard on the wooden crate.")
            # Remove "crate", add "broken crate"
            for idx, obj in enumerate(room_data['objects']):
                if obj.lower() == "crate":
                    room_data['objects'][idx] = "broken crate"
                    break
            else:
                if "broken crate" not in room_data['objects']:
                    room_data['objects'].append("broken crate")
            # Reveal Newspaper Clipping if present
            newspaper_name = "Newspaper Clipping"
            if newspaper_name in evidence and \
               evidence[newspaper_name].get('location') == current_room and \
               evidence[newspaper_name].get('container') == "crate" and \
               newspaper_name not in room_data.get('revealed_items', []):
                print("The wood splinters and breaks apart. Pinned inside, you see a Newspaper Clipping!")
                room_data.setdefault('revealed_items', []).append(newspaper_name)
            else:
                print("The crate splinters, but there doesn't seem to be anything significant hidden inside its remains.")
            player['turns_left'] -= 1
            return False
        else:
            print("There's no crate here to use the brick on.")
            player['turns_left'] -= 1
            return False

    # ...rest of use_item logic unchanged...
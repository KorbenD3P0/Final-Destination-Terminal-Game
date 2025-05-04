import random
import types
import sys
from final_destination_terminal import randomize_item_locations, evidence, keys, rooms
import final_destination_terminal as game

def test_keys_have_valid_locations_and_containers(monkeypatch):
    # Patch random.sample and random.shuffle for determinism
    monkeypatch.setattr(random, "sample", lambda seq, n: list(seq)[:n])
    monkeypatch.setattr(random, "shuffle", lambda x: None)
    randomize_item_locations()
    for k, v in keys.items():
        assert v['location'] is not None, f"Key {k} has no location"
        assert v['container'] is not None, f"Key {k} has no container"
        assert v['location'] in rooms, f"Key {k} location {v['location']} not a room"
        assert v['container'] in rooms[v['location']].get('objects', []), f"Key {k} container {v['container']} not in room objects"

def test_newspaper_clipping_in_attic_crate(monkeypatch):
    monkeypatch.setattr(random, "sample", lambda seq, n: list(seq)[:n])
    monkeypatch.setattr(random, "shuffle", lambda x: None)
    randomize_item_locations()
    clipping = evidence.get("Newspaper Clipping")
    assert clipping is not None
    assert clipping['location'] == "Attic"
    assert clipping['container'] == "crate"

def test_basement_key_in_living_room_fireplace(monkeypatch):
    monkeypatch.setattr(random, "sample", lambda seq, n: list(seq)[:n])
    monkeypatch.setattr(random, "shuffle", lambda x: None)
    randomize_item_locations()
    bkey = keys.get("Basement Key")
    assert bkey is not None
    assert bkey['location'] == "Living Room"
    assert bkey['container'] == "fireplace"

def test_no_duplicate_item_slots(monkeypatch):
    monkeypatch.setattr(random, "sample", lambda seq, n: list(seq)[:n])
    monkeypatch.setattr(random, "shuffle", lambda x: None)
    randomize_item_locations()
    slots = set()
    for k, v in keys.items():
        slot = (v['location'], v['container'])
        assert slot not in slots, f"Duplicate slot {slot}"
        slots.add(slot)
    for e, v in evidence.items():
        if v.get('location') and v.get('container'):
            slot = (v['location'], v['container'])
            assert slot not in slots, f"Duplicate slot {slot}"
            slots.add(slot)

def test_raises_if_not_enough_slots(monkeypatch):
    orig_rooms = {k: v.copy() for k, v in game.rooms.items()}
    for r in game.rooms.values():
        r['possible_containers'] = []
        r['objects'] = []
    try:
        try:
            game.randomize_item_locations()
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
    finally:
        for k in game.rooms:
            game.rooms[k].update(orig_rooms[k])

import random
import types
from final_destination_terminal import randomize_item_locations, keys, evidence, rooms
import final_destination_terminal as game

def test_randomize_item_locations_assigns_keys_and_evidence():
    # Save original state
    orig_keys = {k: v.copy() for k, v in keys.items()}
    orig_evidence = {k: v.copy() for k, v in evidence.items()}
    orig_rooms = {k: v.copy() for k, v in rooms.items()}

    # Patch random.sample and random.shuffle for determinism
    orig_sample = random.sample
    orig_shuffle = random.shuffle
    random.sample = lambda seq, n: list(seq)[:n]
    random.shuffle = lambda x: None

    try:
        randomize_item_locations()
        # All keys must have location and container set
        for k, v in keys.items():
            assert v['location'] is not None, f"Key {k} has no location"
            assert v['container'] is not None, f"Key {k} has no container"
            assert v['location'] in rooms, f"Key {k} location {v['location']} not a room"
            assert v['container'] in rooms[v['location']].get('objects', []), f"Key {k} container {v['container']} not in room objects"

        # All selected evidence (except fixed) must have location/container set or be excluded
        for e, v in evidence.items():
            if e not in ("Newspaper Clipping", "Brick"):
                if v['location'] is not None:
                    assert v['container'] is not None
                    assert v['location'] in rooms
                    assert v['container'] in rooms[v['location']].get('objects', [])

    finally:
        # Restore
        random.sample = orig_sample
        random.shuffle = orig_shuffle
        for k in keys:
            keys[k].update(orig_keys[k])
        for k in evidence:
            evidence[k].update(orig_evidence[k])
        for k in rooms:
            rooms[k].update(orig_rooms[k])

def test_newspaper_clipping_in_attic_crate():
    randomize_item_locations()
    clipping = evidence.get("Newspaper Clipping")
    assert clipping is not None
    assert clipping['location'] == "Attic"
    assert clipping['container'] == "crate"

def test_basement_key_in_living_room_fireplace():
    randomize_item_locations()
    bkey = keys.get("Basement Key")
    assert bkey is not None
    assert bkey['location'] == "Living Room"
    assert bkey['container'] == "fireplace"

def test_no_duplicate_item_slots():
    # Patch random.sample and random.shuffle for determinism
    orig_sample = random.sample
    orig_shuffle = random.shuffle
    random.sample = lambda seq, n: list(seq)[:n]
    random.shuffle = lambda x: None

    try:
        randomize_item_locations()
        slots = set()
        for k, v in keys.items():
            slots.add((v['location'], v['container']))
        for e, v in evidence.items():
            if v.get('location') and v.get('container'):
                slot = (v['location'], v['container'])
                assert slot not in slots, f"Duplicate slot {slot}"
                slots.add(slot)
    finally:
        random.sample = orig_sample
        random.shuffle = orig_shuffle

def test_raises_if_not_enough_slots(monkeypatch):
    # Patch rooms to have no containers
    orig_rooms = {k: v.copy() for k, v in game.rooms.items()}
    for r in game.rooms.values():
        r['possible_containers'] = []
        r['objects'] = []
    try:
        try:
            game.randomize_item_locations()
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
    finally:
        for k in game.rooms:
            game.rooms[k].update(orig_rooms[k])

import final_destination_terminal as game
import random

# test_final_destination_terminal.py


def setup_kitchen_with_brick():
    # Minimal setup for Kitchen with Brick in inventory and boarded window present
    game.player = {
        "location": "Kitchen",
        "inventory": ["Brick"],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    game.rooms["Kitchen"]["objects"] = ["sink", "broken plates", "boarded window"]
    # Remove any previous hazard
    for k in ["hazard", "hazard_info", "hazard_description", "hazard_death", "hazard_chance"]:
        game.rooms["Kitchen"].pop(k, None)

def setup_attic_with_brick_and_crate():
    game.player = {
        "location": "Attic",
        "inventory": ["Brick"],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    game.rooms["Attic"]["objects"] = ["crate"]
    game.rooms["Attic"]["revealed_items"] = []
    # Place evidence in crate
    game.evidence["Newspaper Clipping"]["location"] = "Attic"
    game.evidence["Newspaper Clipping"]["container"] = "crate"
    game.evidence["Newspaper Clipping"]["found"] = False

def setup_kitchen_with_tools():
    game.player = {
        "location": "Kitchen",
        "inventory": ["rusty tools"],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    game.rooms["Kitchen"]["objects"] = ["sink", "broken plates", "boarded window"]

def setup_master_bedroom_with_chains():
    game.player = {
        "location": "Master Bedroom",
        "inventory": ["chains"],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    game.rooms["Master Bedroom"]["objects"] = ["bed", "nightstand", "ceiling fan with chains"]

def test_use_brick_on_boarded_window_creates_gas_leak():
    setup_kitchen_with_brick()
    result = game.use_item(["use", "Brick", "on", "boarded window"])
    assert "broken window" in game.rooms["Kitchen"]["objects"], "Broken window not added"
    assert "boarded window" not in game.rooms["Kitchen"]["objects"], "Boarded window not removed"
    assert game.rooms["Kitchen"]["hazard"] == "gas leak", "Gas leak hazard not created"
    assert not result, "Should not die immediately"

def test_use_brick_on_crate_reveals_evidence():
    setup_attic_with_brick_and_crate()
    result = game.use_item(["use", "Brick", "on", "crate"])
    assert "broken crate" in game.rooms["Attic"]["objects"], "Broken crate not added"
    assert "crate" not in game.rooms["Attic"]["objects"], "Crate not removed"
    assert "Newspaper Clipping" in game.rooms["Attic"]["revealed_items"], "Evidence not revealed"
    assert not result, "Should not die"

def test_use_tools_on_boarded_window_removes_board():
    setup_kitchen_with_tools()
    result = game.use_item(["use", "rusty tools", "on", "boarded window"])
    assert "broken window" in game.rooms["Kitchen"]["objects"], "Broken window not added"
    assert "boarded window" not in game.rooms["Kitchen"]["objects"], "Boarded window not removed"
    assert not result, "Should not die"

def test_use_chains_on_ceiling_fan_runs():
    setup_master_bedroom_with_chains()
    # Patch random.choice to always return "light" for deterministic output
    orig_choice = random.choice
    random.choice = lambda x: "light"
    result = game.use_item(["use", "chains", "on", "ceiling fan with chains"])
    random.choice = orig_choice
    assert not result, "Should not die"
    # No state change to assert, just ensure no crash

def test_use_item_not_in_inventory():
    setup_kitchen_with_brick()
    game.player["inventory"] = []
    result = game.use_item(["use", "Brick", "on", "boarded window"])
    assert not result, "Should not die"
    assert "broken window" not in game.rooms["Kitchen"]["objects"], "Should not change room state"

def test_use_item_on_nonexistent_target():
    setup_kitchen_with_brick()
    result = game.use_item(["use", "Brick", "on", "nonexistent object"])
    assert not result, "Should not die"
    assert "broken window" not in game.rooms["Kitchen"]["objects"], "Should not change room state"

def test_use_item_case_insensitivity():
    setup_kitchen_with_brick()
    result = game.use_item(["use", "brick", "on", "BOARDED WINDOW"])
    assert "broken window" in game.rooms["Kitchen"]["objects"], "Case-insensitive match failed"
    assert not result, "Should not die"

if __name__ == "__main__":
    test_use_brick_on_boarded_window_creates_gas_leak()
    test_use_brick_on_crate_reveals_evidence()
    test_use_tools_on_boarded_window_removes_board()
    test_use_chains_on_ceiling_fan_runs()
    test_use_item_not_in_inventory()
    test_use_item_on_nonexistent_target()
    test_use_item_case_insensitivity()
    print("All use_item tests passed!")

import final_destination_terminal as game
from unittest.mock import patch
import random

def test_examine_basic_object():
    """Test examining a basic object in the room."""
    print("Testing basic object examination...")
    
    # Setup test environment
    game.player = {
        "location": "Living Room",
        "inventory": [],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    
    # Make sure the fireplace is in the room
    if "fireplace" not in game.rooms["Living Room"]["objects"]:
        game.rooms["Living Room"]["objects"].append("fireplace")
    
    initial_turns = game.player["turns_left"]
    
    # Test examining the fireplace
    print("- Examining fireplace...")
    result = game.examine(["examine", "fireplace"])
    
    # Check results
    turns_decreased = game.player["turns_left"] < initial_turns
    print(f"  Death occurred: {result}")
    print(f"  Turns decreased: {turns_decreased}")
    
    assert not result, "Examining a normal object should not cause death"
    assert turns_decreased, "Turn should be decremented when examining an object"

def test_examine_hazardous_object():
    """Test examining a hazardous object."""
    print("Testing hazardous object examination...")
    
    # Setup test environment
    game.player = {
        "location": "Kitchen",
        "inventory": [],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    
    # Add hazard to kitchen
    game.rooms["Kitchen"]["hazard"] = "faulty wiring"
    game.rooms["Kitchen"]["hazard_chance"] = 0.0  # Set to 0 to prevent random death during testing
    game.rooms["Kitchen"]["hazard_description"] = "Exposed wires crackle near the sink."
    game.rooms["Kitchen"]["hazard_death"] = "A spark ignites, electrocuting you!"
    
    # Make sure sink is in the objects list
    if "sink" not in game.rooms["Kitchen"]["objects"]:
        game.rooms["Kitchen"]["objects"].append("sink")
    
    initial_turns = game.player["turns_left"]
    
    # Test examining the sink with patched random to ensure no death
    print("- Examining sink with hazard...")
    with patch('random.random', return_value=0.9):  # Return value > hazard_chance
        result = game.examine(["examine", "sink"])
    
    # Check results
    hazard_detected = game.rooms["Kitchen"].get("hazard") == "faulty wiring"
    turns_decreased = game.player["turns_left"] < initial_turns
    
    print(f"  Hazard detected: {hazard_detected}")
    print(f"  Death occurred: {result}")
    print(f"  Turns decreased: {turns_decreased}")
    
    assert hazard_detected, "Kitchen should have faulty wiring hazard"
    assert not result, "Examining sink with patched random should not cause death"
    assert turns_decreased, "Turn should be decremented"

def test_examine_fatal_hazard():
    """Test examining a hazardous object with fatal outcome."""
    print("Testing fatal hazard examination...")
    
    # Setup test environment
    game.player = {
        "location": "Kitchen",
        "inventory": [],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    
    # Add hazard to kitchen with high chance
    game.rooms["Kitchen"]["hazard"] = "faulty wiring"
    game.rooms["Kitchen"]["hazard_chance"] = 1.0  # Guaranteed to trigger hazard
    game.rooms["Kitchen"]["hazard_description"] = "Exposed wires crackle near the sink."
    game.rooms["Kitchen"]["hazard_death"] = "A spark ignites, electrocuting you!"
    
    # Make sure sink is in the objects list
    if "sink" not in game.rooms["Kitchen"]["objects"]:
        game.rooms["Kitchen"]["objects"].append("sink")
    
    # Test examining the sink with guaranteed death
    print("- Examining sink with fatal hazard...")
    result = game.examine(["examine", "sink"])
    
    # Check results
    print(f"  Death occurred: {result}")
    
    assert result, "Examining sink with hazard_chance = 1.0 should cause death"

def test_examine_special_interaction():
    """Test examining an object with special interactions."""
    print("Testing special object interaction...")
    
    # Setup test environment and initialize interaction counter
    game.sink_interactions = 0
    game.player = {
        "location": "Kitchen",
        "inventory": [],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    
    # Make sure sink is in the objects list
    if "sink" not in game.rooms["Kitchen"]["objects"]:
        game.rooms["Kitchen"]["objects"].append("sink")
    
    # Remove any hazards to test just interaction
    if "hazard" in game.rooms["Kitchen"]:
        del game.rooms["Kitchen"]["hazard"]
    
    # Test examining the sink multiple times
    print("- Examining sink (first time)...")
    result1 = game.examine(["examine", "sink"])
    first_interaction = game.sink_interactions
    
    print("- Examining sink (second time)...")
    result2 = game.examine(["examine", "sink"])
    second_interaction = game.sink_interactions
    
    # Check results
    print(f"  Sink interaction counter after first: {first_interaction}")
    print(f"  Sink interaction counter after second: {second_interaction}")
    print(f"  Deaths occurred: {result1 or result2}")
    
    assert first_interaction == 1, "Sink interaction counter should be 1 after first examination"
    assert second_interaction == 2, "Sink interaction counter should be 2 after second examination"
    assert not (result1 or result2), "Standard sink examinations should not cause death"

def test_examine_revealed_evidence():
    """Test examining revealed evidence."""
    print("Testing examination of revealed evidence...")
    
    # Setup test environment
    game.player = {
        "location": "Attic",
        "inventory": [],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    
    # Ensure Newspaper Clipping is properly set up
    game.evidence["Newspaper Clipping"]["location"] = "Attic"
    game.evidence["Newspaper Clipping"]["found"] = False
    
    # Add to revealed items in room
    if "revealed_items" not in game.rooms["Attic"]:
        game.rooms["Attic"]["revealed_items"] = []
    
    if "Newspaper Clipping" not in game.rooms["Attic"]["revealed_items"]:
        game.rooms["Attic"]["revealed_items"].append("Newspaper Clipping")
    
    initial_turns = game.player["turns_left"]
    
    # Test examining revealed evidence
    print("- Examining revealed Newspaper Clipping...")
    result = game.examine(["examine", "Newspaper Clipping"])
    
    # Check results
    turns_decreased = game.player["turns_left"] < initial_turns
    
    print(f"  Death occurred: {result}")
    print(f"  Turns decreased: {turns_decreased}")
    
    assert not result, "Examining revealed evidence should not cause death"
    assert turns_decreased, "Turn should be decremented when examining evidence"

def test_examine_nonexistent_object():
    """Test examining an object that doesn't exist."""
    print("Testing nonexistent object examination...")
    
    # Setup test environment
    game.player = {
        "location": "Foyer",
        "inventory": [],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    
    initial_turns = game.player["turns_left"]
    
    # Test examining a nonexistent object
    print("- Examining nonexistent object...")
    result = game.examine(["examine", "unicorn"])
    
    # Check results
    turns_decreased = game.player["turns_left"] < initial_turns
    print(f"  Death occurred: {result}")
    print(f"  Turns decreased: {turns_decreased}")
    
    assert not result, "Examining a nonexistent object should not cause death"
    assert turns_decreased, "Turn should be decremented even for nonexistent objects"

def test_examine_with_no_target():
    """Test the examine command with no specified object."""
    print("Testing examine with no target...")
    
    # Setup test environment
    game.player = {
        "location": "Foyer",
        "inventory": [],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    
    initial_turns = game.player["turns_left"]
    
    # Test examining without specifying an object
    print("- Running examine with no target...")
    result = game.examine(["examine"])
    
    # Check results
    turns_decreased = game.player["turns_left"] < initial_turns
    print(f"  Death occurred: {result}")
    print(f"  Turns decreased: {turns_decreased}")
    
    assert not result, "Examining with no target should not cause death"
    
def test_examine_case_sensitivity():
    """Test if the examine function handles case sensitivity properly."""
    print("Testing case sensitivity in examine...")
    
    # Setup test environment
    game.player = {
        "location": "Living Room", 
        "inventory": [],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    
    # Make sure Brick is in the room with capital B
    if "Brick" not in game.rooms["Living Room"]["objects"]:
        game.rooms["Living Room"]["objects"].append("Brick")
    
    # Test examining with lowercase
    print("- Examining 'brick' (lowercase)...")
    result_lower = game.examine(["examine", "brick"])
    
    # Test examining with proper case
    print("- Examining 'Brick' (proper case)...")
    result_proper = game.examine(["examine", "Brick"])
    
    # Check results
    print(f"  Death occurred (lowercase): {result_lower}")
    print(f"  Death occurred (proper case): {result_proper}")
    
    assert not result_lower and not result_proper, "Neither examination should cause death"
    # Note: The actual content of the response isn't easily testable without mocking print,
    # but a successful case-insensitive search would handle both cases the same way

if __name__ == "__main__":
    # Run all tests
    print("\nRunning examine function tests...\n")
    test_examine_basic_object()
    print("\n" + "-"*50 + "\n")
    test_examine_hazardous_object()
    print("\n" + "-"*50 + "\n")
    test_examine_fatal_hazard()
    print("\n" + "-"*50 + "\n")
    test_examine_special_interaction()
    print("\n" + "-"*50 + "\n")
    test_examine_revealed_evidence()
    print("\n" + "-"*50 + "\n")
    test_examine_nonexistent_object()
    print("\n" + "-"*50 + "\n")
    test_examine_with_no_target()
    print("\n" + "-"*50 + "\n")
    test_examine_case_sensitivity()
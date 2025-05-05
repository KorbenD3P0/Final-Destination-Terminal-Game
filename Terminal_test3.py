import pytest
from final_destination_terminal import trigger_chain_reaction, rooms

def test_heavy_object_and_weak_floorboards_fatal(capsys):
    # Setup: Room with weak floorboards hazard
    room = "TestRoom_WeakFloor"
    rooms[room] = {
        "hazard": "weak floorboards",
        "hazard_info": {},
    }
    # Act: Trigger with heavy_object
    result = trigger_chain_reaction(room, "heavy_object")
    out = capsys.readouterr().out
    # Assert: Fatal, correct message
    assert result is True
    assert "floorboards" in out.lower()
    assert ("splinter" in out.lower() or "give way" in out.lower())

def test_heavy_object_and_non_weak_floorboards(capsys):
    # Setup: Room with a different hazard
    room = "TestRoom_NotWeak"
    rooms[room] = {
        "hazard": "unstable shelf",
        "hazard_info": {},
    }
    # Act: Trigger with heavy_object
    result = trigger_chain_reaction(room, "heavy_object")
    out = capsys.readouterr().out
    # Assert: Not fatal, no floorboard message
    assert result is False
    assert "floorboards" not in out.lower()
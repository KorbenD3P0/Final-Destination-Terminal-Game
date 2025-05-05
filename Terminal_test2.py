import pytest
from final_destination_terminal import trigger_chain_reaction, rooms

# test_final_destination_terminal.py


@pytest.fixture(autouse=True)
def patch_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)

def test_gas_leak_and_faulty_wiring_fatal(capsys):
    room = "TestRoom1"
    rooms[room] = {
        "hazard": "faulty wiring",
        "hazard_info": {},
    }
    result = trigger_chain_reaction(room, "gas_leak")
    out = capsys.readouterr().out
    assert result is True
    assert "BOOM" in out or "explodes" in out

def test_water_spill_and_faulty_wiring_fatal(capsys):
    room = "TestRoom2"
    rooms[room] = {
        "hazard": "faulty wiring",
        "hazard_info": {},
    }
    result = trigger_chain_reaction(room, "water_spill")
    out = capsys.readouterr().out
    assert result is True
    assert "electric current" in out or "surges" in out

def test_heavy_object_and_weak_floorboards_fatal(capsys):
    room = "TestRoom3"
    rooms[room] = {
        "hazard": "weak floorboards",
        "hazard_info": {},
    }
    result = trigger_chain_reaction(room, "heavy_object")
    out = capsys.readouterr().out
    assert result is True
    assert "floorboards" in out and ("splinter" in out or "give way" in out)

def test_no_chain_reaction_returns_false(capsys):
    room = "TestRoom4"
    rooms[room] = {
        "hazard": "unstable shelf",
        "hazard_info": {},
    }
    result = trigger_chain_reaction(room, "gas_leak")
    out = capsys.readouterr().out
    assert result is False
    assert "BOOM" not in out

def test_invalid_room_returns_false(capsys):
    result = trigger_chain_reaction("NonexistentRoom", "gas_leak")
    out = capsys.readouterr().out
    assert result is False
    assert "Error during chain reaction" in out
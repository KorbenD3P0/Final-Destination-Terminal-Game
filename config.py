"""
Configuration settings for Final Destination Terminal
"""

# Game parameters
REQUIRED_EVIDENCE = 3
STARTING_TURNS = 60
ESCAPE_MODE_INVENTORY_THRESHOLD = 5  # Max items to safely escape with

# Room generation
MIN_HAZARDS = 1
MAX_HAZARDS = 3

# Difficulty settings
DIFFICULTY = "normal"  # Options: easy, normal, hard

# Color settings (ANSI escape codes)
COLORS = {
    "reset": "\033[0m",
    "yellow": "\033[93m",
    "cyan": "\033[96m", 
    "red": "\033[91m",
    "green": "\033[92m",
    "magenta": "\033[95m"
}

# Modify game parameters based on difficulty
if DIFFICULTY == "easy":
    REQUIRED_EVIDENCE = 2
    STARTING_TURNS = 80
    ESCAPE_MODE_INVENTORY_THRESHOLD = 7
elif DIFFICULTY == "hard":
    REQUIRED_EVIDENCE = 4
    STARTING_TURNS = 45
    ESCAPE_MODE_INVENTORY_THRESHOLD = 3
import textwrap
import os
import random
import sys
import time
from shutil import get_terminal_size
from config import *

# Enable ANSI colors on Windows
if os.name == 'nt':
    os.system('color')

# ANSI escape codes for colors
COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m" # Room Name, Objects, Evidence, Keys, Important Items
COLOR_CYAN = "\033[96m"   # Exits, Actions
COLOR_RED = "\033[91m"     # Warnings, Locked status, Hazards, Death
COLOR_GREEN = "\033[92m"   # Success, Unlocked status
COLOR_MAGENTA = "\033[95m" # Special interactions, Hints

REQUIRED_EVIDENCE = 3
ESCAPE_MODE_INVENTORY_THRESHOLD = 5 # Example: More than 5 items triggers porch collapse

def find_canonical_name(name, collection):
    """Return the canonical name from a collection (list or dict) matching name case-insensitively, or None."""
    name_lower = name.lower()
    for item in collection:
        if item.lower() == name_lower:
            return item
    return None

def get_terminal_width():
    try:
        return get_terminal_size().columns
    except OSError:
        return 80 # Default width if terminal size cannot be determined

# Add this helper function for clearer messaging
def print_danger_level(level, message):
    """Prints a message with appropriate color based on danger level"""
    if level == "low":
        print(f"{COLOR_YELLOW}{message}{COLOR_RESET}")
    elif level == "medium":
        print(f"{COLOR_MAGENTA}{message}{COLOR_RESET}")
    elif level == "high":
        print(f"{COLOR_RED}{message}{COLOR_RESET}")

# Add to game setup (or merge with existing intro_elements if you have one)
intro_elements = {
    "rescuer_description": [
        "a gaunt, wide-eyed stranger", "a frantic woman with wild, tangled hair",
        "a pale, trembling man", "a wiry teenager with haunted eyes",
        "a disheveled figure", "a homeless man", "a street performer",
        "an old, grizzled park ranger", "a breathless young woman",
        "a nervous young man", "an elderly woman", "a maintenance worker",
        "a blind street vendor", "an old fisherman", "a young child",
        "a frantic steward", "a park ranger", "a lone cyclist",
        "a nervous engineer", "a carnival worker"
    ],
    "rescuer_action": [
        "seized your arm", "leapt out, screaming", "stumbled towards you",
        "burst through the crowd", "blocked your path", "ran into the road",
        "grabbed your arm", "emerged from the dense undergrowth",
        "began shouting at the sky", "pushed you back from the edge",
        "leaned over and said", "blocked the doorway", "grabbed your hand",
        "pointed towards the horizon", "tugged at your shirt", "grabbed your arm",
        "ran towards you", "flagged you down", "rushed towards you",
        "seized your arm"
    ],
    "rescuer_warning": [
        "Don't get on!", "Stop! Turn back!", "You have to get off, now!",
        "Don't get on!", "Don't go in there!", "Stop! It's going to fall!",
        "Run! We need to go now!", "You've got to turn back.",
        "The waters are coming!", "Stay back! It's going to crash!",
        "You shouldn't be here. It's not safe.",
        "Don't go in there. There is a problem, and you won't like it.",
        "Get down! The earth is angry!",
        "You need to go inland. The sea is coming to take us",
        "Don't step there! You will fall!",
        "Get to the lifeboats! The ship is going to burn!",
        "Run! The dam's breaking! The water is coming!",
        "Get out of here! There is a big boom coming!",
        "You need to leave, now! The factory is going to fall!",
        "No! Not that one! You have to leave now!"
    ],
    "disaster_ending": [
        "a cataclysmic, fiery explosion",
        "a devastating chain reaction of mangled metal and crushed bodies",
        "tragically succumbed to the depths of Lake Serenity",
        "twisted and plunged", "became an inferno", "buckled and plunged",
        "devastating explosion", "consuming everything in its path",
        "torrential rain, flooding the streets", "brutal impact",
        "snapped, sending chairs plummeting down the slope",
        "imploded in a cloud of dust and debris",
        "earthquake intensified, causing buildings to crumble",
        "a devastating typhoon made landfall", "opened up, swallowing the area",
        "flames erupted, engulfing a large section of the vessel",
        "a wall of water surged towards you", "massive fireball that erupted",
        "roof caved in, crushing everything below",
        "snapped. The massive wheel buckled"
    ],
    "survivor_fate": [
        "impaled", "crushed", "electrocuted", "consumed by a fire",
        "asphyxiated", "dragged under", "melted", "burned alive",
        "swept away", "frozen to death", "pulled under", "crushed by debris",
        "impaled by a broken beam", "consumed by a flare-up", "trampled",
        "drowned", "suffocated", "decapitated", "mangled", "torn apart",
        "collapsed", "died of shock", "died of injuries",
        "crushed by a falling beam", "incinerated",
        "crushed by falling machinery", "buried",
        "crushed by a toppled semi-truck", "sliced apart",
        "crushed beneath a falling section of the coaster track",
        "crushed beneath the weight of the falling stone",
        "electrocuted by downed power lines"
    ]
}

# Example placeholder for disasters dictionary
disasters = {
    "highway pileup": "The screech of tires and the sickening crunch of metal filled the air as multiple vehicles collided in a devastating chain reaction, scattering debris across the rain-slicked highway.",
    "plane crash": "A deafening roar ripped through the sky, followed by a catastrophic explosion that sent fiery debris raining down over McKinley. The air filled with smoke and the screams of the dying.",
    "rollercoaster derailment": "The joyous screams of riders turned into shrieks of terror as the 'Demon's Peak' coaster cars jumped the tracks, twisting into mangled steel high above the ground before plummeting to earth.",
    "bridge collapse": "A deep groan echoed across the river as the McKinley Memorial Bridge shuddered violently. In a horrifying spectacle, the concrete and steel structure buckled and collapsed, plunging vehicles into the dark waters below.",
    "subway accident": "With a jarring screech and a shower of sparks, the subway train derailed in the tunnel, sending carriages careening into the walls. Darkness descended, punctuated by the cries of trapped passengers.",
    "massive plane crash": "From the terminal window, you watched in disbelief as two passenger jets collided in a mid-air inferno, sending a shower of burning wreckage across the landscape.",
    "devastating highway pile-up on I-70": "The highway became a scene of unimaginable chaos as dozens of vehicles collided in a violent, screeching mess of twisted metal and shattered glass.",
    "luxury ferry sinking in Lake Serenity": "A sudden, sickening lurch threw passengers into panic as the 'Queen Isabella' began to list violently, water rapidly flooding the decks as it succumbed to the depths of the lake.",
    "terrifying rollercoaster derailment at 'Demon's Peak'": "The thrill ride turned into a nightmare as the rollercoaster cars flew off the rails at a terrifying height, the screams of the occupants swallowed by the grinding metal and snapping supports.",
    "inferno at the 'Crimson Lounge' nightclub": "A sudden eruption of flames engulfed the 'Crimson Lounge', turning the lively music and laughter into desperate cries for help as smoke billowed from the windows.",
    "collapse of the McKinley Memorial Bridge": "The ground beneath your feet vibrated ominously as the once-proud McKinley Memorial Bridge groaned and then catastrophically gave way, its sections crashing into the river below.",
    "explosion at the McKinley Chemical Plant": "A blinding flash and a thunderous roar ripped through the air as the McKinley Chemical Plant detonated, sending a shockwave and a massive cloud of toxic smoke billowing into the sky.",
    "wildfire that swept through McKinley National Forest": "The air grew thick with smoke and the smell of burning pine as an unstoppable wall of fire raged through McKinley National Forest, consuming everything in its path with terrifying speed.",
    "freak storm that flooded downtown McKinley": "In a matter of minutes, torrential rain transformed the streets of downtown McKinley into raging rivers, trapping people and vehicles in the rapidly rising floodwaters.",
    "high-speed train collision outside McKinley": "The screech of metal on metal culminated in a deafening crash.",
    "ski lift malfunction": "...", # Description handled by intro_elements
    "apartment collapse": "...", # Description handled by intro_elements
    "earthquake": "...", # Description handled by intro_elements
    "typhoon": "...", # Description handled by intro_elements
    "sinkhole": "...", # Description handled by intro_elements
    "cruise ship fire": "...", # Description handled by intro_elements
    "dam break": "...", # Description handled by intro_elements
    "gas pipeline explosion": "...", # Description handled by intro_elements
    "factory collapse": "...", # Description handled by intro_elements
    "ferris wheel malfunction": "..." # Description handled by intro_elements
}

# Define the rooms dictionary BEFORE it's used in randomize_item_locations
rooms = {
    "Front Porch": {"description": "The rotted wooden porch creaks under your feet. The front door, a heavy oak, is slightly ajar. A chilling breeze whispers through the overgrown ivy.", "exits": {"inside": "Foyer"}, "objects": [], "possible_containers": []},
    "Foyer": {"description": "A grand, yet decaying foyer. A crystal chandelier hangs precariously overhead, coated in dust. A wide staircase ascends to the upper floor. To the west, you see a shadowed living room, and to the east, a formal dining room.", "exits": {"upstairs": "Hallway", "west": "Living Room", "east": "Dining Room", "down": "Basement Stairs"}, "objects": ["dusty table"], "possible_containers": ["dusty table"]}, # Added Basement Stairs exit
    "Living Room": {"description": "Overturned armchairs and a tattered sofa litter the living room. The air is thick with the smell of stale tobacco. A cold fireplace is the room's centerpiece, with one loose-looking brick.", "exits": {"east": "Foyer"}, "objects": ["fireplace", "Brick"], "containers": ["fireplace"], "fireplace_brick_removed": False}, # Added Brick and fireplace_brick_removed flag
    "Dining Room": {"description": "A long, mahogany dining table is draped with a moth-eaten cloth. The silverware is tarnished, and cobwebs cling to the empty chairs. A dusty cupboard stands against one wall.", "exits": {"west": "Foyer", "south": "Kitchen"}, "objects": ["dining table", "cupboard"], "possible_containers": ["cupboard"]}, # Added cupboard to objects
    "Kitchen": {"description": "The kitchen is a scene of chaotic disarray. Broken plates and scattered utensils cover the floor. The back door is heavily boarded up. You see a glint of metal near the sink. There's also a boarded window.", "exits": {"north": "Dining Room"}, "objects": ["sink", "broken plates", "boarded window"], "possible_containers": []}, # Added boarded window
    "Library": {"description": "Towering bookshelves line the walls, filled with crumbling books. A large, oak desk sits in the center - its drawers slightly ajar and a book about urban demolition sitting open on top, featuring a wrecking ball doing what they do best.", "exits": {"east": "Foyer"}, "objects": ["bookshelves", "desk"], "possible_containers": ["desk", "bookshelves"]}, # Added desk to objects
    "Hallway": {"description": "The upstairs hallway is eerily silent. Moonlight spills through a grimy window at the end of the hall. Doors lead to several bedrooms and a bathroom. The attic entrance is a dark, imposing doorway.", "exits": {"downstairs": "Foyer", "north": "Master Bedroom", "south": "Guest Bedroom 1", "east": "Guest Bedroom 2", "west": "Bathroom", "up": "Attic Entrance"}, "objects": [], "possible_containers": []},
    "Master Bedroom": {"description": "A massive four-poster bed dominates the room, its velvet curtains ripped and faded.","exits": {"south": "Hallway"},"objects": ["bed", "nightstand", "ceiling fan with chains"], "possible_containers": ["nightstand"]}, # Added ceiling fan
    "Guest Bedroom 1": {"description": "A small, spartan bedroom with a single bed. A child's toy, a red SUV, sits forlornly on the floor. You might want to 'examine toy red suv'.", "exits": {"north": "Hallway"}, "objects": ["bed", "toy red suv"], "possible_containers": ["bed"]}, # Added toy suv
    "Guest Bedroom 2": {"description": "This room was clearly a study. A large, cluttered desk is covered in papers and strange diagrams. A camera rests on the desk. You might want to 'examine camera'.", "exits": {"west": "Hallway"}, "objects": ["desk", "strange diagrams", "camera"], "possible_containers": ["desk"]}, # Added diagrams and camera
    "Bathroom": {"description": "The air is thick with the stench of mildew. A cracked mirror reflects your uneasy face. The medicine cabinet hangs open.", "exits": {"east": "Hallway"}, "objects": ["mirror", "medicine cabinet"], "possible_containers": ["medicine cabinet"]}, # Added medicine cabinet object
    "Attic Entrance": {"description": "A dark and ominous entrance to the attic. It's secured with a heavy-looking lock.", "exits": {"down": "Hallway"}, "locked": True, "objects": [], "possible_containers": []},
    "Attic": {"description": "The attic is filled with dusty boxes and forgotten relics. You feel a strange presence here. A single newspaper clipping is pinned to a crate.", "exits": {"down": "Attic Entrance"}, "objects": ["crate"], "possible_containers": ["crate"]},
    "Basement Stairs": {"description": "A set of creaking wooden stairs leading down into the darkness. A padlock secures the entrance.", "exits": {"up": "Foyer", "down": "Main Basement Area"}, "locked": True, "objects": ["stairs"], "possible_containers": []}, # Added stairs object
    "Main Basement Area": {"description": "The air in the basement is cold and damp. Pipes groan overhead, and the smell of mildew is overpowering. A workbench is covered in rusty tools. A door to a Storage Room is to the south.", "exits": {"up": "Basement Stairs", "south": "Storage Room"}, "objects": ["workbench", "rusty tools"], "possible_containers": ["workbench"]}, # Added rusty tools
    "Storage Room": {"description": "A cramped storage room filled with shelves of dusty jars and forgotten equipment. You feel an intense sense of dread.", "exits": {"north": "Main Basement Area"}, "objects": ["shelves"], "possible_containers": ["shelves"], "locked": True} # Added locked status
}

# Define potential containers
containers = ["dresser", "cupboard", "drawer", "shelf", "box", "nightstand", "desk drawer", "medicine cabinet", "workbench"]

# Define lists of possible locations AFTER rooms are defined
key_possible_locations = ["Library", "Bathroom", "Main Basement Area", "Kitchen", "Dining Room", "Guest Bedroom 1", "Guest Bedroom 2"] # Removed "Living Room"
evidence_possible_locations = ["Living Room", "Guest Bedroom 1", "Guest Bedroom 2", "Dining Room", "Kitchen", "Master Bedroom"] # Example list
hazard_possible_locations = ["Kitchen", "Basement Stairs", "Living Room", "Master Bedroom", "Attic"] # Example list
final_room = "Attic" # Define the final room name

# Define disaster_warnings dictionary
disaster_warnings = {
    "highway pileup": ["Don't get on the ramp!", "The truck ahead is swerving!", "Brake now!"],
    "plane crash": ["Don't board the plane!", "Something's wrong with the engine!", "We have to get off!"],
    "rollercoaster derailment": ["Don't get on the ride!", "The track looks loose!", "Stop the coaster!"],
    "bridge collapse": ["Don't cross the bridge!", "It's making strange noises!", "Turn back!"],
    "subway accident": ["Stay off the platform!", "The train is coming too fast!", "Get back!"],
    # Add specific warnings for other disasters
    "massive plane crash": ["Look out! They're going to hit!", "Get down!", "Run for cover!"],
    "devastating highway pile-up on Route 42": ["Slow down! There's fog!", "Watch out for the log truck!", "Pull over!"],
    "luxury ferry sinking in Lake Serenity": ["The boat is taking on water!", "Get to the life rafts!", "Abandon ship!"],
    "terrifying rollercoaster derailment at 'Demon's Peak'": ["The harness isn't locked!", "It's going too fast!", "Hold on!"],
    "inferno at the 'Crimson Lounge' nightclub": ["Fire! Get out!", "Don't go towards the stage!", "The exit is blocked!"],
    "collapse of the McKinley Memorial Bridge": ["The bridge is shaking!", "Drive faster!", "Get off the bridge!"],
    "explosion at the McKinley Chemical Plant": ["Evacuate immediately!", "Toxic fumes!", "Run!"],
    "wildfire that swept through McKinley National Forest": ["The fire is spreading!", "Get to the river!", "Don't go into the woods!"],
    "freak storm that flooded downtown McKinley": ["Get to higher ground!", "The water is rising!", "Stay out of the basement!"],
    "high-speed train collision outside McKinley": ["The signals are out!", "Jump!", "Brace for impact!"],
    "ski lift malfunction": ["Don't get on the lift!", "The cable is fraying!", "Jump now!"],
    "apartment collapse": ["Get out of the building!", "The ceiling is cracking!", "Use the fire escape!"],
    "earthquake": ["Drop, cover, and hold on!", "Get away from windows!", "Watch for falling debris!"],
    "typhoon": ["Board up the windows!", "Seek shelter!", "Stay away from the coast!"],
    "sinkhole": ["The ground is collapsing!", "Run!", "Get away from the edge!"],
    "cruise ship fire": ["Get to the muster station!", "Put on your life jacket!", "Lower the lifeboats!"],
    "dam break": ["Head for the hills!", "A wall of water is coming!", "Don't stop!"],
    "gas pipeline explosion": ["Get away from the pipeline!", "Don't light anything!", "Call 911!"],
    "factory collapse": ["The roof is caving in!", "Run for the exit!", "Watch out for machinery!"],
    "ferris wheel malfunction": ["Stop the ride!", "We're stuck!", "Don't rock the gondola!"]
}

evidence = {
    "Photo of Jess Golden": {"found": False, "location": "[]", "character": "Jess Golden", "description": "Writing on back: Survived a club collapse but disappeared shortly after; her ultimate fate is unknown."},
    "Motorcycle Debris": {"found": False, "location": "[]", "character": "Sebastian Lebecque", "description": "Piece of metal from a motorcycle crash that immolated Sebastian Lebecque after he escaped a club collapse."},
    "Photo of Patti Fuller at Circuit City": {"found": False, "location": "[]", "character": "Patti Fuller", "description": "Writing on back: Implied to have died during an incident at Circuit City after surviving a subway bombing."},
    "Photo of Will Sax at Circuit City": {"found": False, "location": "[]", "character": "Will Sax", "description": "Writing on back: Implied to have died during an incident at Circuit City after surviving a subway bombing."},
    "Shard of Glass": {"found": False, "location": "[]", "character": "Zack Halloran", "description": "Sharp piece of glass from a falling pane that sliced Zack Halloran in half after he survived a subway bombing."},
    "Bloody Hubcap": {"found": False, "location": "[]", "character": "Al Kinsey", "description": "A blood-stained Ferrari hubcap that decapitated Al Kinsey after he survived a subway bombing."},
    "Dented Motorcycle Helmet": {"found": False, "location": "[]", "character": "Hal Ward", "description": "Hal Ward's helmet, found with his body after he drowned in a flash flood following his survival of a subway bombing."},
    "Charred Metal Pail": {"found": False, "location": "[]", "character": "Susan Fries", "description": "A burnt metal pail that exploded after its contents came in contact with a live spark, killing Susan Frie. She had previously survived a subway bombing."},
    "Rusty Blade": {"found": False, "location": "[]", "character": "Juliet Collins", "description": "A rusty knife, likely used by the Ripper (Bill Sangster), who killed Juliet Collins after she survived an explosion."},
    "Photo of Bill Sangster": {"found": False, "location": "[]", "character": "Bill Sangster", "description": "Writing on back: Survived an explosion, did not survive being crushed by drawbridge gears. Later identified as the infamous Whitechapel Ripper. His final fate is unknown."},
    "Piece of Corroded Pipe": {"found": False, "location": "[]", "character": "Matthew Upton", "description": "A section of pipe involved in the fiery death of Matthew Upton, who survived an explosion."},
    "Small Cobra Figurine": {"found": False, "location": "[]", "character": "Hector Barnes", "description": "A small snake figurine, reminiscent of the cobras that killed Hector Barnes after he survived an explosion, following his interaction with an Egyptian sarcophagus."},
    "Hieroglyph Fragment": {"found": False, "location": "[]", "character": "Mrs Stanley", "description": "A fragment with hieroglyphs, linked to an Egyptian sarcophagus that brought about the death by snakes of Mrs Stanley after she survived an explosion."},
    "Photo of Andrew Caine": {"found": False, "location": "[]", "character": "Andrew Caine", "description": "Writing on back: Survived an explosion. His subsequent fate is unknown."},
    "Shattered Glass Shards": {"found": False, "location": "[]", "character": "Stewart Tubbs", "description": "Fragments of glass jars from a hospital, linked to the death of Stewart Tubbs by inhaling noxious vapors after he survived an explosion."},
    "Bloody Earbuds": {"found": False, "location": "[]", "character": "Aldis Escobar", "description": "Aldis Escobar died in a fiery car crash on Las Vegas Boulevard after his near-death experience in an elevator. He was listening to music on his iPod at the time."},
    "Bloody Razor Blade": {"found": False, "location": "[]", "character": "Arlen Ploog", "description": "Arlen Ploog bled to death after being attacked by Tina with a razor blade."},
    "Photo of Danny Larriva": {"found": False, "location": "[]", "character": "Danny Larriva", "description": "Photo with writing on the back: Danny Larriva was a ten-year-old boy beaten to death, likely by his mother's boyfriend, Roberto Diaz."},
    "Photo of Roberto Diaz": {"found": False, "location": "[]", "character": "Roberto Diaz", "description": "Photo with writing on the back: Roberto Diaz was shot and then electrocuted by falling power lines after killing Danny Larriva."},
    "Costume Feather": {"found": False, "location": "[]", "character": "Shawna Engels", "description": "Shawna Engels, a dancer, was killed by a panther that got loose backstage during a show."},
    "Tom Gaines' Wedding Ring": {"found": False, "location": "[]", "character": "Tom Gaines", "description": "Tom Gaines was crushed to death by other passengers in a falling elevator."},
    "Allie Goodwin-Gaines' Wedding Ring": {"found": False, "location": "[]", "character": "Allie Goodwin-Gaines", "description": "Allie Goodwin-Gaines was crushed by the falling elevator after surviving the initial plunge."},
    "Warren Ackerman's Police Badge": {"found": False, "location": "[]", "character": "Warren Ackerman", "description": "Detective Warren Ackerman was electrocuted by falling power lines after shooting Roberto Diaz."},
    "Piece of Traffic Light": {"found": False, "location": "[]", "character": "Officer Sean Murphy", "description": "Officer Sean Murphy was decapitated by a falling traffic light in a van crash."},
    "Photo of Fred Newton": {"found": False, "location": "[]", "character": "Fred Newton", "description": "Photo with writing on the back: Fred Newton fell to his death from a malfunctioning elevator."},
    "Photo of Ethel Newton": {"found": False, "location": "[]", "character": "Ethel Newton", "description": "Photo with writing on the back: Ethel Newton fell to his death from a malfunctioning elevator."},
    "Bullet Casing": {"found": False,"location": "[]","character": "Macy","description": "Macy, a waitress who survived the club, was later killed by a falling metal panel dislodged by a bullet from Ben's gun. This casing is from the fatal shot."},
    "Photo of Stairs": {"found": False,"location": "[]","character": "Eric","description": "Eric, who survived the club collapse, later died by breaking his neck in a fall down stairs at the hospital. This photo represents the location of his death."},
    "Spent Bullet Casing": {"found": False,"location": "[]","character": "Ben","description": "Ben, who survived the club collapse, accidentally shot himself in the head with his own gun while fleeing the police. This spent casing was the cause of his death."},
    "Medical Chart Spike": {"found": False,"location": "[]","character": "Jamie","description": "Jamie, a band member who survived the club, later died at the morgue when he was impaled by a falling medical chart spike. This spike is the object that killed him."},
    "Photo of Jack Curtis": {"found": False, "location": "[]", "description": "Photo with writing on back describing how Jack Curtis was shot by Officer Beriev after the events in the precinct."},
    "Photo of Lonnie": {"found": False, "location": "[]", "description": "Photo with writing on back describing Lonnie's miraculous survival of a thirteen-story fall after snagging on a phone wire, sustaining severe injuries."},
    "Small Piece of Blood-Stained Fabric": {"found": False, "location": "[]", "description": "Small piece of fabric stained with blood from the knife attack Amy Tom survived in the alley."},
    "Spent Bullet Casing": {"found": False, "location": "[]", "description": "A spent bullet casing from Officer Beriev's gun when he shot Jack Curtis in the aftermath of the precinct events."}, 
    "Piece of Serrated Knife Blade": {"found": False, "location": "[]", "description": "A small, sharp piece of the serrated knife blade used by the man in the hood before he was shot and killed by Jack Curtis."},
    "Photo of Chelsea Cox": {"found": False, "location": "[]", "description": "Photo with writing on back describing Chelsea Cox's death when she was hit in the eyes by falling icicles after escaping death's initial design."},
    "Crumpled Metal Shard": {"found": False, "location": "[]", "description": "A small piece of twisted metal from Dawson Donahue's exploding car, detailing how the car then crushed him against a wall after he survived a garage fire."},
    "Burnt Fabric Piece": {"found": False, "location": "[]", "description": "A small, burnt piece of fabric from Katie Astin's clothes after she was electrocuted by a fallen lighting rig, detailing her survival of earlier 'accidents'."},
    "Shattered Record Shard": {"found": False, "location": "[]", "description": "A sharp shard from Joshua Cornell III's platinum record, detailing how it decapitated him after he survived falling stereo equipment."},
    "Glass Bottle Neck Shard": {"found": False, "location": "[]", "description": "A sharp piece of the glass bottle neck that was shot into Dominique Swann's mouth after she survived choking on a nut."},
    "Bloody Scalpel": {"found": False, "location": "[]", "character": "Rinoka", "description": "Survived a train crash, but died later in the hospital due to injuries exacerbated by falling surgical instruments and a bath."},
    "Charred Matchbook": {"found": False, "location": "[]", "character": "Peter", "description": "Survived a train crash but died later, trapped in a restaurant fire."},
    "Shattered Umbrella Spoke": {"found": False, "location": "[]", "character": "James", "description": "Survived a train crash but died later, impaled by umbrellas after being launched through a store window."},
    "Piece of Tow Cable": {"found": False, "location": "[]", "character": "Bodil", "description": "Survived a train crash but died later, launched by a tow truck and impaled by umbrellas in a store."},
    "Bloody Chainsaw Fragment": {"found": False, "location": "[]", "character": "Mary-Beth", "description": "Survived a train crash but died later, killed by falling scaffolding and a chainsaw."},
    "Rusty Faucet Handle": {"found": False, "location": "[]", "character": "Andrew Williams", "description": "Died in a hospital, scalded in a bath."},
    "Bloody Corkscrew": {"found": False, "location": "[]", "character": "Jack Cohen", "description": "Survived a train crash but died later, impaled in the eye with a corkscrew in Central Park."},
    "Bottle of Acetic Acid": {"found": False, "location": "[]", "character": "Chablis", "description": "A small bottle of acetic acid, spilled near potassium ferricyanide, created deadly fumes that ended Chablis's life in a locked darkroom."},
    "Section of Braided Hair Extension": {"found": False, "location": "[]", "character": "Shiraz", "description": "A piece of braided hair extension, tragically caught in spinning rims during a music video shoot, leading to Shiraz's violent death."},
    "Toy Laundry Truck": {"found": False, "location": "[]", "character": "Gunter", "description": "A miniature laundry truck, a reminder of the vehicle that fatefully struck Gunter, severing his body."},
    "Broken Cigarette Holder": {"found": False, "location": "[]", "character": "Merlot", "description": "Merlot's elegant cigarette holder, found broken amidst the chaos of the sinking ship, hinting at her final, trampled moments."},
    "Piece of Seaweed": {"found": False, "location": "[]", "character": "Carlo", "description": "A piece of seaweed, tangled around Carlo's retrieved body, a morbid souvenir of his drowning after the ship's demise."},
    "Miniature Buffet Table Piece": {"found": False, "location": "[]", "character": "Rose", "description": "A small piece from a miniature buffet table, crushing Rose against a bulkhead during the ship's violent tilt."},
    "Spent Bullet Casing 2": {"found": False, "location": "[]", "character": "Brut", "description": "A spent bullet casing, symbolizing the explosion that threw Brut from the ship's deck into the fatal waters below."}, # Renamed duplicate key
    "Photo of Sherry": {"found": False, "location": "[]", "character": "Sherry", "description": "A photo of Sherry. On the back, a chilling note describes her death after escaping the ship, tragically struck by a bus."},
    "Brick": {"found": False, "location": "Living Room", "container": None, "character": "Alex Browning", "description": "A dirty brick, one corner covered with dried blood, hair and gore. This was the brick that killed Alex Browning; he survived the plane crash and was being hunted by Death, narrowly escaping its design multiple times. If HE didn't make it..."},
    "Retractable Clothesline Piece": {"found": False, "location": "[]", "character": "Tod Waggner", "description": "A piece of a retractable clothesline. Tod died when he slipped in his bathroom and accidentally hanged himself with the clothesline."},
    "Photo of Clear Rivers": {"found": False, "location": "[]", "character": "Clear Rivers", "description": "A photo of Clear. Writing on the back describes her survival of the plane crash and her understanding that Death is coming for the survivors. She is actively trying to evade it."},
    "Light Bulb": {"found": False, "location": "[]", "character": "Carter Horton", "description": "A light bulb from a large sign. Carter was killed when a falling sign crushed him."},
    "Miniature Toy Bus": {"found": False, "location": "[]", "character": "Terry Chaney", "description": "A miniature model of a bus. Terry was tragically struck and killed by a speeding bus."},
    "Charred Mug": {"found": False, "location": "[]", "character": "Valerie Lewton", "description": "A burnt and broken ceramic mug. Ms. Lewton died in a house fire (ahem..explosion) caused by a series of unfortunate accidents."},
    "Bloody Piece of Metal": {"found": False, "location": "[]", "character": "Billy Hitchcock", "description": "A jagged piece of metal, stained with what appears to be blood. Billy was decapitated by a piece of metal flung from a train."},
    "Navel Piercing with Crystal": {"found": False, "location": "[]", "character": "Carrie Dreyer", "description": "A small navel piercing with a dangling crystal, belonging to Carrie Dreyer. She died in the Devil's Flight roller coaster crash."},
    "Mud Flap Girl Necklace": {"found": False, "location": "[]", "character": "Franklin Cheeks", "description": "A cheap, chrome silhouette of a mud flap girl on a chain, won by Franklin Cheeks. The back of his head was (mostly) removed by a radiator fan after surviving the roller coaster crash."},
    "Fuzzy Red Dice": {"found": False, "location": "[]", "character": "Rory Peters", "description": "A pair of fuzzy red dice, similar to those in Rory Peters' car. He died by being sliced into several chunks by wire fencing after surviving the route 23 pile-up."},
    "Cigarette": {"found": False, "location": "[]", "character": "Kat Jennings", "description": "A cigarette, like the ones smoked by Kat Jennings. She died when her car's airbag deployed, impaling her head on a pipe after surviving the route 23 pile-up."},
    "Pool Ball Keychain": {"found": False, "location": "[]", "character": "Eugene Dix", "description": "An orange striped pool ball keychain, the kind Eugene Dix owned. He died by accidental incineration in Lakeview Hospital along with Clear Rivers after surviving the route 23 pile-up."},
    "Valium Pills": {"found": False, "location": "[]", "character": "Nora Carpenter", "description": "A bottle of Valium pills, like those taken by Nora Carpenter. She died when her head was pulled off by an elevator after surviving the route 23 pile-up."},
    "Empty Water Bottle": {"found": False, "location": "[]", "character": "Tim Carpenter", "description": "An empty water bottle, like those Tim Carpenter used as drumsticks. He died being crushed by a falling plate glass window at a dentist's office after surviving the route 23 pile-up."},
    "Nipple Ring": {"found": False, "location": "[]", "character": "Evan Lewis", "description": "A nipple ring, like the one worn by Evan Lewis. He died after being impaled through the facial by a fire ladder after surviving the route 23 pile-up."},
    "Roxy Duffle Bag": {"found": False, "location": "[]", "character": "Shaina Gordon", "description": "A Roxy brand duffle bag, belonging to Shaina Gordon. She died in the route 23 pile-up."},
    "Plastic Bag of Weed": {"found": False, "location": "[]", "character": "Dano Royale", "description": "A small plastic bag containing weed, like the one Dano Royale had. He died in the route 23 pile-up."},
    "White Rose": {"found": False, "location": "[]", "character": "Isabella Hudson", "description": "A white rose, similar to those in Isabella Hudson's van for a memorial service. She survived the route 23 pile-up and Death's design by giving birth to her baby."},
    "Work Gloves": {"found": False, "location": "[]", "character": "Brian Gibbons", "description": "A pair of work gloves, worn by Brian Gibbons. He died in an explosion caused by a barbeque grill and propane tank after surviving the Lakeview Apartments fire and a secondary attempt on his life by a news van."},
    "Newspaper Clipping about Flight 180": {"found": False, "location": "[]", "character": "Clear Rivers", "description": "A newspaper clipping detailing the Flight 180 disaster and the subsequent deaths of the survivors. Clear Rivers, a survivor of Flight 180, died from gas in a hospital after helping the route 23 pile-up survivors."},
    "Photo of Jason on Devil's Flight": {"found": False, "location": "[]", "character": "Jason Wise", "description": "A photo of Jason Wise on the Devil's Flight roller coaster. He died in the roller coaster crash."},
    "Overexposed Photo of Kevin": {"found": False, "location": "[]", "character": "Kevin Fischer", "description": "An overexposed photo of Kevin Fischer. He survived the roller coaster crash but died later in a subway crash."},
    "Photo of Lewis from Ring-The-Bell Game": {"found": False, "location": "[]", "character": "Lewis Romero", "description": "A photo of Lewis Romero at the Ring-The-Bell game, where he knocked off the bell. He survived the roller coaster crash but died later by being crushed by weights."},
    "Photo of Ashley and Ashlyn at Clown Shoot": {"found": False, "location": "[]", "character": "Ashley Freund & Ashlyn Halperin", "description": "A photo of Ashley Freund and Ashlyn Halperin at the clown shoot game. They survived the roller coaster crash but died later in a tanning bed accident."},
    "Photo of Ian with Banners": {"found": False, "location": "[]", "character": "Ian McKinley", "description": "A photo of Ian McKinley with banners in the background that look like teeth. He survived the roller coaster crash but died later by being crushed by a falling sign and cherry picker basket."},
    "Strip of nails": {"found": False, "location": [], "character": "Erin Ulmer", "description": "A strip of collated nails, the type used in a nail gun. Several are missing, and traces of blood suggest they were forcibly removed. It's a chilling reminder of Erin Ulmer's gruesome demise."},    "Camera": {"found": False, "location": "[]", "character": "Wendy Christensen", "description": "An older digital camera used by Wendy Christensen to capture several ominous photographs hinting at the deaths of her classmates. She survived the Devil's Flight roller coaster malfunction and subsequent attempt on her life by Ian McKinley only to be killed in a subway crash several months later."},    
    "Photo of Julie giving the finger": {"found": False, "location": "[]", "character": "Julie Christensen", "description": "A photo of Julie Christensen giving the finger for the yearbook. She survived the Devil's Flight roller coaster premonition."},
    "Photo of Perry": {"found": False, "location": "[]", "character": "Perry Malinowski", "description": "A photo of Perry Malinowski. She survived the Devil's Flight roller coaster premonition but died later at the fair."},
    "Photo of Amber": {"found": False, "location": "[]", "character": "Amber Regan", "description": "A photo of Amber Regan. She survived the Devil's Flight roller coaster premonition."}, 
    "Toy SUV": {"found": False, "location": "[]", "character": "Kimberly Corman", "description": "A photo of Kimberly Corman. She survived the route 23 pile-up premonition and confronted Death at the lake."},
    "Photo of Officer Burke": {"found": False, "location": "[]", "character": "Thomas Burke", "description": "A photo of Officer Thomas Burke. He survived the route 23 pile-up premonition."},
    "Photo of Frankie": {"found": False, "location": "[]", "character": "Frankie Arnold", "description": "A photo of Frankie Arnold. He died in the route 23 pile-up."},
    "Newspaper Clipping": {"found": False, "location": "Attic", "character": "You", "description": "A newspaper clipping with a headline about a major disaster."}, # Modified entry
}

keys = {
    "Attic Key": {"found": False, "location": "Library"},
    "Basement Key": {"found": False, "location": "Bathroom"},
    "Storage Room Key": {"found": False, "location": "Main Basement Area"}
}

COLOR_RED = '\033[91m'
COLOR_YELLOW = '\033[93m'
COLOR_RESET = '\033[0m'

def center_text(text):
    """Center each line of text in the terminal."""
    lines = text.splitlines()
    terminal_width = os.get_terminal_size().columns
    centered_lines = [line.center(terminal_width) for line in lines]
    return '\n'.join(centered_lines)

def display_title_screen():
    """Display an ASCII art title screen with 'Terminal' in red and centered."""
    title_art = r"""
    ███████╗██╗███╗   ██╗ █████╗ ██╗         ██████╗ ███████╗███████╗████████╗██╗███╗   ██╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
    ██╔════╝██║████╗  ██║██╔══██╗██║         ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██║████╗  ██║██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
    █████╗  ██║██╔██╗ ██║███████║██║         ██║  ██║█████╗  ███████╗   ██║   ██║██╔██╗ ██║███████║   ██║   ██║██║   ██║██╔██╗ ██║
    ██╔══╝  ██║██║╚██╗██║██╔══██║██║         ██║  ██║██╔══╝  ╚════██║   ██║   ██║██║╚██╗██║██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
    ██║     ██║██║ ╚████║██║  ██║███████╗    ██████╔╝███████╗███████║   ██║   ██║██║ ╚████║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝    ╚═════╝ ╚══════╝╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                            ████████╗███████╗██╔═██╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗
                                            ╚══██╔══╝██╔════╝██║  ██║████╗ ████║██║████╗  ██║██╔══██╗██║
                                               ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║
                                               ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║
                                               ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
                                               ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
    """
    os.system('cls' if os.name == 'nt' else 'clear')

    # Find the indices of 'Terminal' in the ASCII art
    terminal_start = title_art.find("Terminal")
    if terminal_start != -1:
        terminal_end = terminal_start + len("Terminal")
        colored_title_lines = []
        for line in title_art.splitlines():
            start_index = line.find("Terminal")
            if start_index != -1:
                colored_line = line[:start_index] + COLOR_RED + "Terminal" + COLOR_RESET + line[start_index + len("Terminal"):]
                colored_title_lines.append(colored_line)
            else:
                colored_title_lines.append(line)
        centered_title_art = center_text('\n'.join(colored_title_lines))
        print(centered_title_art)
    else:
        centered_title_art = center_text(title_art)
        print(f"{COLOR_RED}{centered_title_art}{COLOR_RESET}") # Fallback if 'Terminal' not found

    print(f"\n{COLOR_YELLOW}{center_text('Death is closer than it appears')}{COLOR_RESET}")
    print(center_text("\nPress Enter to begin..."))
    input()
    os.system('cls' if os.name == 'nt' else 'clear')

# Example of how to run it (if this is the main script)
if __name__ == "__main__":
    display_title_screen()


def game_intro():
    global player
    width = get_terminal_width()
    # Add this call to the beginning of game_intro
    display_title_screen()
    print(textwrap.fill("\nFINAL DESTINATION: TERMINAL", width=width))
    print(textwrap.fill("\nWelcome to McKinley, population: Dropping like flies.", width=width))
    print(textwrap.fill("\nLocal tales speak of numerous accidental deaths, murders, and suicides attributed to something called 'Death's List'. It was nonsense to you from the moment you first heard that bullshit conspiracy theory. Heavy on the past tense.", width=width))
    print(textwrap.fill("\nYou've just arrived at the abandoned residence of one William Bludworth - who has not been seen in some time, but it is said he held evidence proving Death was a force of nature out to claim survivors of multiple casualty disasters.", width=width))
    print(textwrap.fill("\nYou are an investigative journalist determined to uncover the truth behind the legends of McKinley before the demolition of the place, which is supposed to be in 2 days.", width=width))

    chosen_disaster = random.choice(list(disasters.keys()))
    disaster_description = disasters[chosen_disaster]
    rescuer_description = random.choice(intro_elements["rescuer_description"])
    rescuer_action = random.choice(intro_elements["rescuer_action"])

    # Select a warning based on the chosen disaster
    relevant_warnings = disaster_warnings.get(chosen_disaster, intro_elements["rescuer_warning"]) # Fallback to general warnings
    rescuer_warning = random.choice(relevant_warnings)

    disaster_ending = random.choice(intro_elements["disaster_ending"])

    # --- Select 3 UNIQUE survivor fates ---
    fates_list = intro_elements["survivor_fate"]
    if len(fates_list) < 3:
        print("Warning: Not enough unique survivor fates defined to pick 3.")
        # Handle this case, maybe repeat or use fewer? For now, let's assume >= 3
        chosen_fates = fates_list * 3 # Simple fallback: repeat if list is too short
        chosen_fates = chosen_fates[:3]
    else:
        chosen_fates = random.sample(fates_list, 3) # Select 3 unique fates

    survivor_fate1 = chosen_fates[0]
    survivor_fate2 = chosen_fates[1]
    survivor_fate3 = chosen_fates[2]
    # --- End of change ---

    # Wrap the dynamically generated story parts
    print(textwrap.fill(f"\nYou have a personal stake because, as fate would have it, you recently walked away from a {chosen_disaster} that ended many lives.", width=width))
    print(textwrap.fill(f"You were about to be caught up in the disaster, when {rescuer_description}, {rescuer_action}, '{rescuer_warning}!'", width=width))
    print(disaster_description) # Already wrapped
    print(textwrap.fill(f"The {disaster_ending}.", width=width))
    print(textwrap.fill(f"More were lost afterwards, the other survivors.. in increasingly gruesome accidents. One was {survivor_fate1}, another was {survivor_fate2}, and a third was {survivor_fate3}. You are the last one left.", width=width))

    # Wrap the goal and instructions
    print(textwrap.fill("\nYour goal is to find 3 key pieces of evidence related to people who saw Death coming before your own time runs out.", width=width))
    print(textwrap.fill("You have a limited number of turns before dawn.", width=width))
    print(textwrap.fill("Type 'list' to see available actions.", width=width))
    print(textwrap.fill("\nExplore the grounds, interact with objects or examine evidence, and watch your step!", width=width))
    print(textwrap.fill("\nGood luck...", width=width))
    input("\nType or press 'Enter' to begin...")

    # In the game_intro function, after choosing the disaster:
    chosen_disaster = random.choice(list(disasters.keys()))
    disaster_description = disasters[chosen_disaster]

    # Store the chosen disaster in the player dictionary
    player['opening_disaster'] = chosen_disaster

def get_ambient_event():
    """Returns a random ambient event to increase tension"""
    events = [
        f"{COLOR_RED}The house creaks ominously around you.{COLOR_RESET}",
        f"{COLOR_RED}A cold draft sends shivers down your spine.{COLOR_RESET}",
        f"{COLOR_RED}You hear the distant sound of metal scraping against metal.{COLOR_RESET}",
        f"{COLOR_RED}The floorboards groan beneath your feet.{COLOR_RESET}",
        f"{COLOR_RED}You catch a glimpse of movement from the corner of your eye.{COLOR_RESET}",
        f"{COLOR_RED}The lights flicker momentarily.{COLOR_RESET}",
    ]
    
    # Higher chance for events as time runs out
    chance = 0.1
    if player['turns_left'] <= 30:
        chance = 0.25
    if player['turns_left'] <= 15:
        chance = 0.4
        
    if random.random() < chance:
        return random.choice(events)
    return None

def review_evidence():
    """Shows the player their collected evidence and what it means"""
    collected = []
    for name, info in evidence.items():
        if info.get('found', False):
            collected.append((name, info.get('description', 'No description available')))
    
    if not collected:
        print("You haven't found any evidence yet.")
        return
    
    print(f"\n{COLOR_YELLOW}Evidence Collected:{COLOR_RESET}")
    for i, (name, desc) in enumerate(collected, 1):
        print(f"{i}. {COLOR_YELLOW}{name}{COLOR_RESET}: {desc}")
    
    if len(collected) >= REQUIRED_EVIDENCE:
        print(f"\n{COLOR_MAGENTA}The evidence is clear - Death has a design, and you're on its list.{COLOR_RESET}")
        if not escape_mode:
            print(f"{COLOR_RED}You should get out while you still can!{COLOR_RESET}")
    else:
        print(f"\n{COLOR_MAGENTA}You need {REQUIRED_EVIDENCE - len(collected)} more piece(s) of evidence to confirm your suspicions.{COLOR_RESET}")

def randomize_item_locations():
    global evidence, keys # Ensure we are modifying the global dictionaries

    print("\n--- Starting Item Randomization ---") # More informative output

    # 1. Reset locations, containers, and found status for all items
    for item_dict_name, item_dict in [("evidence", evidence), ("keys", keys)]:
        for item_name, item_info in item_dict.items():
            item_info['found'] = False
            item_info['location'] = None # Reset location
            item_info['container'] = None # Reset container
            print(f"Reset {item_dict_name} '{item_name}'")

    # 2. Identify all possible container slots: (room_name, container_name)
    all_container_slots = []
    for room_name, room_data in rooms.items():
        # Use 'possible_containers' which should list container *objects* in the room
        for container_obj in room_data.get('possible_containers', []):
            # Ensure the container object actually exists in the room's objects list for consistency
            if container_obj in room_data.get('objects', []):
                all_container_slots.append((room_name, container_obj))
            else:
                # This indicates a potential mismatch in your room definitions
                print(f"Warning: Container '{container_obj}' listed in possible_containers for '{room_name}' but not in objects.")

    print(f"Found {len(all_container_slots)} potential container slots.")

    # 3. Identify items to place dynamically
    key_names = list(keys.keys())
    print(f"Keys to place: {key_names}")

    # Exclude fixed/special evidence items for dynamic placement
    fixed_evidence_dynamic_exclusion = ["Newspaper Clipping", "Brick"] # Add any other fixed evidence for dynamic exclusion
    placeable_evidence_names = [e for e in evidence.keys() if e not in fixed_evidence_dynamic_exclusion]
    print(f"Placeable evidence: {placeable_evidence_names}")

    # 4. Determine number of evidence items to select based on available slots
    num_slots_available = len(all_container_slots)
    num_keys_to_place = len(key_names)

    # Reserve the "Attic", "crate" slot for the Newspaper Clipping
    reserved_slot = ("Attic", "crate")
    if reserved_slot in all_container_slots:
        all_container_slots.remove(reserved_slot)
        num_slots_available -= 1
        print(f"Reserved slot {reserved_slot} for Newspaper Clipping.")

    if num_keys_to_place > num_slots_available:
        raise ValueError(f"Not enough container slots ({num_slots_available}) to place all keys ({num_keys_to_place}). Check room definitions.")

    num_evidence_slots = num_slots_available - num_keys_to_place
    num_evidence_to_select = min(len(placeable_evidence_names), num_evidence_slots)
    print(f"Selecting {num_evidence_to_select} out of {len(placeable_evidence_names)} placeable evidence items.")

    # 5. Select a random subset of evidence
    selected_evidence = random.sample(placeable_evidence_names, num_evidence_to_select)
    print(f"Selected evidence: {selected_evidence}")

    # 6. Combine items to be placed dynamically
    items_to_place = key_names + selected_evidence
    print(f"Total items to place dynamically: {items_to_place}")

    # 7. Shuffle container slots
    random.shuffle(all_container_slots)
    print("Shuffled container slots for dynamic placement.")

    # 8. Assign items to shuffled slots
    print("\n--- Dynamic Item Placement ---") # More specific output
    used_slots = set()
    for item_name in items_to_place:
        if not all_container_slots:
            print(f"Warning: Ran out of container slots while trying to place '{item_name}'.")
            break # Stop if we run out of slots unexpectedly
        room_name, container_name = all_container_slots.pop()
        slot = (room_name, container_name)
        if slot in used_slots:
            continue  # Skip duplicate slot
        used_slots.add(slot)
        if item_name in keys:
            keys[item_name]['location'] = room_name
            keys[item_name]['container'] = container_name
            print(f"Placed Key '{item_name}' in '{container_name}' in room '{room_name}'")
        elif item_name in evidence:
            evidence[item_name]['location'] = room_name
            evidence[item_name]['container'] = container_name
            print(f"Placed Evidence '{item_name}' in '{container_name}' in room '{room_name}'")

    # 9. Handle fixed items explicitly
    print("\n--- Fixed Item Placement ---") # More specific output

    # Ensure Newspaper Clipping is always in the Attic crate
    newspaper_clipping_name = "Newspaper Clipping"
    if newspaper_clipping_name in evidence:
        evidence[newspaper_clipping_name]['location'] = "Attic"
        evidence[newspaper_clipping_name]['container'] = "crate"
        used_slots.add(("Attic", "crate")) # Mark as used
        print(f"Placed Fixed Evidence '{newspaper_clipping_name}' in 'crate' in room 'Attic'")
    else:
        print(f"Warning: Fixed evidence '{newspaper_clipping_name}' not found in evidence dictionary.")

    # --- Add Fixed Placement for Basement Key ---
    basement_key_name = "Basement Key"
    if basement_key_name in keys:
        slot = ("Living Room", "fireplace")
        if slot not in used_slots:
            keys[basement_key_name]['location'] = "Living Room"
            keys[basement_key_name]['container'] = "fireplace"
            used_slots.add(slot)
            print(f"Placed Fixed Key '{basement_key_name}' in 'fireplace' in room 'Living Room'")
        else:
            print("Warning: 'Basement Key' slot already used for fixed placement.")
    else:
        print("Warning: '{basement_key_name}' not found in keys dictionary for fixed placement.")

    print("--- End Item Placement ---\n")

    # --- (Optional) Randomize Hazard Placement ---
    # Example: Define hazards dictionary
    potential_hazards = {
        "unstable shelf": {
            "description": "A shelf packed with heavy objects looks ready to collapse...",
            "death_message": "As you brush past, the shelf gives way, burying you under its contents.",
            "trigger_chance": 0.1
        },
        "faulty wiring": {
            "description": "Exposed electrical wires crackle ominously near a metal object...",
            "death_message": "You touch the nearby metal object, completing a circuit. A lethal shock courses through you.",
            "trigger_chance": 0.15  # Triggered by interaction, not just entry
        },
        "precarious object": {
            "description": "Something heavy (like a chandelier or large vase) shifts precariously above...",
            "death_message": "With a groan of stressed metal/wood, the object breaks free and falls, crushing you instantly.",
            "trigger_chance": 0.1  # Could be triggered by loud noise or vibration (like slamming door)
        },
        "weak floorboards": {
            "description": "The floorboards in this area look rotten and weak...",
            "death_message": "Your weight is too much! The floorboards snap, sending you plummeting into darkness below.",
            "trigger_chance": 0.25  # Higher chance on movement
        }
    }
    # --- Hazard Placement Logic ---
    # Decide how many hazards to place (e.g., 1 or 2)
    num_hazards_to_place = random.randint(1, 2) # Place 1 or 2 random hazards
    placed_hazards = 0

    # Shuffle potential locations to avoid placing multiple hazards in the same room easily
    random.shuffle(hazard_possible_locations)
    available_locations = hazard_possible_locations[:] # Copy the list

    while placed_hazards < num_hazards_to_place and available_locations:
        chosen_hazard_room = available_locations.pop(0) # Take the next available location

        # Check if the room already has a hazard from a previous iteration (if placing multiple)
        if 'hazard' not in rooms[chosen_hazard_room]:
            hazard_type = random.choice(list(potential_hazards.keys()))
            hazard_info = potential_hazards[hazard_type]

            rooms[chosen_hazard_room]['hazard'] = hazard_type
            # Store the full info for easier access later
            rooms[chosen_hazard_room]['hazard_info'] = hazard_info
            # Keep separate description/death for potential modification by game events
            rooms[chosen_hazard_room]['hazard_description'] = hazard_info['description']
            rooms[chosen_hazard_room]['hazard_death'] = hazard_info['death_message']
            rooms[chosen_hazard_room]['hazard_chance'] = hazard_info['trigger_chance']

            print(f"Debug: Placed hazard '{hazard_type}' in {chosen_hazard_room}")
            placed_hazards += 1
        # Optional: else: print(f"Debug: Room {chosen_hazard_room} already has a hazard, skipping.")

    if placed_hazards < num_hazards_to_place:
        print("Debug: Could not place all requested hazards (ran out of unique locations).")

def display_objectives():
    """Display current game objectives."""
    print(f"\n{COLOR_MAGENTA}Current Objectives:{COLOR_RESET}")
    
    # Evidence collection objective
    evidence_count = player['found_evidence']
    if evidence_count < REQUIRED_EVIDENCE:
        print(f"- Find evidence: {COLOR_YELLOW}{evidence_count}/{REQUIRED_EVIDENCE} pieces{COLOR_RESET}")
    else:
        print(f"- {COLOR_GREEN}✓ Found all required evidence!{COLOR_RESET}")
    
    # Unlocking objectives
    for room_name in ["Attic Entrance", "Basement Stairs", "Storage Room"]:
        if room_name in rooms and rooms[room_name].get('locked', False):
            print(f"- Find key for {COLOR_YELLOW}{room_name}{COLOR_RESET}")
        elif room_name in rooms:
            print(f"- {COLOR_GREEN}✓ Unlocked {room_name}!{COLOR_RESET}")
    
    # Escape objective
    if escape_mode:
        print(f"- {COLOR_RED}ESCAPE THE HOUSE IMMEDIATELY!{COLOR_RESET}")
    
    # Time warning
    if player['turns_left'] <= 15:
        print(f"\n{COLOR_RED}WARNING: Demolition imminent! ({player['turns_left']} turns left){COLOR_RESET}")
    elif player['turns_left'] <= 30:
        print(f"\n{COLOR_YELLOW}CAUTION: Time is running out. ({player['turns_left']} turns left){COLOR_RESET}")

def display_status():
    """Clears the screen and displays the current room, status, inventory, and exits."""
    width = get_terminal_width()
    os.system('cls' if os.name == 'nt' else 'clear') # Clear screen

    current_room = player['location']
    room_data = rooms[current_room]
    wrapped_description = textwrap.fill(room_data['description'], width=width)

    # Highlight Room Name
    print(f"\n--- {COLOR_YELLOW}{current_room}{COLOR_RESET} ---")
    print(wrapped_description)

    # Highlight Objects and Revealed Items
    visible_objects = room_data.get('objects', [])
    revealed_items = room_data.get('revealed_items', [])
    display_items = visible_objects + [item for item in revealed_items if item not in visible_objects] # Combine and avoid duplicates if item is both object and revealed

    if display_items:
        # Separate keys/evidence from regular objects for potential different highlighting
        key_evidence_items = [f"{COLOR_YELLOW}{item}{COLOR_RESET}" for item in display_items if item in keys or item in evidence]
        other_objects = [f"{COLOR_MAGENTA}{item}{COLOR_RESET}" for item in display_items if item not in keys and item not in evidence]
        items_str = ", ".join(other_objects + key_evidence_items)
        display_objectives() # Call objectives display here for better context
        print(f"You see: {items_str}") # Removed "the following objects here" for brevity

    # Display Status Info
    print(f"\nTurns Left: {player['turns_left']}")
    print(f"Score: {player['score']}") # Added score display
    inventory_str = ", ".join([f"{COLOR_YELLOW}{item}{COLOR_RESET}" for item in player['inventory']]) if player['inventory'] else "Empty"
    print(f"Inventory: {inventory_str}")
    evidence_str = f"{player['found_evidence']} / {REQUIRED_EVIDENCE}"
    print(f"Evidence Found: {COLOR_YELLOW}{evidence_str}{COLOR_RESET}")

    # Highlight Exits
    print(f"\n{COLOR_CYAN}Exits:{COLOR_RESET}")
    for direction, room_name in room_data['exits'].items():
        if room_name in rooms: # Check if the exit leads to a valid room
            locked_status = f" {COLOR_RED}(Locked){COLOR_RESET}" if rooms[room_name].get('locked') else ""
            # Indicate if the exit leads outside during escape mode
            escape_exit_indicator = f" {COLOR_GREEN}(Escape Route!){COLOR_RESET}" if escape_mode and room_name == "Front Porch" else ""
            print(f"- {COLOR_CYAN}{direction.capitalize()}{COLOR_RESET}: {room_name}{locked_status}{escape_exit_indicator}")
        else:
            print(f"- {COLOR_CYAN}{direction.capitalize()}{COLOR_RESET}: Leads somewhere unknown (Error: Room '{room_name}' not defined)")


    # Highlight Hazard Warnings in Room Description (Subtle)
    if room_data.get('hazard'):
        hazard_desc = room_data.get('hazard_description', "Something feels dangerous here.")
        print(f"{COLOR_RED}Warning: {hazard_desc}{COLOR_RESET}")

    # Highlight Time Warnings (Wrecking Ball)
    warning_message = ""
    # Adjust warning thresholds and messages as needed
    if player['turns_left'] <= 14 and player['turns_left'] > 0:
        if random.random() < 0.6: # 60% chance
            warning_message = "The roar of heavy machinery is deafening. You can hear the distinct sound of impacts nearby. The demolition is happening NOW! Time is running out!"
    elif player['turns_left'] <= 29 and player['turns_left'] > 15:
        if random.random() < 0.4:
            warning_message = "The mechanical sounds are getting louder. You can hear distinct grinding and the rumble of an engine."
    elif player['turns_left'] <= 44 and player['turns_left'] > 30:
        if random.random() < 0.2:
            warning_message = "The distant hum is more noticeable now, and you occasionally hear a metallic clank."
    elif player['turns_left'] <= 60 and player['turns_left'] > 45 and random.random() < 0.1:
        warning_message = "You hear a faint, distant hum, like machinery far away."

    if warning_message:
        print(f"\n{COLOR_RED}{warning_message}{COLOR_RESET}")

    # List available actions command hint (already in Terminal_test.py's display_status)
    # print(f"\nType '{COLOR_CYAN}list{COLOR_RESET}' for available actions.") # Optional: Add this hint if list_actions isn't prominent enough

def check_time():
    """Checks if the player has run out of turns."""
    if player['turns_left'] <= 0:
        print(f"\n{COLOR_RED}CRUNCH! A massive wrecking ball slams into the side of the house!{COLOR_RESET}")
        print(f"{COLOR_RED}The vibrations bring the already unstable structure down around you.{COLOR_RESET}")
        print("\nGame Over - The demolition crew didn't wait.")
        return True # Time is up
    return False # Time remains

def check_final_room():
    """Checks if the player is escaping and handles endings."""
    global escape_mode # Ensure we can modify escape_mode if needed (e.g., for specific endings)
    if escape_mode and player['location'] == "Front Porch":
        print("\nYou burst out onto the Front Porch, desperate to escape!")
        inventory_count = len(player['inventory'])
        print(f"You scramble across the porch, weighed down by the items you've collected ({inventory_count} items)...")
        time.sleep(1) # Dramatic pause

        # Ending Logic
        if inventory_count > ESCAPE_MODE_INVENTORY_THRESHOLD:
            print(f"{COLOR_RED}The rotten porch groans under the combined weight!{COLOR_RESET}")
            print(f"{COLOR_RED}With a sickening crack, the floorboards give way beneath you!{COLOR_RESET}")
            time.sleep(1)
            print(f"{COLOR_RED}You plummet downwards just as the wrecking ball swings towards the house...{COLOR_RESET}")
            print("\nGame Over - Crushed by the wrecking ball after falling through the porch.")
        elif player['found_evidence'] < REQUIRED_EVIDENCE:
             # This case should ideally not be reachable if escape_mode triggers correctly, but as a fallback:
             print(f"{COLOR_YELLOW}You escaped the house, but without enough evidence, the truth about Bludworth and Death's Design remains hidden.{COLOR_RESET}")
             print(f"{COLOR_YELLOW}You feel a chill, wondering if your own time is borrowed...{COLOR_RESET}")
             print("\nGame Over? - Escaped, but the mystery lingers.")
        else:
             # Successful Escape
             print(f"{COLOR_GREEN}You make it across the porch just as the first wrecking ball impacts the upper floor!{COLOR_RESET}")
             print(f"{COLOR_GREEN}You sprint away from the collapsing house, clutching the evidence.{COLOR_RESET}")
             print(f"\nYou found {player['found_evidence']} pieces of evidence.")
             # Add score display or other success metrics if desired
             print(f"{COLOR_GREEN}\nCongratulations! You survived and have the proof! (Score: {player['score']}){COLOR_RESET}")

        return True # Game ends after reaching the porch in escape mode
    return False # Not in escape mode or not at the porch


def get_input():
    prompt = f"({player['location']} | Turns: {player['turns_left']}) > "
    return input(prompt).lower().split()

def move(command):
    if len(command) < 2:
        print("Go where?")
        return
    direction = command[1]
    current_room = player['location']
    if direction in rooms[current_room]['exits']:
        next_room = rooms[current_room]['exits'][direction]
        if next_room in rooms and rooms[next_room].get('locked'):
            # Check if the specific key needed is in inventory
            needed_key = None
            if next_room == "Attic Entrance": needed_key = "Attic Key"
            elif next_room == "Main Basement Area": needed_key = "Basement Key"
            elif next_room == "Storage Room": needed_key = "Storage Room Key"
            # Add other locked rooms and their keys here

            if needed_key and needed_key in player['inventory']:
                 print(f"{COLOR_RED}The way to {next_room} is locked, but you have the {needed_key}. Use 'unlock {direction}' or 'unlock {next_room}'.{COLOR_RESET}")
            else:
                 print(f"{COLOR_RED}That way ({next_room}) is locked.{COLOR_RESET}")
            # Don't change location or decrement turn if locked
            return False # No death occurred
        else:
            # Special message for Front Porch -> Foyer
            if current_room == "Front Porch" and next_room == "Foyer":
                print("The porch floorboards bend and snap under your feet as your weight leaves them. It feels like they could break at any second if any more weight had been applied.")
                print("You jump through the doorway to avoid breaking the patio floorboards. The heavy front door slams shut behind you, causing the crystal chandelier overhead to shudder violently. The cable anchoring the bourgeoise behemoth groans under the new momentum as the wind from the door causes it to sway in your direction.")
                # Potential Chandelier Hazard Trigger (Example - requires hazard system integration)
                if rooms["Foyer"].get('hazard') == "precarious object" and random.random() < 0.3: # Increased chance from slam
                    print(f"\n{COLOR_RED}{rooms['Foyer'].get('hazard_description', 'Something shifts violently overhead!')}{COLOR_RESET}") # Describe the object shifting
                    print(f"{COLOR_RED}The sudden slam of the door is too much! {rooms['Foyer'].get('hazard_death', 'It falls, crushing you!')}{COLOR_RESET}")
                    return True # Death

            player['location'] = next_room
            player['turns_left'] -= 1

            # Add Score for New Room
            if next_room not in player['visited_rooms']:
                player['visited_rooms'].add(next_room)
                player['score'] += 5 # Points for exploring
                print(f"{COLOR_GREEN}New room discovered! +5 points.{COLOR_RESET}") # Use Green for positive feedback

            # Add Success Message
            print(f"You move {direction} into the {COLOR_YELLOW}{next_room}{COLOR_RESET}.") # Highlight room name

            # Hazard Check on Entry (Requires hazard system integration)
            room_data = rooms[player['location']]
            if room_data.get('hazard'):
                hazard_type = room_data['hazard']
                hazard_info = room_data.get('hazard_info', {}) # Get full info if available
                hazard_chance = room_data.get('hazard_chance', 0)
                hazard_description = room_data.get('hazard_description', "It feels dangerous...")
                hazard_death_msg = room_data.get('hazard_death', "You trigger a deadly trap!")

                # Example: Check for weak floorboards on movement
                if hazard_type == "weak floorboards" and random.random() < hazard_chance:
                    print(f"\n{COLOR_RED}{hazard_description}{COLOR_RESET}")
                    print(f"{COLOR_RED}{hazard_death_msg}{COLOR_RESET}")
                    return True # Indicate death

                # Example: Check for precarious object on movement (vibration)
                elif hazard_type == "precarious object" and random.random() < hazard_chance:
                     print(f"\n{COLOR_RED}{hazard_description}{COLOR_RESET}")
                     print(f"{COLOR_RED}{hazard_death_msg}{COLOR_RESET}")
                     return True # Indicate death

                # Add checks for other hazards triggered *purely* by entering, if any

    else:
        print("You can't go that way.")

    # Adjust hazard chances as the game progresses
    turns_elapsed = player['turns_left'] - 45  # Assuming starting turns is 45
    if turns_elapsed > 30:  # Later in the game
        # Increase hazard chances
        for room_name, room_data in rooms.items():
            if 'hazard_chance' in room_data:
                room_data['hazard_chance'] *= 1.5  # 50% more dangerous

    return False # No death occurred if execution reaches here

def apply_status_effect(effect_name, duration):
    """Apply a status effect to the player."""
    player.setdefault('status_effects', {})
    player['status_effects'][effect_name] = duration
    
    if effect_name == "injured":
        print(f"{COLOR_RED}You've been injured! Movement will be more difficult.{COLOR_RESET}")
    elif effect_name == "disoriented":
        print(f"{COLOR_YELLOW}You feel disoriented. Your vision swims and directions seem confusing.{COLOR_RESET}")
    elif effect_name == "panicked":
        print(f"{COLOR_MAGENTA}Your heart races as panic takes hold. Time seems to be moving faster.{COLOR_RESET}")

def process_status_effects():
    """Process active status effects at the start of each turn."""
    if 'status_effects' not in player:
        player['status_effects'] = {} # Initialize if it doesn't exist
        return

    effects_to_remove = []
    for effect, turns_left in player['status_effects'].items():
        # Reduce duration
        player['status_effects'][effect] -= 1

        # Apply effect for this turn
        if effect == "injured":
            # 20% chance to lose extra turn from pain when moving
            if random.random() < 0.2 and player.get('last_command_type') == 'go':
                print(f"{COLOR_RED}Pain shoots through your body, slowing you down.{COLOR_RESET}")
                player['turns_left'] -= 1
        elif effect == "panicked":
            # 30% chance to lose extra turn due to panic
            if random.random() < 0.3:
                print(f"{COLOR_MAGENTA}Your panic makes time seem to slip away faster.{COLOR_RESET}")
                player['turns_left'] -= 1

        # Check if effect has expired
        if player['status_effects'][effect] <= 0:
            effects_to_remove.append(effect)
            print(f"Your {effect} condition has improved.")

    # Remove expired effects
    for effect in effects_to_remove:
        del player['status_effects'][effect]

def process_player_input(command):
    """Parses player input and calls the appropriate action function."""
    continue_game = True
    action_taken = False  # Did the player attempt a valid action type?
    death_occurred = False  # Did the action result in death?

    if not command:
        print("Please enter a command.")
        return continue_game, action_taken, death_occurred  # No action taken, no death

    verb = command[0].lower()
    action_taken = True  # Assume an action was attempted if input is not empty

    if verb == "go":
        death_occurred = move(command)
    elif verb == "examine":
        death_occurred = examine(command)
    elif verb == "take":
        death_occurred = take(command)  # Now returns death status
    elif verb == "drop":
        death_occurred = drop(command)  # Now returns death status
    elif verb == "use":
        death_occurred = use_item(command)
    elif verb == "unlock":
        death_occurred = unlock(command)  # Now returns death status
    elif verb == "search" or verb == "look":  # Allow 'look in' as alias for 'search in'
        if len(command) > 1 and command[1].lower() == 'in':
            death_occurred = search(command)  # search already returns death status
        else:
            print("Look where? Or 'look in [container]'?")
            action_taken = False  # Invalid syntax for 'look'
            player['turns_left'] -= 1  # Penalize turn for bad command
    elif verb == "inventory" or verb == "i":
        inventory_str = ", ".join([f"{COLOR_YELLOW}{item}{COLOR_RESET}" for item in player['inventory']]) if player['inventory'] else "Empty"
        print(f"Inventory: {inventory_str}")
        action_taken = False  # Viewing inventory doesn't count as taking a turn or a risk
    elif verb == "list" or verb == "help":
        print("Available commands: go [direction], examine [object/item], take [item], drop [key], use [item] on [object], search in [container], unlock [exit/room], inventory, list, quit, evidence")
        action_taken = False  # Listing commands doesn't count as taking a turn or a risk
    elif verb == "quit":
        print("Are you sure you want to quit? (yes/no)")
        confirm = input("> ").lower()
        if confirm == 'yes':
            continue_game = False
        action_taken = False  # Quitting confirmation doesn't count as taking a turn or a risk
    elif verb == "evidence":
        review_evidence()
        action_taken = False  # Doesn't count as taking a turn
    else:
        print(f"Unknown command: '{verb}'")
        action_taken = False  # Invalid command
        player['turns_left'] -= 1  # Penalize turn for bad command

    return continue_game, action_taken, death_occurred
    
def examine(command: list[str]) -> bool:
    global sink_interactions, crate_interactions, stairs_interactions, bookshelves_interactions # Add new counters

    if len(command) < 2:
        print("Examine what?")
        return False # Return False as no death occurred
    item = " ".join(command[1:])
    current_room = player['location']
    room_data = rooms[current_room] # Get current room data
    specific_interaction = False # Flag to track if a specific interaction occurred
    death_occurred = False # Flag for death this turn

    # --- Hazard Check Before Specific Interactions ---
    hazard_type = room_data.get('hazard')
    hazard_info = room_data.get('hazard_info', {})
    hazard_chance = room_data.get('hazard_chance', 0)

    # Check for faulty wiring when examining specific objects (e.g., sink)
    if hazard_type == "faulty wiring" and item.lower() == "sink" and current_room == "Kitchen":
        specific_interaction = True
        print("You reach towards the sink, noticing the crackling wires nearby...")
        if random.random() < hazard_chance:
            print(hazard_info.get('death_message', "You touch a live wire!"))
            death_occurred = True
        else:
            print("You pull your hand back just in time. That was close!")
            # Add player thought for near miss
            print(f"{COLOR_YELLOW}Your heart pounds. That could have been bad.{COLOR_RESET}")
            player['turns_left'] -= 1 # Penalize for close call

    # Stairs Interaction (General - will be refined below for specific room)
    elif item.lower() == "stairs":
        specific_interaction = True
        stairs_interactions += 1
        if stairs_interactions == 1:
            print("You examine the creaking wooden stairs. They look old and somewhat unstable.")
        elif stairs_interactions == 2:
            print("You cautiously put some weight on the top step. It groans in protest. Some steps look particularly worn.")
            # Mark stairs as weakened for future interactions
            update_room_state(current_room, "weakened_stairs") # Assuming this function exists
        else: # Third interaction
            print("You test the stairs more firmly...")
            death_chance_multiplier = 2.0

            if room_data.get('hazard') == 'weak floorboards': # If the stairs themselves are the hazard
                if random.random() < room_data.get('hazard_chance', 0.25) * death_chance_multiplier:
                    print(f"{COLOR_RED}The stairs finally give way under your testing!{COLOR_RESET}")
                    print(f"{COLOR_RED}You tumble down, potentially injured.{COLOR_RESET}") # More generic message
                    death_occurred = True # Consider making this a chance of injury instead?
                else:
                    print(f"{COLOR_RED}The stairs groan alarmingly but hold for now. This is extremely dangerous.{COLOR_RESET}")
            else: # Generic risk
                if random.random() < 0.2:
                    print(f"{COLOR_YELLOW}A step cracks loudly! You quickly pull back, avoiding disaster.{COLOR_RESET}")
                    # Apply disoriented status effect from the close call
                    apply_status_effect("disoriented", 2) # Assuming this function exists
                else:
                    print("...They creak loudly but seem to hold. Still, caution is advised.")
        if not death_occurred:
            player['turns_left'] -= 1

    # Check for unstable shelf when examining shelves or bookshelves
    elif hazard_type == "unstable shelf" and (item.lower() == "shelves" or item.lower() == "bookshelves"):
        specific_interaction = True
        target_name = "shelves" if item.lower() == "shelves" else "bookshelves"
        print(f"You examine the {target_name}, laden with dusty objects. They groan under the weight...")
        if random.random() < hazard_chance:
            print(hazard_info.get('death_message', f"The {target_name} collapse!"))
            death_occurred = True
        else:
            print(f"The {target_name} wobble precariously, but hold for now.")
            player['turns_left'] -= 1 # Decrement turn for interaction
            player['score'] += 3 # Assuming score is defined

    # Check for gas leak interaction (e.g., examining sink with faulty wiring nearby)
    elif hazard_type == "gas leak" and item.lower() == "sink" and current_room == "Kitchen":
        specific_interaction = True
        print("You examine the sink, the smell of gas thick in the air. You notice sparking wires nearby...")
        # Increased chance if wiring is also faulty
        combined_chance = hazard_info.get('trigger_chance', 0.2)
        if rooms[current_room].get('hazard') == 'faulty wiring':
            combined_chance *= 1.5 # Make ignition more likely if both hazards present

        if random.random() < combined_chance:
            print(hazard_info.get('death_message', "The gas ignites!"))
            death_occurred = True
        else:
            print("Sparks fly near the sink, but miraculously don't ignite the gas... yet.")
            player['turns_left'] -= 1

    # Check for weak floorboards when examining heavy objects near them
    elif hazard_type == "weak floorboards" and item.lower() in ["workbench", "shelves", "bed", "desk", "bookshelves"]: # Add relevant heavy objects
        specific_interaction = True
        print(f"You lean closer to examine the {item}. The floorboards beneath you creak ominously...")
        if random.random() < hazard_chance * 0.5: # Lower chance than direct movement, but still possible
            print(hazard_info.get('death_message', "The floor gives way!"))
            death_occurred = True
        else:
            print("The floor holds, but it felt disturbingly weak.")
            player['turns_left'] -= 1


    # --- Existing specific interaction checks (Refined) ---
    if not death_occurred:
        # Sink Interaction
        if item.lower() == "sink" and current_room == "Kitchen" and not specific_interaction:
            sink_interactions += 1
            specific_interaction = True
            if sink_interactions == 1:
                print("You examine the grimy sink. You notice some exposed wiring nearby and a faint smell of gas. Better be careful.")
            elif sink_interactions == 2:
                print("Looking closer at the sink, the wiring sparks intermittently. The gas smell is stronger. This feels dangerous.")
            else: # Third time's the charm?
                print("You tempt fate near the sink again. The wiring crackles violently...")
                death_chance_multiplier = 2.0 # Base multiplier for tempting fate

                if room_data.get('hazard') == 'gas leak':
                    death_chance_multiplier = 3.0 # Higher chance for ignition
                    if random.random() < room_data.get('hazard_chance', 0.2) * death_chance_multiplier:
                        print(f"{COLOR_RED}...igniting the gas filling the room!{COLOR_RESET}")
                        print(f"{COLOR_RED}{room_data.get('hazard_death', 'The kitchen explodes in a devastating fireball!')}!{COLOR_RESET}")
                        death_occurred = True
                    else:
                        print("...Sparks fly, but the gas doesn't ignite. Your luck is unbelievable.")

                elif room_data.get('hazard') == 'faulty wiring':
                    death_chance_multiplier = 2.5 # Higher chance for electrocution
                    if random.random() < room_data.get('hazard_chance', 0.15) * death_chance_multiplier:
                        print(f"{COLOR_RED}{room_data.get('hazard_death', 'You touch the sink and a lethal current surges through your body!')}!{COLOR_RESET}")
                        death_occurred = True
                    else:
                        print("...A strong shock jolts you, but you survive. Seriously, stop it.")

                else:
                    print("...but nothing happens this time. You really need to stop doing that.")

            if not death_occurred:
                player['turns_left'] -= 1

        # Bookshelves Interaction
        elif item.lower() == "bookshelves" and current_room == "Library" and not specific_interaction:
            bookshelves_interactions += 1
            specific_interaction = True
            if bookshelves_interactions == 1:
                print("You examine the towering bookshelves. They seem old and overloaded, leaning slightly.")
            elif bookshelves_interactions == 2:
                print("Running your hand along a shelf, you feel it shift noticeably. Dust rains down. One book looks particularly loose.")

                # Small chance to find evidence hidden in the books
                if random.random() < 0.3:
                    for evidence_name, evidence_info in evidence.items():
                        if evidence_info.get('location') == current_room and evidence_info.get('container') == "bookshelves" and not evidence_info.get('found'):
                            print(f"{COLOR_YELLOW}A book shifts, revealing something hidden behind it...{COLOR_RESET}")
                            room_data.setdefault('revealed_items', []).append(evidence_name)
                            break
            else: # Third interaction
                print("You lean against the bookshelves carelessly...")
                death_chance_multiplier = 2.5 # Increased chance for leaning

                if room_data.get('hazard') == 'unstable shelf':
                    if random.random() < room_data.get('hazard_chance', 0.1) * death_chance_multiplier:
                        print(f"{COLOR_RED}{room_data.get('hazard_death', 'The shelves give way, burying you under an avalanche of heavy books and splintered wood!')}!{COLOR_RESET}")
                        death_occurred = True
                    else:
                        print(f"{COLOR_YELLOW}The shelves groan loudly and shift, but remain standing. That was incredibly foolish.{COLOR_RESET}")
                else: # No specific hazard, but still risky
                    if random.random() < 0.15: # Base chance of collapse from leaning
                        print(f"{COLOR_RED}The old wood groans and splinters... the entire structure collapses on top of you!{COLOR_RESET}")
                        death_occurred = True
                    else:
                        print(f"{COLOR_YELLOW}...they hold your weight, creaking ominously. Probably not a good idea to do that again.{COLOR_RESET}")
            if not death_occurred:
                player['turns_left'] -= 1

        # Crate Interaction (Attic)
        elif item.lower() == "crate" and current_room == "Attic" and not specific_interaction:
            crate_interactions += 1
            specific_interaction = True
            if crate_interactions == 1:
                print("You examine the sturdy wooden crate. It looks like it might contain stored items. A newspaper clipping is pinned to the side.")
            elif crate_interactions == 2:
                print("You tap on the crate. It sounds mostly hollow, but something shifts inside. The wood seems brittle in places.")

                # Chance to reveal the newspaper clipping
                if "Newspaper Clipping" in evidence and evidence["Newspaper Clipping"]["location"] == current_room and "Newspaper Clipping" not in room_data.get('revealed_items', []):
                    print(f"{COLOR_YELLOW}The newspaper clipping on the side becomes more readable now.{COLOR_RESET}")
                    room_data.setdefault('revealed_items', []).append("Newspaper Clipping")
            else: # Third interaction
                print("You try to shift the heavy crate...")
                death_chance_multiplier = 1.5

                if room_data.get('hazard') == 'precarious object': # e.g., something stored ON the crate
                    if random.random() < room_data.get('hazard_chance', 0.1) * death_chance_multiplier:
                        print(f"{COLOR_RED}...dislodging something resting on top! {room_data.get('hazard_death', 'It falls and crushes you!')}!{COLOR_RESET}")
                        death_occurred = True
                    else:
                        print(f"{COLOR_YELLOW}...something wobbles precariously on top, but settles back down. Careful!{COLOR_RESET}")
                elif room_data.get('hazard') == 'weak floorboards':
                    if random.random() < room_data.get('hazard_chance', 0.25) * death_chance_multiplier:
                        print(f"{COLOR_RED}...The movement is too much for the rotten floorboards beneath! {room_data.get('hazard_death', 'The floor gives way!')}!{COLOR_RESET}")
                        death_occurred = True
                    else:
                        print(f"{COLOR_YELLOW}...The floorboards groan loudly under the combined weight, but hold.{COLOR_RESET}")
                else: # Generic risk
                    if random.random() < 0.1:
                        print(f"{COLOR_MAGENTA}...As you push it, your hand slips through a rotten plank! A sharp splinter embeds itself deep in your arm. The shock and pain are intense...{COLOR_RESET}")
                        # Apply injured status effect
                        apply_status_effect("injured", 3) # Assuming this function exists
                        print("You pull your hand back, wincing. That hurt.")
                    else:
                        print("...It scrapes loudly across the floor but doesn't reveal anything new.")
            if not death_occurred:
                player['turns_left'] -= 1

    # --- Generic Object Examination ---
    if not specific_interaction and not death_occurred:
        object_found = False
        # Add specific descriptions for previously unhandled objects
        examine_messages = {
            "dusty table": "A simple wooden table covered in a thick layer of dust. Looks like it hasn't been touched in years.",
            "dining table": "A long mahogany table, scarred and faded. Ghostly outlines in the dust suggest where plates once sat.",
            "cupboard": "A tall wooden cupboard, its doors slightly warped. A faint, musty smell emanates from within.",
            "fireplace": f"A large, cold fireplace, stained black with soot. {'One brick near the bottom looks loose.' if not room_data.get('fireplace_brick_removed') else 'The cavity where a brick used to be is dark and full of loose mortar.'}", # Hint added/updated
            "sink": "A grimy kitchen sink. You notice some exposed wiring nearby and a faint smell of gas.", # Hint added
            "broken plates": "Shards of cheap ceramic litter the floor, crunching underfoot if you're not careful.",
            "boarded window": "Heavy wooden planks cover the window frame, nailed securely. No light gets through.",
            "bookshelves": "Tall, imposing bookshelves filled with dusty, decaying books. They seem overloaded.", # Hint added
            "desk": "An old wooden desk. Its surface might hold clues or just clutter, depending on the room.",
            "bed": "A bed, either simple or grand, showing signs of age. The mattress is stained and torn.",
            "mirror": "A cracked mirror hanging precariously. Your reflection looks distorted and uneasy.",
            "medicine cabinet": "A small metal cabinet, rusted at the hinges, hanging slightly open. Looks empty from here.",
            "crate": "A sturdy wooden crate, possibly containing stored items. A newspaper clipping is pinned to the side.", # Hint added
            "workbench": "A solid workbench covered in old, rusty tools and layers of dust. Might be useful things here.", # Hint added
            "shelves": "Wooden shelves lined with dusty jars and forgotten equipment. They look ready to collapse.", # Hint added
            "nightstand": "A small table beside the bed, likely for personal items. Its drawer is slightly ajar.",
            "ceiling fan with chains": "An old ceiling fan hangs overhead, coated in dust. Two chains dangle from it, one likely for the light, one for the fan.", # Description added
            "toy red suv": "A small, plastic red SUV toy car. It looks like it's seen better days.", # Description added
            "strange diagrams": "Sheets of paper covered in complex, unsettling diagrams and equations. They don't make immediate sense.", # Description added
            "camera": "An older model camera rests on the desk, a layer of dust covering its lens.", # Description added
            "broken window": "The window frame is shattered, glass shards litter the floor nearby. Cold air blows through.", # For after using brick
            "broken crate": "Splintered remains of a wooden crate lie on the floor.", # For after using brick
            "back door": "A sturdy wooden back door. It looks like it leads outside.", # Description for the opened back door
            "dusty table": "A simple wooden table covered in a thick layer of dust. Looks like it hasn't been touched in years.",
            "dining table": "A long mahogany table, scarred and faded. Ghostly outlines in the dust suggest where plates once sat.",
            "cupboard": "A tall wooden cupboard, its doors slightly warped. A faint, musty smell emanates from within.",
            "fireplace": lambda room_data: f"A large, cold fireplace, stained black with soot. {'One brick near the bottom looks loose.' if not room_data.get('fireplace_brick_removed') else 'The cavity where a brick used to be is dark and full of loose mortar.'}", # Dynamic message
            "sink": "A grimy kitchen sink. You notice some exposed wiring nearby and a faint smell of gas.", # Hint added
            "broken plates": "Shards of cheap ceramic litter the floor, crunching underfoot if you're not careful.",
            "boarded window": "Heavy wooden planks cover the window frame, nailed securely. No light gets through.",
            "bookshelves": "Tall, imposing bookshelves filled with dusty, decaying books. They seem overloaded.", # Hint added
            "desk": "An old wooden desk. Its surface might hold clues or just clutter, depending on the room.",
            "bed": "A bed, either simple or grand, showing signs of age. The mattress is stained and torn.",
            "mirror": "A cracked mirror hanging precariously. Your reflection looks distorted and uneasy.",
            "medicine cabinet": "A small metal cabinet, rusted at the hinges, hanging slightly open. Looks empty from here.",
            "crate": "A sturdy wooden crate, possibly containing stored items. A newspaper clipping is pinned to the side.", # Hint added
            "workbench": "A solid workbench covered in old, rusty tools and layers of dust. Might be useful things here.", # Hint added
            "shelves": "Wooden shelves lined with dusty jars and forgotten equipment. They look ready to collapse.", # Hint added
            "nightstand": "A small table beside the bed, likely for personal items. Its drawer is slightly ajar.",
            "ceiling fan with chains": "An old ceiling fan hangs overhead, coated in dust. Two chains dangle from it, one likely for the light, one for the fan.", # Description added
            "toy red suv": "A small, plastic red SUV toy car. It looks like it's seen better days.", # Description added
            "strange diagrams": "Sheets of paper covered in complex, unsettling diagrams and equations. They don't make immediate sense.", # Description added
            "camera": "An older model camera rests on the desk, a layer of dust covering its lens.", # Description added
            "broken window": "The window frame is shattered, glass shards litter the floor nearby. Cold air blows through.", # For after using brick
            "broken crate": "Splintered remains of a wooden crate lie on the floor.", # For after using brick
            "back door": "A sturdy wooden back door. It looks like it leads outside.", # Description for the opened back door
            "Photo of Jess Golden": "Writing on back: Survived a club collapse but disappeared shortly after; her ultimate fate is unknown.",
            "Motorcycle Debris": "Piece of metal from a motorcycle crash that immolated Sebastian Lebecque after he escaped a club collapse.",
            "Photo of Patti Fuller at Circuit City": "Writing on back: Implied to have died during an incident at Circuit City after surviving a subway bombing.",
            "Photo of Will Sax at Circuit City": "Writing on back: Implied to have died during an incident at Circuit City after surviving a subway bombing.",
            "Shard of Glass": "Sharp piece of glass from a falling pane that sliced Zack Halloran in half after he survived a subway bombing.",
            "Bloody Hubcap": "A blood-stained Ferrari hubcap that decapitated Al Kinsey after he survived a subway bombing.",
            "Dented Motorcycle Helmet": "Hal Ward's helmet, found with his body after he drowned in a flash flood following his survival of a subway bombing.",
            "Charred Metal Pail": "A burnt metal pail that exploded after its contents came in contact with a live spark, killing Susan Frie. She had previously survived a subway bombing.",
            "Rusty Blade": "A rusty knife, likely used by the Ripper (Bill Sangster), who killed Juliet Collins after she survived an explosion.",
            "Photo of Bill Sangster": "Writing on back: Survived an explosion, did not survive being crushed by drawbridge gears. Later identified as the infamous Whitechapel Ripper. His final fate is unknown.",
            "Piece of Corroded Pipe": "A section of pipe involved in the fiery death of Matthew Upton, who survived an explosion.",
            "Small Cobra Figurine": "A small snake figurine, reminiscent of the cobras that killed Hector Barnes after he survived an explosion, following his interaction with an Egyptian sarcophagus.",
            "Hieroglyph Fragment": "A fragment with hieroglyphs, linked to an Egyptian sarcophagus that brought about the death by snakes of Mrs Stanley after she survived an explosion.",
            "Photo of Andrew Caine": "Writing on back: Survived an explosion. His subsequent fate is unknown.",
            "Shattered Glass Shards": "Fragments of glass jars from a hospital, linked to the death of Stewart Tubbs by inhaling noxious vapors after he survived an explosion.",
            "Bloody Earbuds": "Aldis Escobar died in a fiery car crash on Las Vegas Boulevard after his near-death experience in an elevator. He was listening to music on his iPod at the time.",
            "Bloody Razor Blade": "Arlen Ploog bled to death after being attacked by Tina with a razor blade.",
            "Photo of Danny Larriva": "Photo with writing on the back: Danny Larriva was a ten-year-old boy beaten to death, likely by his mother's boyfriend, Roberto Diaz.",
            "Photo of Roberto Diaz": "Photo with writing on the back: Roberto Diaz was shot and then electrocuted by falling power lines after killing Danny Larriva.",
            "Costume Feather": "Shawna Engels, a dancer, was killed by a panther that got loose backstage during a show.",
            "Tom Gaines' Wedding Ring": "Tom Gaines was crushed to death by other passengers in a falling elevator.",
            "Allie Goodwin-Gaines' Wedding Ring": "Allie Goodwin-Gaines was crushed by the falling elevator after surviving the initial plunge.",
            "Warren Ackerman's Police Badge": "Detective Warren Ackerman was electrocuted by falling power lines after shooting Roberto Diaz.",
            "Piece of Traffic Light": "Officer Sean Murphy was decapitated by a falling traffic light in a van crash.",
            "Photo of Fred Newton": "Photo with writing on the back: Fred Newton fell to his death from a malfunctioning elevator.",
            "Photo of Ethel Newton": "Photo with writing on the back: Ethel Newton fell to his death from a malfunctioning elevator.",
            "Bullet Casing": "Macy, a waitress who survived the club, was later killed by a falling metal panel dislodged by a bullet from Ben's gun. This casing is from the fatal shot.",
            "Photo of Stairs": "Eric, who survived the club collapse, later died by breaking his neck in a fall down stairs at the hospital. This photo represents the location of his death.",
            "Spent Bullet Casing": "Ben, who survived the club collapse, accidentally shot himself in the head with his own gun while fleeing the police. This spent casing was the cause of his death.",
            "Medical Chart Spike": "Jamie, a band member who survived the club, later died at the morgue when he was impaled by a falling medical chart spike. This spike is the object that killed him.",
            "Photo of Jack Curtis": "Photo with writing on back describing how Jack Curtis was shot by Officer Beriev after the events in the precinct.",
            "Photo of Lonnie": "Photo with writing on back describing Lonnie's miraculous survival of a thirteen-story fall after snagging on a phone wire, sustaining severe injuries.",
            "Small Piece of Blood-Stained Fabric": "Small piece of fabric stained with blood from the knife attack Amy Tom survived in the alley.",
            "Spent Bullet Casing 2": "A spent bullet casing from Officer Beriev's gun when he shot Jack Curtis in the aftermath of the precinct events.",
            "Piece of Serrated Knife Blade": "A small, sharp piece of the serrated knife blade used by the man in the hood before he was shot and killed by Jack Curtis.",
            "Photo of Chelsea Cox": "Photo with writing on back describing Chelsea Cox's death when she was hit in the eyes by falling icicles after escaping death's initial design.",
            "Crumpled Metal Shard": "A small piece of twisted metal from Dawson Donahue's exploding car, detailing how the car then crushed him against a wall after he survived a garage fire.",
            "Burnt Fabric Piece": "A small, burnt piece of fabric from Katie Astin's clothes after she was electrocuted by a fallen lighting rig, detailing her survival of earlier 'accidents'.",
            "Shattered Record Shard": "A sharp shard from Joshua Cornell III's platinum record, detailing how it decapitated him after he survived falling stereo equipment.",
            "Glass Bottle Neck Shard": "A sharp piece of the glass bottle neck that was shot into Dominique Swann's mouth after she survived choking on a nut.",
            "Bloody Scalpel": "Survived a train crash, but died later in the hospital due to injuries exacerbated by falling surgical instruments and a bath.",
            "Charred Matchbook": "Survived a train crash but died later, trapped in a restaurant fire.",
            "Shattered Umbrella Spoke": "Survived a train crash but died later, impaled by umbrellas after being launched through a store window.",
            "Piece of Tow Cable": "Survived a train crash but died later, launched by a tow truck and impaled by umbrellas in a store.",
            "Bloody Chainsaw Fragment": "Survived a train crash but died later, killed by falling scaffolding and a chainsaw.",
            "Rusty Faucet Handle": "Died in a hospital, scalded in a bath.",
            "Bloody Corkscrew": "Survived a train crash but died later, impaled in the eye with a corkscrew in Central Park.",
            "Bottle of Acetic Acid": "A small bottle of acetic acid, spilled near potassium ferricyanide, created deadly fumes that ended Chablis's life in a locked darkroom.",
            "Section of Braided Hair Extension": "A piece of braided hair extension, tragically caught in spinning rims during a music video shoot, leading to Shiraz's violent death.",
            "Toy Laundry Truck": "A miniature laundry truck, a reminder of the vehicle that fatefully struck Gunter, severing his body.",
            "Broken Cigarette Holder": "Merlot's elegant cigarette holder, found broken amidst the chaos of the sinking ship, hinting at her final, trampled moments.",
            "Piece of Seaweed": "A piece of seaweed, tangled around Carlo's retrieved body, a morbid souvenir of his drowning after the ship's demise.",
            "Miniature Buffet Table Piece": "A small piece from a miniature buffet table, crushing Rose against a bulkhead during the ship's violent tilt.",
            "Photo of Sherry": "A photo of Sherry. On the back, a chilling note describes her death after escaping the ship, tragically struck by a bus.",
            "Brick": "A dirty brick, one corner covered with dried blood, hair and gore. This was the brick that killed Alex Browning; he survived the plane crash and was being hunted by Death, narrowly escaping its design multiple times. If HE didn't make it...",
            "Retractable Clothesline Piece": "A piece of a retractable clothesline. Tod died when he slipped in his bathroom and accidentally hanged himself with the clothesline.",
            "Photo of Clear Rivers": "A photo of Clear. Writing on the back describes her survival of the plane crash and her understanding that Death is coming for the survivors. She is actively trying to evade it.",
            "Light Bulb": "A light bulb from a large sign. Carter was killed when a falling sign crushed him.",
            "Miniature Toy Bus": "A miniature model of a bus. Terry was tragically struck and killed by a speeding bus.",
            "Charred Mug": "A burnt and broken ceramic mug. Ms. Lewton died in a house fire (ahem..explosion) caused by a series of unfortunate accidents.",
            "Bloody Piece of Metal": "A jagged piece of metal, stained with what appears to be blood. Billy was decapitated by a piece of metal flung from a train.",
            "Navel Piercing with Crystal": "A small navel piercing with a dangling crystal, belonging to Carrie Dreyer. She died in the Devil's Flight roller coaster crash.",
            "Mud Flap Girl Necklace": "A cheap, chrome silhouette of a mud flap girl on a chain, won by Franklin Cheeks. The back of his head was (mostly) removed by a radiator fan after surviving the roller coaster crash.",
            "Fuzzy Red Dice": "A pair of fuzzy red dice, similar to those in Rory Peters' car. He died by being sliced into several chunks by wire fencing after surviving the route 23 pile-up.",
            "Cigarette": "A cigarette, like the ones smoked by Kat Jennings. She died when her car's airbag deployed, impaling her head on a pipe after surviving the route 23 pile-up.",
            "Pool Ball Keychain": "An orange striped pool ball keychain, the kind Eugene Dix owned. He died by accidental incineration in Lakeview Hospital along with Clear Rivers after surviving the route 23 pile-up.",
            "Valium Pills": "A bottle of Valium pills, like those taken by Nora Carpenter. She died when her head was pulled off by an elevator after surviving the route 23 pile-up.",
            "Empty Water Bottle": "An empty water bottle, like those Tim Carpenter used as drumsticks. He died being crushed by a falling plate glass window at a dentist's office after surviving the route 23 pile-up.",
            "Nipple Ring": "A nipple ring, like the one worn by Evan Lewis. He died after being impaled through the facial by a fire ladder after surviving the route 23 pile-up.",
            "Roxy Duffle Bag": "A Roxy brand duffle bag, belonging to Shaina Gordon. She died in the route 23 pile-up.",
            "Plastic Bag of Weed": "A small plastic bag containing weed, like the one Dano Royale had. He died in the route 23 pile-up.",
            "White Rose": "A white rose, similar to those in Isabella Hudson's van for a memorial service. She survived the route 23 pile-up and Death's design by giving birth to her baby.",
            "Work Gloves": "A pair of work gloves, worn by Brian Gibbons. He died in an explosion caused by a barbeque grill and propane tank after surviving the Lakeview Apartments fire and a secondary attempt on his life by a news van.",
            "Newspaper Clipping about Flight 180": "A newspaper clipping detailing the Flight 180 disaster and the subsequent deaths of the survivors. Clear Rivers, a survivor of Flight 180, died from gas in a hospital after helping the route 23 pile-up survivors.",
            "Photo of Jason on Devil's Flight": "A photo of Jason Wise on the Devil's Flight roller coaster. He died in the roller coaster crash.",
            "Overexposed Photo of Kevin": "An overexposed photo of Kevin Fischer. He survived the roller coaster crash but died later in a subway crash.",
            "Photo of Lewis from Ring-The-Bell Game": "A photo of Lewis Romero at the Ring-The-Bell game, where he knocked off the bell. He survived the roller coaster crash but died later by being crushed by weights.",
            "Photo of Ashley and Ashlyn at Clown Shoot": "A photo of Ashley Freund and Ashlyn Halperin at the clown shoot game. They survived the roller coaster crash but died later in a tanning bed accident.",
            "Photo of Ian with Banners": "A photo of Ian McKinley with banners in the background that look like teeth. He survived the roller coaster crash but died later by being crushed by a falling sign and cherry picker basket.",
            "Strip of nails": "A strip of collated nails, the type used in a nail gun. Several are missing, and traces of blood suggest they were forcibly removed. It's a chilling reminder of Erin Ulmer's gruesome demise.",
            "Camera": "An older digital camera used by Wendy Christensen to capture several ominous photographs hinting at the deaths of her classmates. She survived the Devil's Flight roller coaster malfunction and subsequent attempt on her life by Ian McKinley only to be killed in a subway crash several months later.",
            "Photo of Julie giving the finger": "A photo of Julie Christensen giving the finger for the yearbook. She survived the Devil's Flight roller coaster premonition.",
            "Photo of Perry": "A photo of Perry Malinowski. She survived the Devil's Flight roller coaster premonition but died later at the fair.",
            "Photo of Amber": "A photo of Amber Regan. She survived the Devil's Flight roller coaster premonition.",
            "Toy SUV": "A photo of Kimberly Corman. She survived the route 23 pile-up premonition and confronted Death at the lake.",
            "Photo of Officer Burke": "A photo of Officer Thomas Burke. He survived the route 23 pile-up premonition.",
            "Photo of Frankie": "A photo of Frankie Arnold. He died in the route 23 pile-up.",
            "Newspaper Clipping": "A newspaper clipping with a headline about a major disaster.", # Modified entry
        }

        for room_object in room_data.get('objects', []):
            if item.lower() == room_object.lower():
                print(examine_messages.get(room_object, f"You look at the {room_object}. Nothing seems particularly special about it.")) # Use specific message or default
                object_found = True
                break # Found the object, stop looping

        if not object_found:
            # Check if it's a revealed item (key/evidence) the player is trying to examine
            revealed_items = room_data.get('revealed_items', [])
            examined_revealed = False
            for revealed_item_name in revealed_items:
                if item.lower() in revealed_item_name.lower():
                    # Check if it's evidence or a key
                    if revealed_item_name in evidence:
                        print(f"It's the '{revealed_item_name}'. Description: {evidence[revealed_item_name]['description']}")
                    elif revealed_item_name in keys:
                        print(f"It's the {revealed_item_name}. Looks like it unlocks something.")
                    else:
                        print(f"You look at the {revealed_item_name}.")
                    examined_revealed = True
                    break
            if not examined_revealed:
                print(f"You don't see a '{item}' here to examine.")

    # Only decrement turn if no specific interaction happened AND no death occurred
    if not specific_interaction and not death_occurred:
        player['turns_left'] -= 1

    return death_occurred

# Assume COLOR_RED, COLOR_YELLOW, player, rooms, evidence, random are defined elsewhere

def use_item(command):
    if len(command) < 4 or command[2].lower() != 'on':
        print("Use which item on what? (e.g., 'use brick on window')")
        player['turns_left'] -= 1
        return False

    item_to_use = command[1]
    target_object = " ".join(command[3:])
    current_room = player['location']
    room_data = rooms[current_room]

    # Canonical (case-insensitive) lookup
    canonical_item = find_canonical_name(item_to_use, player['inventory'])
    canonical_target = find_canonical_name(target_object, room_data.get('objects', []))

    death_occurred = False
    interaction_happened = False

    if not canonical_item:
        print(f"You don't have a {item_to_use}.")
        player['turns_left'] -= 1
        return False

    if not canonical_target:
        print(f"You don't see a {target_object} here to use the {item_to_use} on.")
        player['turns_left'] -= 1
        return False

    # --- Use Brick on Boarded Window ---
    if canonical_item.lower() == "brick" and canonical_target.lower() == "boarded window":
        if current_room == "Kitchen":
            print("You smash the heavy brick against the boarded-up window.")
            print("With a splintering crack, the boards break, revealing the outside... but also dislodging a loose gas pipe fitting near the window frame.")
            print(f"{COLOR_RED}Gas begins to hiss loudly into the room!{COLOR_RESET}")
            if "boarded window" in room_data['objects']:
                room_data['objects'].remove("boarded window")
            if "broken window" not in room_data['objects']:
                room_data['objects'].append("broken window")
            # Update room description to reflect broken window and gas
            rooms[current_room]['description'] = "The kitchen is a scene of chaotic disarray. Broken plates and scattered utensils cover the floor. The back door is heavily boarded up. You see a glint of metal near the sink. The window is smashed, and the smell of gas is strong."
            # Add or update hazard
            room_data['hazard'] = "gas leak"
            room_data['hazard_info'] = {
                "description": "The room is filling with gas from a broken pipe!",
                "death_message": "A spark ignites the gas, causing a massive explosion!",
                "trigger_chance": 0.2
            }
            room_data['hazard_description'] = room_data['hazard_info']['description']
            room_data['hazard_death'] = room_data['hazard_info']['death_message']
            room_data['hazard_chance'] = room_data['hazard_info']['trigger_chance']
            interaction_happened = True
            # Optional: Consider adding update_room_state(current_room, "broke_window") if you implement such a function

            # Check for chain reaction with faulty wiring
            if room_data.get('hazard') == "faulty wiring" or any('wiring' in obj.lower() for obj in room_data.get('objects', [])):
                print(f"{COLOR_RED}The exposed wiring near the gas leak creates an extremely dangerous situation!{COLOR_RESET}")
                if random.random() < 0.4:  # 40% chance of immediate disaster
                    death_occurred = trigger_chain_reaction(current_room, "gas_leak")
                    if death_occurred:
                        return True
        else:
            print("There's no boarded window here to use the brick on.")

    # --- Use Brick on Crate ---
    elif canonical_item.lower() == "brick" and canonical_target.lower() == "crate":
        if current_room == "Attic":
            print("You bring the heavy brick down hard on the wooden crate.")
            newspaper_name = "Newspaper Clipping"  # Assuming this is the correct name
            if newspaper_name in evidence and \
                    evidence[newspaper_name].get('location') == current_room and \
                    evidence[newspaper_name].get('container') == "crate" and \
                    newspaper_name not in room_data.get('revealed_items', []):
                print("The wood splinters and breaks apart. Pinned inside, you see a Newspaper Clipping!")
                room_data.setdefault('revealed_items', []).append(newspaper_name)
                if "crate" in room_data['objects']:
                    room_data['objects'].remove("crate")
                if "broken crate" not in room_data['objects']:
                    room_data['objects'].append("broken crate")
                rooms[current_room]['description'] = "The attic is filled with dusty boxes and forgotten relics, along with the remains of a smashed crate. You feel a strange presence here."
            else:
                print("The crate splinters, but there doesn't seem to be anything significant hidden inside its remains.")
                if "crate" in room_data['objects']:
                    room_data['objects'].remove("crate")
                if "broken crate" not in room_data['objects']:
                    room_data['objects'].append("broken crate")
                rooms[current_room]['description'] = "The attic is filled with dusty boxes and forgotten relics, along with the remains of a smashed crate. You feel a strange presence here."
            interaction_happened = True
        else:
            print("There's no crate here to use the brick on.")

    # --- Use Tools on Boarded Window ---
    elif canonical_item.lower() == "rusty tools" and canonical_target.lower() == "boarded window":
        if current_room == "Kitchen":
            print("You wedge the prybar from your toolset between the planks on the window.")
            print("With a screech of protesting nails and splintering wood, you manage to pry off the boards.")
            print(f"{COLOR_YELLOW}The window is now open, but the noise might attract attention... or worse.{COLOR_RESET}")
            if "boarded window" in room_data['objects']:
                room_data['objects'].remove("boarded window")
            if "broken window" not in room_data['objects']:
                room_data['objects'].append("broken window")
            rooms[current_room]['description'] = rooms[current_room]['description'].replace("There's also a boarded window.", "The window is broken open.")
            if room_data.get('hazard') == 'gas leak':
                print(f"{COLOR_RED}Opening the window creates a draft, swirling the gas... hopefully dispersing it.{COLOR_RESET}")
            interaction_happened = True
        else:
            print("There's no boarded window here to use the tools on.")

    # --- Use Tools on Boarded Door ---
    elif canonical_item.lower() == "rusty tools" and canonical_target.lower() == "boarded door":
        # Ensure 'boarded door' is added to the relevant room's objects list (e.g., Kitchen)
        if current_room == "Kitchen" and "boarded door" in room_data.get('objects', []):
            print("You use the prybar on the heavily boarded back door.")
            print("It takes considerable effort, but you manage to loosen and remove the planks.")
            print(f"{COLOR_YELLOW}The back door is now accessible, leading outside.{COLOR_RESET}")
            # Define the Backyard room if it doesn't exist
            if "Backyard" not in rooms:
                rooms["Backyard"] = {"description": "A small, overgrown backyard. The fence is broken in places. The back door leads inside.", "exits": {"inside": "Kitchen"}, "objects": ["broken fence"], "possible_containers": []}
            rooms[current_room]['exits']['outside'] = "Backyard"
            room_data['objects'].remove("boarded door")
            if "back door" not in room_data['objects']:  # Add 'back door' if not present
                room_data['objects'].append("back door")
            rooms[current_room]['description'] = rooms[current_room]['description'].replace("The back door is heavily boarded up.", "The back door stands open, leading outside.")
            interaction_happened = True
        else:
            print("There's no boarded door here to use the tools on.")

    # --- Use Chains on Ceiling Fan (Consolidated Logic) ---
    elif canonical_item.lower() == "chains" and canonical_target.lower() == "ceiling fan with chains":
        if current_room == "Master Bedroom":
            print("You reach up and pull one of the chains dangling from the ceiling fan.")
            # Combine effects from both snippets
            chain_effect = random.choice(["light", "fan", "stuck", "hazard", "hazard"])  # Weight hazard slightly more

            if chain_effect == "light":
                print("A dim light flickers on, casting long shadows across the room.")
                # Optional: Update room state or description

            elif chain_effect == "fan":
                print("With a groan, the dusty fan blades begin to turn slowly, stirring up clouds of dust.")
                # Chance for non-lethal scare (from snippet 1)
                if random.random() < 0.15:  # 15% chance looks loose
                    print("One of the fan blades looks dangerously loose...")
                    if random.random() < 0.3:  # 30% chance it detaches if loose (4.5% overall)
                        print("...and detaches, flying across the room like a guillotine! It narrowly misses your head!")
                        print(f"{COLOR_YELLOW}That was way too close!{COLOR_RESET}")
                    else:
                        print("...but it holds on. For now.")
                print("You cough as dust fills the air.")  # Flavor text

            elif chain_effect == "stuck":
                # Ominous crack message (from snippet 2)
                print("The chain seems stuck. You pull harder and hear an ominous crack from the ceiling.")

            elif chain_effect == "hazard":
                # Prioritize faulty wiring hazard if present (from snippet 1 logic)
                if room_data.get('hazard') == 'faulty wiring':
                    print("As you pull the chain, you hear a crackling sound from the fan's motor housing.")
                    # Check trigger chance from hazard_info if possible, else use default
                    hazard_chance = room_data.get('hazard_info', {}).get('trigger_chance', 0.15)
                    if random.random() < hazard_chance * 2.0:  # Increased chance for direct interaction
                        print("Sparks shower down! The faulty wiring ignites the motor!")
                        # Get death message from hazard_info if possible
                        death_msg = room_data.get('hazard_info', {}).get('death_message', "The fan explodes in a shower of sparks and burning plastic, electrocuting you!")
                        print(f"{COLOR_RED}{death_msg}{COLOR_RESET}")
                        death_occurred = True
                    else:
                        print("Sparks shower down, and you smell burning plastic, but it doesn't fully ignite. You quickly let go.")
                else:
                    # If no wiring hazard, use fan falling logic (from snippet 2 logic)
                    print("You pull the chain, and hear an ominous crack from the ceiling mount...")
                    if random.random() < 0.25:  # 25% chance fan falls
                        print(f"{COLOR_RED}With a sickening crack, the ceiling mount gives way!{COLOR_RESET}")
                        print(f"{COLOR_RED}The fan crashes down, its blades slicing through the air. You don't have time to move.{COLOR_RESET}")
                        death_occurred = True
                    else:  # 75% chance it holds
                        print("The fan wobbles dangerously but holds. That was close.")

            interaction_happened = True
        else:  # Not in Master Bedroom
            print("There's no ceiling fan with chains here.")

    # --- Add alias for pulling chains ---
    elif command[0].lower() == "pull" and ("chain" in command[1].lower() or "chains" in command[1].lower()):
        # Check if the fan object exists in the current room
        if any(obj.lower() == "ceiling fan with chains" for obj in room_data.get('objects', [])):
            # Redirect to the 'use chains on ceiling fan' logic
            # Ensure we pass a correctly formatted command list
            standardized_command = ["use", "chains", "on", "ceiling fan with chains"]
            return use_item(standardized_command)
        else:
            print("There are no chains here to pull.")
            # No turn cost for failed alias if it wasn't a valid 'use' command initially
            return False  # No death, no interaction

    # --- Default case if no specific interaction matched ---
    else:
        if not interaction_happened and not death_occurred:  # Check added
            print(f"You can't use the {item_to_use} on the {target_object} like that.")
        # Fall through to turn decrement below if no specific interaction happened

    # --- Decrement turn logic ---
    # Decrement turn if:
    # 1. A specific interaction happened successfully (and didn't cause death).
    # 2. The command failed basic checks (no item, no target).
    # 3. The command was valid syntax but the specific use wasn't implemented/matched ('else' block above).
    if not death_occurred:
        # If interaction_happened is True, a specific action occurred.
        # If item_to_use wasn't in inventory or target_exists was False, it failed early (handled return/turn cost already).
        # If it reached the final 'else', it means syntax was okay but no valid 'use' case matched.
        # So, decrement turn if an interaction happened OR if it reached the final 'else' block.
        if interaction_happened or (not interaction_happened and canonical_target and canonical_item):
            player['turns_left'] -= 1

    return death_occurred

def take(command):
    try:
        if len(command) < 2:
            print("Take what?")
            player['turns_left'] -= 1
            return False # Indicate no death

        item = " ".join(command[1:])
        current_room = player['location']
        room_data = rooms[current_room]
        item_taken = False
        points_awarded = 0
        death_occurred = False

        # --- Hazard Check: Taking unstable items ---
        if item.lower() == "book" and current_room == "Library" and room_data.get('hazard') == 'unstable shelf':
            print("You reach for a dusty book on the overloaded shelf...")
            hazard_chance = room_data.get('hazard_chance', 0.1)
            if random.random() < hazard_chance * 1.5: # Slightly increased chance when interacting
                print(room_data.get('hazard_death', "The shelf gives way under the slight shift!"))
                death_occurred = True
            else:
                print("The shelf groans ominously but holds. You snatch the book quickly.")
                player['turns_left'] -= 1
            return death_occurred # Return death status

        #--- Taking Keys ---
        for key_name, key_info in keys.items():
            if item.lower() == key_name.lower():
                # Check if the key is physically present and revealed in the current room
                if key_info.get('location') == current_room and key_name in room_data.get('revealed_items', []):
                    if key_name not in player['inventory']:
                        print(f"You take the {COLOR_YELLOW}{key_name}{COLOR_RESET}.")
                        player['inventory'].append(key_name)
                        # Remove from revealed items
                        if key_name in room_data.get('revealed_items', []):
                            room_data['revealed_items'].remove(key_name)
                        item_taken = True
                        points_awarded = 7
                        player['score'] += 7
                        break # Exit loop once key is taken
                    else:
                        print(f"You already have the {COLOR_YELLOW}{key_name}{COLOR_RESET}.")
                        player['turns_left'] -= 1 # Cost turn for trying to take again
                        return death_occurred # No death
                # Check if the key is in the room but not revealed
                elif key_info.get('location') == current_room:
                    print(f"You see the {COLOR_YELLOW}{key_name}{COLOR_RESET}, but you need to find it first (e.g., 'look in {key_info.get('container', 'container')}').")
                    player['turns_left'] -= 1 # Cost turn for trying to take unrevealed
                    return death_occurred # No death
                # If key is not in this room, continue checking other keys
                else:
                    continue

        # --- Taking Evidence ---
        if not item_taken: # Only check evidence if a key wasn't already taken
            for evidence_name, evidence_info in evidence.items():
                # Use 'in' for partial matches
                if item.lower() in evidence_name.lower():
                    # Check if present, revealed, and not found
                    if evidence_info.get('location') == current_room and \
                       evidence_name in room_data.get('revealed_items', []) and \
                       not evidence_info.get('found', False):
                        print(f"You take the {COLOR_YELLOW}{evidence_name}{COLOR_RESET}.")
                        evidence[evidence_name]['found'] = True
                        player['found_evidence'] += 1
                        player['score'] += 50
                        # Trigger escape mode
                        if player['found_evidence'] >= REQUIRED_EVIDENCE:
                            global escape_mode
                            escape_mode = True
                            print(f"\n{COLOR_RED}This last piece of evidence has made it clear: Death is actively stalking you! You need to escape before something happens to you!{COLOR_RESET}")
                        # Remove from revealed items
                        if evidence_name in room_data.get('revealed_items', []):
                            room_data['revealed_items'].remove(evidence_name)
                        item_taken = True
                        points_awarded = 50
                        print(f"{COLOR_GREEN}Evidence found! +{points_awarded} points.{COLOR_RESET}")
                        break # Exit evidence loop
                    # Check if in room but not revealed
                    elif evidence_info.get('location') == current_room and \
                         evidence_name not in room_data.get('revealed_items', []) and \
                         not evidence_info.get('found', False):
                        print(f"You suspect evidence like '{evidence_name}' might be here, but you need to find it first (e.g., 'look in {evidence_info.get('container', 'container')}').")
                        player['turns_left'] -= 1 # Cost turn for trying to take unrevealed
                        return death_occurred # No death
                    # Check if revealed but already found
                    elif evidence_info.get('location') == current_room and \
                         evidence_name in room_data.get('revealed_items', []) and \
                         evidence_info.get('found', False):
                        print(f"You already found the {COLOR_YELLOW}{evidence_name}{COLOR_RESET}.")
                        player['turns_left'] -= 1 # Cost turn for trying to take again
                        return death_occurred # No death
                    # If not relevant here, continue checking
                    else:
                        continue

        # --- Taking Other Items (Brick, Tools) ---
        if not item_taken:
            # --- Allow taking Brick if in Living Room and present in objects, revealed_items, or revealed from fireplace ---
            if item.lower() == "brick" and current_room == "Living Room":
                brick_in_objects = "Brick" in room_data.get('objects', [])
                brick_in_revealed = "Brick" in room_data.get('revealed_items', [])
                # Also allow if fireplace_brick_removed and Brick not in inventory
                brick_revealed_by_fireplace = room_data.get('fireplace_brick_removed', False) and "Brick" not in player['inventory']
                if (brick_in_objects or brick_in_revealed or brick_revealed_by_fireplace) and "Brick" not in player['inventory']:
                    print(f"You wiggle the loose {COLOR_YELLOW}Brick{COLOR_RESET} out of the fireplace. It feels heavy.")
                    print(f"{COLOR_MAGENTA}Removing the brick reveals a small, dark cavity and loosens some mortar. The structure above looks less stable...{COLOR_RESET}")
                    player['inventory'].append("Brick")
                    if brick_in_objects:
                        room_data['objects'].remove("Brick")
                    if brick_in_revealed:
                        room_data['revealed_items'].remove("Brick")
                    room_data['fireplace_brick_removed'] = True # Flag needed
                    item_taken = True
                    points_awarded = 5
                    player['score'] += 5
                    update_room_state(current_room, "removed_brick")
                    # Potential Hazard
                    if room_data.get('hazard') == 'precarious object':
                        if random.random() < room_data.get('hazard_chance', 0.1) * 1.2:
                            print(f"{COLOR_RED}Removing the brick destabilizes the mantelpiece above! {room_data.get('hazard_death', 'It crashes down on you!')}{COLOR_RESET}")
                            death_occurred = True
                            points_awarded = 0
                            return True # Death occurred
                elif "Brick" in player['inventory']:
                    print(f"You already have the {COLOR_YELLOW}Brick{COLOR_RESET}.")
                    player['turns_left'] -= 1 # Cost turn for trying to take again
                    return death_occurred # No death
                else:
                    print(f"You suspect evidence like 'Brick' might be here, but you need to find it first (e.g., 'look in fireplace').")
                    player['turns_left'] -= 1
                    return death_occurred
            # ...existing code for rusty tools, etc...
        # ...existing code...

        # --- Final Processing ---
        if not death_occurred: # Only process score/turn if player didn't die
            if item_taken:
                player['score'] += points_awarded
                if points_awarded > 0 and points_awarded != 50: # Avoid double message for evidence
                    print(f"{COLOR_GREEN}+{points_awarded} points!{COLOR_RESET}")
                player['turns_left'] -= 1 # Cost turn for successfully taking something
            else:
                # Only print "can't take" if no specific message was printed above
                found_key_or_evidence = False
                for k_name, k_info in keys.items():
                    if k_info.get('location') == current_room and item.lower() == k_name.lower():
                        found_key_or_evidence = True
                        break
                if not found_key_or_evidence:
                    for e_name, e_info in evidence.items():
                        if e_info.get('location') == current_room and item.lower() in e_name.lower():
                            found_key_or_evidence = True
                            break
                if not found_key_or_evidence and not (item.lower() == "book" and current_room == "Library"):
                    print(f"You can't take '{item}' or it's not here/revealed yet.")
                    player['turns_left'] -= 1 # Cost turn for trying to take invalid/unavailable

    except Exception as e:
        print(f"{COLOR_RED}Error taking item: {str(e)}{COLOR_RESET}")
        print("You reach for the item, but something goes wrong...")
        player['turns_left'] -= 1 # Still costs a turn for error
        return False # No death due to error in taking
    return death_occurred # Return final death status

def help_command():
    """Display helpful information about game mechanics."""
    print(f"\n{COLOR_MAGENTA}--- FINAL DESTINATION: TERMINAL HELP ---{COLOR_RESET}")
    print("Your goal is to collect 3 pieces of evidence and escape the house alive.")
    print("\nBASIC COMMANDS:")
    print(f"- {COLOR_CYAN}go [direction]{COLOR_RESET}: Move between rooms")
    print(f"- {COLOR_CYAN}examine [object]{COLOR_RESET}: Look at something closely")
    print(f"- {COLOR_CYAN}take [item]{COLOR_RESET}: Pick up an item")
    print(f"- {COLOR_CYAN}search in [container]{COLOR_RESET}: Look inside something")
    print(f"- {COLOR_CYAN}use [item] on [object]{COLOR_RESET}: Interact with objects using items")
    print(f"- {COLOR_CYAN}unlock [direction/room]{COLOR_RESET}: Unlock a door with the right key")
    print(f"- {COLOR_CYAN}inventory{COLOR_RESET} or {COLOR_CYAN}i{COLOR_RESET}: Check what you're carrying")
    print(f"- {COLOR_CYAN}evidence{COLOR_RESET}: Review collected evidence")
    print(f"- {COLOR_CYAN}help{COLOR_RESET}: Show this help text")
    print("\nADVICE:")
    print("- Search containers carefully to find keys and evidence")
    print("- Be careful! The house contains deadly hazards")
    print("- Once you have 3 pieces of evidence, head for the front porch to escape")
    print("- Your turns are limited - the house will be demolished soon!")

def drop(command):
    if len(command) < 2:
        print("Drop what?")
        player['turns_left'] -= 1
        return False
        
    item_to_drop = " ".join(command[1:])
    current_room = player['location']
    room_data = rooms[current_room]
    death_occurred = False

    if item_to_drop in player['inventory']:
        if item_to_drop.endswith(" Key"):  # Only allow dropping keys for now
            player['inventory'].remove(item_to_drop)
            print(f"You drop the {item_to_drop}.")
            # Potential hazard check for metal keys near faulty wiring
            if room_data.get('hazard') == 'faulty wiring' and 'metal' in item_to_drop.lower():
                if random.random() < room_data.get('hazard_chance', 0.15) * 0.3:
                    print(f"{COLOR_RED}The dropped key clatters near exposed wires, causing a spark!{COLOR_RESET}")
                    print(f"{COLOR_RED}{room_data.get('hazard_death', 'The resulting surge gets you!')}!{COLOR_RESET}")
                    death_occurred = True
        else:
            print("You can only drop keys for now.")
    else:
        print(f"You don't have a {item_to_drop} in your inventory.")

    if not death_occurred:
        player['turns_left'] -= 1
    return death_occurred

def unlock(command):
    if len(command) < 2:
        print("Unlock what?")
        player['turns_left'] -= 1
        return False # No death

    target = " ".join(command[1:])
    current_room = player['location']
    room_data = rooms[current_room]
    unlocked = False
    action_performed = False # Track if any relevant action (success, fail, already unlocked) occurred
    death_occurred = False

    for direction, room_name in rooms[current_room]['exits'].items():
        # Allow unlocking by direction or room name
        if target.lower() == room_name.lower() or target.lower() == direction.lower():
            action_performed = True # We found the target exit
            if room_name in rooms and rooms[room_name].get('locked'):
                # Determine the needed key based on the target room
                needed_key = None
                target_room_data = rooms[room_name] # Get data for the target room
                if room_name == "Attic Entrance": needed_key = "Attic Key"
                elif room_name == "Main Basement Area": needed_key = "Basement Key"
                elif room_name == "Storage Room": needed_key = "Storage Room Key"
                # Add other locked rooms and their keys here

                if needed_key:
                    if needed_key in player['inventory']:
                        print(f"You insert the {COLOR_YELLOW}{needed_key}{COLOR_RESET} into the lock...")
                        # Potential Hazard: Booby-trapped lock?
                        # Example: Faulty wiring hazard on the door being unlocked
                        if target_room_data.get('hazard') == 'faulty wiring':
                            if random.random() < target_room_data.get('hazard_chance', 0.15) * 0.8: # High chance when interacting directly
                                print(f"{COLOR_RED}...touching exposed wires near the lock mechanism! {target_room_data.get('hazard_death', 'A lethal shock courses through you!')}{COLOR_RESET}")
                                death_occurred = True
                                break # Exit loop on death

                        if not death_occurred:
                            print(f"...and turn. Click! The way to the {COLOR_YELLOW}{room_name}{COLOR_RESET} is unlocked.")
                            print(f"{COLOR_GREEN}Unlocked! +10 points.{COLOR_RESET}")
                            target_room_data['locked'] = False # Unlock the target room
                            player['score'] += 10 # Points for unlocking
                            unlocked = True
                            break # Exit loop after successful unlock
                    else:
                        print(f"{COLOR_RED}You need the {needed_key} to unlock the way to the {room_name}.{COLOR_RESET}")
                        break # Exit loop, player lacks key
                else:
                    # This case should ideally not happen if locked rooms always have a defined key
                    print(f"{COLOR_RED}The way to {room_name} is locked, but the key is unknown (game data error).{COLOR_RESET}")
                    break
            elif room_name in rooms and not rooms[room_name].get('locked'):
                print(f"The way to the {COLOR_YELLOW}{room_name}{COLOR_RESET} is already unlocked.")
                action_performed = True # Still counts as an action attempt
                break # Exit loop, already unlocked
            else:
                # This case handles if the exit leads to a non-existent room name
                print(f"{COLOR_RED}Cannot find information for '{room_name}'.{COLOR_RESET}")
                action_performed = True # Still counts as an action attempt
                break

    if not action_performed:
        print(f"There's no locked exit matching '{target}' here.")
        # Penalize turn if no valid target found

    # Decrement turn only if no death occurred
    if not death_occurred:
        player['turns_left'] -= 1
    return death_occurred

def search(command):
    if len(command) < 3 or command[1].lower() != 'in':
        print("Look in what? (e.g., 'look in desk')")
        player['turns_left'] -= 1
        return False # No death
    container_name = " ".join(command[2:])
    current_room = player['location']
    room_data = rooms[current_room]
    death_occurred = False # Flag for death
    searched_something = False # Flag to track if a valid search attempt was made

    # --- Fireplace Search Logic ---
    if container_name.lower() == "fireplace" and current_room == "Living Room":
        searched_something = True # Attempted to search fireplace
        if room_data.get('fireplace_brick_removed'):
            # Brick is removed, check for the key
            key_name = "Basement Key"
            key_info = keys.get(key_name)
            if key_info and key_info.get('location') == current_room and \
               key_info.get('container', '').lower() == container_name.lower() and \
               key_name not in player['inventory'] and \
               key_name not in room_data.get('revealed_items', []):
                print(f"You reach into the dark cavity behind the missing brick and your fingers brush against something cold... It's the {COLOR_YELLOW}{key_name}{COLOR_RESET}!")
                room_data.setdefault('revealed_items', []).append(key_name)
                # No points awarded here, points are for taking
            elif key_name in room_data.get('revealed_items', []) or key_name in player['inventory']:
                 print("You search the cavity behind the missing brick again, but it's empty now.")
            else:
                 # Key wasn't placed here for some reason, or logic error
                 print("You search the cavity behind the missing brick, but find only dust and loose mortar.")
        else:
            # Brick is still in place
            print("You examine the fireplace. Ash and soot cover the hearth. That one brick still looks loose. Maybe you could 'take brick'?")
        # Turn cost handled at the end

    # --- Existing Container Search Logic ---
    elif container_name.lower() in [cont.lower() for cont in room_data.get('possible_containers', [])]:
        searched_something = True # Attempted to search a valid container
        found_something = False
        revealed_text = []

        # Check keys (excluding Basement Key if handled above)
        for key_name, key_info in keys.items():
            if key_name == "Basement Key" and container_name.lower() == "fireplace": continue # Already handled
            if key_info.get('location') == current_room and \
               key_info.get('container', '').lower() == container_name.lower() and \
               key_name not in player['inventory'] and \
               key_name not in room_data.get('revealed_items', []):
                revealed_text.append(f"the {COLOR_YELLOW}{key_name}{COLOR_RESET}")
                room_data.setdefault('revealed_items', []).append(key_name)
                found_something = True

        # Check evidence
        for evidence_name, evidence_info in evidence.items():
             # Use 'in' for partial matches only if needed, exact match is safer for containers
             if evidence_info.get('location') == current_room and \
                evidence_info.get('container', '').lower() == container_name.lower() and \
                not evidence_info.get('found', False) and \
                evidence_name not in room_data.get('revealed_items', []):
                 # Special handling for clipping description if needed
                 display_name = f"a {evidence_name}" if "Newspaper Clipping" in evidence_name else f"'{evidence_name}'" # Adjusted clipping check
                 revealed_text.append(f"{COLOR_YELLOW}{display_name}{COLOR_RESET}")
                 room_data.setdefault('revealed_items', []).append(evidence_name)
                 found_something = True

        if revealed_text:
            print(f"Inside the {container_name}, you find: {', '.join(revealed_text)}.")
        else:
            # Check if items ARE in the container but already revealed/taken
            already_found = False
            for item_list in [keys, evidence]:
                for item_name, item_info in item_list.items():
                    if item_info.get('location') == current_room and \
                       item_info.get('container', '').lower() == container_name.lower():
                        # Check if it's taken (inventory/found) or just revealed
                        if (item_name in player['inventory']) or \
                           (item_name in evidence and evidence[item_name].get('found')) or \
                           (item_name in room_data.get('revealed_items', [])):
                            already_found = True
                            break
                if already_found: break

            if already_found:
                 print(f"You search the {container_name} again, but find nothing new.")
            else:
                 print(f"You search the {container_name}, but it seems to be empty.")
        # Turn cost handled at the end

    # --- Fallback for invalid search targets ---
    # This part only runs if container_name wasn't the fireplace OR a valid container
    if not searched_something:
        # Check if the target is an object in the room but not a container
        is_non_container_object = any(obj.lower() == container_name.lower() for obj in room_data.get('objects', []) if obj.lower() not in [cont.lower() for cont in room_data.get('possible_containers', [])])

        if is_non_container_object:
             print(f"You can't search inside the {container_name}.")
        # Specific non-container messages (like medicine cabinet if it's not searchable)
        elif container_name.lower() == "medicine cabinet" and current_room == "Bathroom": # Added room check
             print(f"You look inside the {container_name} but find only grime and a cracked, empty bottle.") # Assuming it's not a searchable container
        else:
             print(f"You don't see a '{container_name}' here to look inside.")
        # Turn cost handled at the end

    player['turns_left'] -= 1
    return death_occurred # Return death status (currently always False here, but could change)

def trigger_escape_mode():
    """Triggers escape mode with appropriate messaging and effects."""
    global escape_mode
    escape_mode = True
    print(f"\n{COLOR_RED}With this final piece of evidence, the truth hits you like a sledgehammer.{COLOR_RESET}")
    print(f"\n{COLOR_RED}DEATH IS COMING FOR YOU! The disasters, the warnings... they're all real.{COLOR_RESET}")
    print(f"\n{COLOR_RED}You need to get out of this house NOW!{COLOR_RESET}")
    print(f"\n{COLOR_YELLOW}Make your way to the Front Porch to escape!{COLOR_RESET}")
    
    # Increase hazard chances in all rooms
    for room_name, room_data in rooms.items():
        if 'hazard_chance' in room_data:
            room_data['hazard_chance'] *= 1.5  # 50% more dangerous in escape mode
    
    # Add some ambient effects
    player['turns_left'] = min(player['turns_left'], 20)  # Cap remaining turns if over 20
    
    return True

def trigger_chain_reaction(room_name, initial_trigger):
    """Create a chain reaction of hazards based on an initial trigger."""
    try:
        room_data = rooms[room_name]
        
        if initial_trigger == "gas_leak" and room_data.get('hazard') == "faulty wiring":
            print(f"\n{COLOR_RED}The leaking gas meets the sparking wires...{COLOR_RESET}")
            time.sleep(1)  # Dramatic pause
            print(f"\n{COLOR_RED}BOOM! The kitchen explodes in a fireball!{COLOR_RESET}")
            return True  # Fatal
            
        elif initial_trigger == "water_spill" and room_data.get('hazard') == "faulty wiring":
            print(f"\n{COLOR_RED}Water spreads across the floor, reaching the exposed wiring...{COLOR_RESET}")
            time.sleep(1)  # Dramatic pause
            print(f"\n{COLOR_RED}The electric current surges through the puddle and into your body!{COLOR_RESET}")
            return True  # Fatal
            
        elif initial_trigger == "heavy_object" and room_data.get('hazard') == "weak floorboards":
            print(f"\n{COLOR_RED}The weight is too much for the weakened floor...{COLOR_RESET}")
            time.sleep(1)  # Dramatic pause
            print(f"\n{COLOR_RED}The floorboards splinter and give way, plunging you into darkness below!{COLOR_RESET}")
            return True  # Fatal
    
    except Exception as e:
        print(f"{COLOR_RED}Error during chain reaction: {str(e)}{COLOR_RESET}")
        print("Something definitely went wrong, but you survive... for now.")
        
    return False  # Non-fatal if no matching chain reaction or exception occurred

def update_room_state(room_name, action_taken):
    """Updates room state based on player actions"""
    try:
        room_data = rooms.get(room_name, {})
        
        if room_name == "Kitchen" and action_taken == "broke_window":
            # Create a gas leak hazard when window is broken
            if "gas leak" not in room_data.get('hazard', ''):
                room_data['hazard'] = "gas leak"
                room_data['hazard_description'] = "The room is filling with gas from a broken pipe!"
                room_data['hazard_death'] = "A spark ignites the gas, causing a massive explosion!"
                room_data['hazard_chance'] = 0.2
                print(f"{COLOR_YELLOW}You hear a faint hissing sound. The gas pipe must have been damaged.{COLOR_RESET}")
                
                # Chain reaction: If there's also faulty wiring, increase danger
                if any('wiring' in obj.lower() for obj in room_data.get('objects', [])):
                    room_data['hazard_chance'] = 0.4
                    print(f"{COLOR_RED}The exposed wiring near the gas leak creates an extremely dangerous situation!{COLOR_RESET}")
        
        elif room_name == "Living Room" and action_taken == "removed_brick":
            # Update fireplace description after brick removal
            room_data['description'] = room_data['description'].replace(
                "A cold fireplace is the room's centerpiece, with one loose-looking Brick.",
                "A cold fireplace is the room's centerpiece, with a gap where a brick was removed."
            )
            
            # Potential structural weakness from removing the brick
            if random.random() < 0.3:  # 30% chance to add a new hazard
                room_data['hazard'] = "precarious object"
                room_data['hazard_description'] = "The mantelpiece looks unstable after the brick removal..."
                room_data['hazard_death'] = "The heavy mantelpiece crashes down, crushing you beneath it!"
                room_data['hazard_chance'] = 0.15
        
        elif room_name == "Attic" and action_taken == "broke_crate":
            # Update attic description after crate is broken
            room_data['description'] = room_data['description'].replace(
                "The attic is filled with dusty boxes and forgotten relics. You feel a strange presence here.",
                "The attic is filled with dusty boxes and forgotten relics. You feel a strange presence here. A broken crate lies on the floor."
            )
            
            # Reveal the newspaper clipping if not already found
            newspaper_found = False
            for evidence_name, evidence_info in evidence.items():
                if "Newspaper" in evidence_name and evidence_info.get('container') == "crate":
                    room_data.setdefault('revealed_items', []).append(evidence_name)
                    newspaper_found = True
                    break
            
            if not newspaper_found:
                print("The crate is broken, but there doesn't seem to be anything significant inside.")
        
        elif room_name == "Master Bedroom" and action_taken == "pulled_ceiling_fan":
            # Update ceiling fan state
            room_data['description'] = room_data['description'].replace(
                "A massive four-poster bed dominates the room, its velvet curtains ripped and faded.",
                "A massive four-poster bed dominates the room, its velvet curtains ripped and faded. The ceiling fan spins eerily above."
            )
            
            # Random chance for hazard creation from fan
            if random.random() < 0.2:  # 20% chance
                room_data['hazard'] = "precarious object"
                room_data['hazard_description'] = "The ceiling fan wobbles dangerously as it spins..."
                room_data['hazard_death'] = "The fan breaks free from the ceiling, blades slicing through the air as it crashes down on you!"
                room_data['hazard_chance'] = 0.15
        
        elif room_name == "Basement Stairs" and action_taken == "weakened_stairs":
            # Update stairs description after they've been weakened
            room_data['description'] = room_data['description'].replace(
                "A set of creaking wooden stairs leading down into the darkness.",
                "A set of creaking wooden stairs leading down into the darkness. They seem particularly unstable now."
            )
            
            # Increase hazard chance if hazard already exists
            if room_data.get('hazard') == "weak floorboards":
                room_data['hazard_chance'] = min(0.9, room_data.get('hazard_chance', 0.25) * 1.5)  # Cap at 90%
                print(f"{COLOR_RED}The stairs seem much less stable now!{COLOR_RESET}")
    
    except Exception as e:
        print(f"{COLOR_RED}Error updating room state: {str(e)}{COLOR_RESET}")
        print("The game will try to continue, but this room might behave unexpectedly.")

def increase_danger():
    """Increases hazard chances based on turn count"""
    remaining_turns = player['turns_left']
    # Danger increases as turns decrease
    if remaining_turns <= 15:  # Critical danger zone
        danger_multiplier = 2.0
    elif remaining_turns <= 30:  # High danger
        danger_multiplier = 1.5
    elif remaining_turns <= 45:  # Moderate danger
        danger_multiplier = 1.2
    else:
        danger_multiplier = 1.0
        
    # Apply multiplier to all room hazards
    for room_name, room_data in rooms.items():
        if 'hazard_chance' in room_data:
            # Cap maximum chance at 0.75 to avoid guaranteed death
            room_data['hazard_chance'] = min(0.75, room_data['hazard_chance'] * danger_multiplier)

def main():
    """Main function to start and manage the game."""
    global player, escape_mode
    global sink_interactions, crate_interactions, stairs_interactions, bookshelves_interactions, ceiling_fan_pulled

    # Initialize counters and state
    player = {
        "location": "Front Porch",
        "inventory": [],
        "found_evidence": 0,
        "turns_left": 60,
        "visited_rooms": set(),
        "score": 0,
        "opening_disaster": None,
        "last_command_type": None
    }
    
    escape_mode = False
    sink_interactions = 0
    crate_interactions = 0
    stairs_interactions = 0
    bookshelves_interactions = 0
    ceiling_fan_pulled = False

    
    # Set up the game
    randomize_item_locations()
    game_intro()
    
    # Game loop
    while True:
        try:
            # Process any active status effects
            process_status_effects()
            
            # Update visited rooms tracking
            if player['location'] not in player['visited_rooms']:
                player['visited_rooms'].add(player['location'])
            
            # Display room and status information
            display_status()
            
            # Check for ambient events
            ambient_event = get_ambient_event()
            if ambient_event:
                print(ambient_event)
            
            # Check for game-ending conditions
            if check_time():  # Out of turns
                return False
            
            if check_final_room():  # Reached the final room in escape mode
                return True
            
            # Get and process player input
            command = get_input()
            player['last_command_type'] = command[0] if command else None
            continue_game, action_taken, death_occurred = process_player_input(command)
            
            if death_occurred:
                print(f"\n{COLOR_RED}Game Over - Death has claimed you.{COLOR_RESET}")
                return False
            
            if not continue_game:  # Player quit
                print("Thanks for playing!")
                return False
            
            # Increase danger as the game progresses
            if action_taken:
                increase_danger()
                
        except Exception as e:
            print(f"\n{COLOR_RED}Error during gameplay: {str(e)}{COLOR_RESET}")
            print("The game will try to continue...")
            # Optional: log the error to a file
            continue  # Continue to the next iteration of the loop
    
    return False 

# Start the game when the script is run directly
if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n{COLOR_GREEN}Congratulations on your escape!{COLOR_RESET}")
    else:
        print(f"\n{COLOR_RED}Perhaps you'll have better luck next time...{COLOR_RESET}")
    input("\nPress Enter to exit...")
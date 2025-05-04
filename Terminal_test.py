import textwrap
import os
import random
import sys
import time
from shutil import get_terminal_size

# ANSI escape codes for colors
COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m" # Room Name, Objects, Evidence, Keys, Important Items
COLOR_CYAN = "\033[96m"   # Exits, Actions
COLOR_RED = "\033[91m"     # Warnings, Locked status, Hazards, Death
COLOR_GREEN = "\033[92m"   # Success, Unlocked status
COLOR_MAGENTA = "\033[95m" # Special interactions, Hints

REQUIRED_EVIDENCE = 3
ESCAPE_MODE_INVENTORY_THRESHOLD = 5 # Example: More than 5 items triggers porch collapse

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
    "devastating highway pile-up on Route 42": "The highway became a scene of unimaginable chaos as dozens of vehicles collided in a violent, screeching mess of twisted metal and shattered glass.",
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
    "Living Room": {"description": "Overturned armchairs and a tattered sofa litter the living room. The air is thick with the smell of stale tobacco. A cold fireplace is the room's centerpiece, with one loose-looking Brick.", "exits": {"east": "Foyer"}, "objects": ["fireplace", "Brick"], "possible_containers": ["fireplace"], "fireplace_brick_removed": False}, # Added Brick and fireplace_brick_removed flag
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
    "Photo of Alex Browning": {"found": False, "location": "[]", "character": "Alex Browning", "description": "A photo of Alex. Writing on the back describes how he survived the plane crash and is now being hunted by Death, narrowly escaping its design multiple times."},
    "Retractable Clothesline Piece": {"found": False, "location": "[]", "character": "Tod Waggner", "description": "A piece of a retractable clothesline. Tod died when he slipped in his bathroom and accidentally hanged himself with the clothesline."},
    "Photo of Clear Rivers": {"found": False, "location": "[]", "character": "Clear Rivers", "description": "A photo of Clear. Writing on the back describes her survival of the plane crash and her understanding that Death is coming for the survivors. She is actively trying to evade it."},
    "Light Bulb": {"found": False, "location": "[]", "character": "Carter Horton", "description": "A light bulb from a large sign. Carter was killed when a falling sign crushed him."},
    "Miniature Toy Bus": {"found": False, "location": "[]", "character": "Terry Chaney", "description": "A miniature model of a bus. Terry was tragically struck and killed by a speeding bus."},
    "Charred Mug": {"found": False, "location": "[]", "character": "Valerie Lewton", "description": "A burnt and broken ceramic mug. Ms. Lewton died in a house fire (ahem..explosion) caused by a series of unfortunate accidents."},
    "Bloody Piece of Metal": {"found": False, "location": "[]", "character": "Billy Hitchcock", "description": "A jagged piece of metal, stained with what appears to be blood. Billy was decapitated by a piece of metal flung from a train."},
    "Navel Piercing with Crystal": {"found": False, "location": "[]", "character": "Carrie Dreyer", "description": "A small navel piercing with a dangling crystal, belonging to Carrie Dreyer. She died in the Devil's Flight roller coaster crash."},
    "Mud Flap Girl Necklace": {"found": False, "location": "[]", "character": "Frank Cheek", "description": "A cheap, chrome silhouette of a mud flap girl on a chain, won by Frank Cheek. He was decapitated by a fan after surviving the roller coaster crash."},
    "Fuzzy Red Dice": {"found": False, "location": "[]", "character": "Rory Peters", "description": "A pair of fuzzy red dice, similar to those in Rory Peters' car. He died by being sliced into several chunks by wire fencing after surviving the route 23 pile-up."},
    "Cigarette": {"found": False, "location": "[]", "character": "Kat Jennings", "description": "A cigarette, like the ones smoked by Kat Jennings. She died when her car's airbag deployed, impaling her head on a pipe after surviving the route 23 pile-up."},
    "Pool Ball Keychain": {"found": False, "location": "[]", "character": "Eugene Dix", "description": "An orange striped pool ball keychain, the kind Eugene Dix owned. He died by accidental incineration in Lakeview Hospital along with Clear Rivers after surviving the route 23 pile-up."},
    "Valium Pills": {"found": False, "location": "[]", "character": "Nora Carpenter", "description": "A bottle of Valium pills, like those taken by Nora Carpenter. She died when her head was pulled off by an elevator after surviving the route 23 pile-up."},
    "Empty Water Bottle": {"found": False, "location": "[]", "character": "Tim Carpenter", "description": "An empty water bottle, like those Tim Carpenter used as drumsticks. He died being crushed by a falling plate glass window at a dentist's office after surviving the route 23 pile-up."},
    "Nipple Ring": {"found": False, "location": "[]", "character": "Evan Lewis", "description": "A nipple ring, like the one worn by Evan Lewis. He died after being impaled through the facial by a fire ladder after surviving the highway pile-up."},
    "Roxy Duffle Bag": {"found": False, "location": "[]", "character": "Shaina Gordon", "description": "A Roxy brand duffle bag, belonging to Shaina Gordon. She died in the highway pile-up."},
    "Plastic Bag of Weed": {"found": False, "location": "[]", "character": "Dano Royale", "description": "A small plastic bag containing weed, like the one Dano Royale had. He died in the highway pile-up."},
    "White Rose": {"found": False, "location": "[]", "character": "Isabella Hudson", "description": "A white rose, similar to those in Isabella Hudson's van for a memorial service. She survived the highway pile-up and Death's design by giving birth to her baby."},
    "Work Gloves": {"found": False, "location": "[]", "character": "Brian Gibbons", "description": "A pair of work gloves, worn by Brian Gibbons. He died in an explosion caused by a barbeque grill and propane tank after surviving the Lakeview Apartments fire and a secondary attempt on his life by a news van."},
    "Newspaper Clipping about Flight 180": {"found": False, "location": "[]", "character": "Clear Rivers", "description": "A newspaper clipping detailing the Flight 180 disaster and the subsequent deaths of the survivors. Clear Rivers, a survivor of Flight 180, died from gas in a hospital after helping the highway pile-up survivors."},
    "Photo of Jason on Devil's Flight": {"found": False, "location": "[]", "character": "Jason Wise", "description": "A photo of Jason Wise on the Devil's Flight roller coaster. He died in the roller coaster crash."},
    "Overexposed Photo of Kevin": {"found": False, "location": "[]", "character": "Kevin Fischer", "description": "An overexposed photo of Kevin Fischer. He survived the roller coaster crash but died later in a subway crash."},
    "Photo of Lewis from Ring-The-Bell Game": {"found": False, "location": "[]", "character": "Lewis Romero", "description": "A photo of Lewis Romero at the Ring-The-Bell game, where he knocked off the bell. He survived the roller coaster crash but died later by being crushed by weights."},
    "Photo of Ashley and Ashlyn at Clown Shoot": {"found": False, "location": "[]", "character": "Ashley Freund & Ashlyn Halperin", "description": "A photo of Ashley Freund and Ashlyn Halperin at the clown shoot game. They survived the roller coaster crash but died later in a tanning bed accident."},
    "Photo of Ian with Banners": {"found": False, "location": "[]", "character": "Ian McKinley", "description": "A photo of Ian McKinley with banners in the background that look like teeth. He survived the roller coaster crash but died later by being crushed by a falling sign and cherry picker basket."},
    "Photo of Erin": {"found": False, "location": "[]", "character": "Erin Ulmer", "description": "A photo of Erin Ulmer. She survived the Devil's Flight roller coaster premonition."},
    "Photo of Julie Giving the Finger": {"found": False, "location": "[]", "character": "Julie Christensen", "description": "A photo of Julie Christensen giving the finger for the yearbook. She survived the Devil's Flight roller coaster premonition."},
    "Photo of Perry": {"found": False, "location": "[]", "character": "Perry Malinowski", "description": "A photo of Perry Malinowski. She survived the Devil's Flight roller coaster premonition but died later at the fair."},
    "Photo of Amber": {"found": False, "location": "[]", "character": "Amber Regan", "description": "A photo of Amber Regan. She survived the Devil's Flight roller coaster premonition."},
    "Photo of Kimberly": {"found": False, "location": "[]", "character": "Kimberly Corman", "description": "A photo of Kimberly Corman. She survived the highway pile-up premonition and confronted Death at the lake."},
    "Photo of Officer Burke": {"found": False, "location": "[]", "character": "Thomas Burke", "description": "A photo of Officer Thomas Burke. He survived the highway pile-up premonition."},
    "Photo of Frankie": {"found": False, "location": "[]", "character": "Frankie Arnold", "description": "A photo of Frankie Arnold. He died in the highway pile-up."},
    "Newspaper Clipping": {"found": False, "location": "[]", "character": "You", "description": "A newspaper clipping with a headline about a major disaster."}, # Modified entry
}

keys = {
    "Attic Key": {"found": False, "location": "Library"},
    "Basement Key": {"found": False, "location": "Bathroom"},
    "Storage Room Key": {"found": False, "location": "Main Basement Area"}
}

def game_intro():
    global player
    width = get_terminal_width()
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


def randomize_item_locations():
    global evidence, keys # Ensure we are modifying the global dictionaries

    # 1. Reset locations, containers, and found status for all items
    for item_dict in [evidence, keys]:
        for item_name, item_info in item_dict.items():
            item_info['found'] = False
            item_info['location'] = None # Reset location
            item_info['container'] = None # Reset container

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


    # 3. Identify items to place dynamically
    key_names = list(keys.keys())
    # Exclude fixed/special evidence items like "Newspaper Clipping"
    placeable_evidence_names = [e for e in evidence.keys() if e != "Newspaper Clipping about Flight 180"] # Adjust if your clipping name is different

    # 4. Determine number of evidence items to select based on available slots
    num_slots_available = len(all_container_slots)
    num_keys_to_place = len(key_names)

    if num_keys_to_place > num_slots_available:
        raise ValueError(f"Not enough container slots ({num_slots_available}) to place all keys ({num_keys_to_place}). Check room definitions.")

    num_evidence_slots = num_slots_available - num_keys_to_place
    num_evidence_to_select = min(len(placeable_evidence_names), num_evidence_slots)

    # 5. Select a random subset of evidence
    selected_evidence = random.sample(placeable_evidence_names, num_evidence_to_select)

    # 6. Combine items to be placed
    items_to_place = key_names + selected_evidence

    # 7. Shuffle container slots
    random.shuffle(all_container_slots)

    # 8. Assign items to shuffled slots
    print("\n--- Item Placement ---") # Debugging output
    for item_name in items_to_place:
        if not all_container_slots:
            print(f"Warning: Ran out of container slots while trying to place {item_name}.")
            break # Stop if we run out of slots unexpectedly

        room_name, container_name = all_container_slots.pop()

        if item_name in keys:
            keys[item_name]['location'] = room_name
            keys[item_name]['container'] = container_name
            print(f"Placed Key '{item_name}' in '{container_name}' in room '{room_name}'")
        elif item_name in evidence:
            evidence[item_name]['location'] = room_name
            evidence[item_name]['container'] = container_name
            print(f"Placed Evidence '{item_name}' in '{container_name}' in room '{room_name}'")

    # 9. Handle fixed items explicitly
    # Example: Ensure Newspaper Clipping is always in the Attic crate
    if "Newspaper Clipping" in evidence:
        if "Attic" in rooms and "crate" in rooms["Attic"].get("possible_containers", []):
            evidence["Newspaper Clipping"]['location'] = "Attic"
            evidence["Newspaper Clipping"]['container'] = "crate"
            print(f"Placed Fixed Evidence 'Newspaper Clipping' in 'crate' in room 'Attic'")
        else:
            print("Warning: Could not place fixed 'Newspaper Clipping' in Attic crate. Check room/container definitions.")

    # --- Add Fixed Placement for Basement Key ---
    if "Basement Key" in keys:
        keys["Basement Key"]['location'] = "Living Room"
        keys["Basement Key"]['container'] = "fireplace"
        print(f"Placed Fixed Key 'Basement Key' in 'fireplace' in room 'Living Room'")
    else:
        print("Warning: 'Basement Key' not found in keys dictionary for fixed placement.")
    # --- End Fixed Placement ---
            
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

def process_player_input(command):
    """Parses player input and calls the appropriate action function."""
    continue_game = True
    action_taken = False # Did the player attempt a valid action type?
    death_occurred = False # Did the action result in death?

    if not command:
        print("Please enter a command.")
        return continue_game, action_taken, death_occurred # No action taken, no death

    verb = command[0].lower()
    action_taken = True # Assume an action was attempted if input is not empty

    if verb == "go":
        death_occurred = move(command)
    elif verb == "examine":
        death_occurred = examine(command)
    elif verb == "take":
        death_occurred = take(command) # Now returns death status
    elif verb == "drop":
        death_occurred = drop(command) # Now returns death status
    elif verb == "use":
        death_occurred = use_item(command)
    elif verb == "unlock":
        death_occurred = unlock(command) # Now returns death status
    elif verb == "search" or verb == "look": # Allow 'look in' as alias for 'search in'
        if len(command) > 1 and command[1].lower() == 'in':
             death_occurred = search(command) # search already returns death status
        else:
             print("Look where? Or 'look in [container]'?")
             action_taken = False # Invalid syntax for 'look'
             player['turns_left'] -= 1 # Penalize turn for bad command
    elif verb == "inventory" or verb == "i":
        inventory_str = ", ".join([f"{COLOR_YELLOW}{item}{COLOR_RESET}" for item in player['inventory']]) if player['inventory'] else "Empty"
        print(f"Inventory: {inventory_str}")
        action_taken = False # Viewing inventory doesn't count as taking a turn or a risk
    elif verb == "list":
        print("Available commands: go [direction], examine [object/item], take [item], drop [key], use [item] on [object], search in [container], unlock [exit/room], inventory, list, quit")
        action_taken = False # Listing commands doesn't count as taking a turn or a risk
    elif verb == "quit":
        print("Are you sure you want to quit? (yes/no)")
        confirm = input("> ").lower()
        if confirm == 'yes':
            continue_game = False
        action_taken = False # Quitting confirmation doesn't count as taking a turn or a risk
    else:
        print(f"Unknown command: '{verb}'")
        action_taken = False # Invalid command
        player['turns_left'] -= 1 # Penalize turn for bad command

    # Turn decrement is now handled within each action function (or here for invalid commands)
    # We no longer need a separate check based on action_taken here.

    return continue_game, action_taken, death_occurred


def examine(command):
    global ceiling_fan_pulled # Keep this if used elsewhere, otherwise remove
    global sink_interactions, crate_interactions, stairs_interactions, bookshelves_interactions # Add new counters

    if len(command) < 2:
        print("Examine what?")
        return False # Return False as no death occurred
    item = " ".join(command[1:])
    current_room = player['location']
    room_data = rooms[current_room] # Get current room data
    # evidence_found_this_turn = False # This variable is not used, can be removed
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
            player['turns_left'] -= 1

    if random.random() < room_data.get('hazard_chance', 0.25) * death_chance_multiplier:
        print(f"\n{COLOR_RED}The stairs finally give way under your repeated testing!{COLOR_RESET}")
        print(f"{COLOR_RED}You tumble down into the darkness, breaking your neck on the concrete floor below.{COLOR_RESET}")
        death_occurred = True
    else:
        print("The stairs groan alarmingly but hold for now. This is extremely dangerous.")

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
            player['turns_left'] += 3 # Add score for surviving hazard
            player['score'] += 3

    # Check for loose wire when examining sink (if water is present conceptually) - Assuming 'faulty wiring' covers this now. Can be removed or merged.
    elif hazard_type == "loose wire" and item.lower() == "sink" and current_room == "Kitchen":
        specific_interaction = True
        print("You examine the sink. Water drips slowly, pooling near a sparking wire...")
        if random.random() < hazard_chance:
            print(hazard_info.get('death_message', "You step in the puddle!"))
            death_occurred = True
        else:
            print("You carefully avoid the puddle near the sparking wire.")
            player['turns_left'] -= 1

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
                print("You examine the grimy sink. You notice some exposed wiring nearby and a faint smell of gas. Better be careful.") # Added hint
            elif sink_interactions == 2:
                print("Looking closer at the sink, the wiring sparks intermittently. The gas smell is stronger. This feels dangerous.")
            else: # Third time's the charm?
                print("You tempt fate near the sink again. The wiring crackles violently...")
                death_chance_multiplier = 2.0 # Base multiplier for tempting fate
                final_death_message = "...but nothing happens this time. You really need to stop doing that."

                # Check specific hazards for increased risk
                if room_data.get('hazard') == 'gas leak':
                    death_chance_multiplier = 3.0 # Higher chance for ignition
                    if random.random() < room_data.get('hazard_chance', 0.2) * death_chance_multiplier:
                         print("...igniting the gas filling the room!")
                         print(room_data.get('hazard_death', "The kitchen explodes!"))
                         death_occurred = True
                    else:
                         final_death_message = "...Sparks fly, but the gas doesn't ignite. Your luck is unbelievable."

                elif room_data.get('hazard') == 'faulty wiring':
                     death_chance_multiplier = 2.5 # Higher chance for electrocution
                     if random.random() < room_data.get('hazard_chance', 0.15) * death_chance_multiplier:
                         print(room_data.get('hazard_death', "You touch the sink and get electrocuted!"))
                         death_occurred = True
                     else:
                         final_death_message = "...A strong shock jolts you, but you survive. Seriously, stop it."

                if not death_occurred:
                    print(final_death_message)

            if not death_occurred: player['turns_left'] -= 1

        # Bookshelves Interaction
        elif item.lower() == "bookshelves" and current_room == "Library" and not specific_interaction:
            bookshelves_interactions += 1
            specific_interaction = True
            if bookshelves_interactions == 1:
                print("You examine the towering bookshelves. They seem old and overloaded, leaning slightly.")
            elif bookshelves_interactions == 2:
                print("Running your hand along a shelf, you feel it shift noticeably. Dust rains down. One book looks particularly loose.") # Hint for potential 'take' hazard
            else: # Third interaction
                print("You lean against the bookshelves carelessly...")
                death_chance_multiplier = 2.5 # Increased chance for leaning

                if room_data.get('hazard') == 'unstable shelf':
                    if random.random() < room_data.get('hazard_chance', 0.1) * death_chance_multiplier:
                        print(room_data.get('hazard_death', "The shelves give way!"))
                        death_occurred = True
                    else:
                        print("The shelves groan loudly and shift, but remain standing. That was incredibly foolish.")
                else: # No specific hazard, but still risky
                     if random.random() < 0.15: # Base chance of collapse from leaning
                         print("The old wood groans and splinters... the entire structure collapses on top of you!")
                         death_occurred = True
                     else:
                        print("...they hold your weight, creaking ominously. Probably not a good idea to do that again.")
            if not death_occurred: player['turns_left'] -= 1

        # Crate Interaction (Attic)
        elif item.lower() == "crate" and current_room == "Attic" and not specific_interaction:
             crate_interactions += 1
             specific_interaction = True
             if crate_interactions == 1:
                 print("You examine the sturdy wooden crate. It looks like it might contain stored items. A newspaper clipping is pinned to the side.")
             elif crate_interactions == 2:
                 print("You tap on the crate. It sounds mostly hollow, but something shifts inside. The wood seems brittle in places.")
             else: # Third interaction
                 print("You try to shift the heavy crate...")
                 death_chance_multiplier = 1.5

                 if room_data.get('hazard') == 'precarious object': # e.g., something stored ON the crate
                     if random.random() < room_data.get('hazard_chance', 0.1) * death_chance_multiplier:
                         print(f"...dislodging the {item} resting on top! {room_data.get('hazard_death', 'It falls and crushes you!')}")
                         death_occurred = True
                     else:
                         print("...something wobbles precariously on top, but settles back down. Careful!")
                 elif room_data.get('hazard') == 'weak floorboards':
                     if random.random() < room_data.get('hazard_chance', 0.25) * death_chance_multiplier:
                         print(f"...The movement is too much for the rotten floorboards beneath! {room_data.get('hazard_death', 'The floor gives way!')}")
                         death_occurred = True
                     else:
                         print("...The floorboards groan loudly under the combined weight, but hold.")
                 else: # Generic risk
                     if random.random() < 0.1:
                         print("...As you push it, your hand slips through a rotten plank! A sharp splinter embeds itself deep in your arm. The shock and pain are intense...")
                         # Could add a status effect later, for now just flavour/minor consequence
                         print("You pull your hand back, wincing. That hurt.")
                     else:
                         print("...It scrapes loudly across the floor but doesn't reveal anything new.")
             if not death_occurred: player['turns_left'] -= 1

        # Stairs Interaction (Basement Stairs)
        elif item.lower() == "stairs" and current_room == "Basement Stairs" and not specific_interaction:
             stairs_interactions += 1
             specific_interaction = True
             if stairs_interactions == 1:
                 print("You examine the creaking wooden stairs leading down. They look old and somewhat unstable, especially near the bottom.")
             elif stairs_interactions == 2:
                 print("You cautiously put some weight on the top step. It groans in protest. A couple of steps near the bottom look particularly rotten.")
             else: # Third interaction
                 print("You jump lightly on the stairs to test them...")
                 death_chance_multiplier = 2.0

                 if room_data.get('hazard') == 'weak floorboards': # If the stairs themselves are the hazard
                     if random.random() < room_data.get('hazard_chance', 0.25) * death_chance_multiplier:
                         print(f"\n{COLOR_RED}The stairs finally give way under your repeated testing!{COLOR_RESET}")
                         print(f"{COLOR_RED}You tumble down into the darkness, breaking your neck on the concrete floor below.{COLOR_RESET}")
                         death_occurred = True
                     else:
                         print("The stairs groan alarmingly but hold for now. This is extremely dangerous.")
                 else: # Generic risk
                     if random.random() < 0.2:
                         print("That was close. These stairs aren't safe.")
                     else:
                         print("...They creak loudly but seem to hold. Still, caution is advised.")
             if not death_occurred: player['turns_left'] -= 1

        # Ceiling Fan Interaction (Master Bedroom) - Moved to 'use' command later

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
            "stairs": "A set of wooden stairs leading downwards, looking somewhat unstable.", # Hint added
            "workbench": "A solid workbench covered in old, rusty tools and layers of dust. Might be useful things here.", # Hint added
            "shelves": "Wooden shelves lined with dusty jars and forgotten equipment. They look ready to collapse.", # Hint added
            "nightstand": "A small table beside the bed, likely for personal items. Its drawer is slightly ajar.",
            "ceiling fan with chains": "An old ceiling fan hangs overhead, coated in dust. Two chains dangle from it, one likely for the light, one for the fan.", # Description added
            "toy red suv": "A small, plastic red SUV toy car. It looks like it's seen better days.", # Description added
            "strange diagrams": "Sheets of paper covered in complex, unsettling diagrams and equations. They don't make immediate sense.", # Description added
            "camera": "An older model camera rests on the desk, a layer of dust covering its lens.", # Description added
            "broken window": "The window frame is shattered, glass shards litter the floor nearby. Cold air blows through.", # For after using brick
            "broken crate": "Splintered remains of a wooden crate lie on the floor.", # For after using brick
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
    if not specific_interaction:
         player['turns_left'] -= 1

    return death_occurred

def use_item(command):
    if len(command) < 4 or command[2].lower() != 'on':
        print("Use which item on what? (e.g., 'use brick on window')")
        player['turns_left'] -= 1
        return False
    item_to_use = command[1]
    target_object = " ".join(command[3:])
    current_room = player['location']
    room_data = rooms[current_room]

    death_occurred = False
    interaction_happened = False
    target_exists = any(obj.lower() == target_object.lower() for obj in room_data.get('objects', []))

    if item_to_use not in player['inventory']:
        print(f"You don't have a {item_to_use}.")
        player['turns_left'] -= 1
        return False

    if not target_exists:
        print(f"You don't see a {target_object} here to use the {item_to_use} on.")
        player['turns_left'] -= 1
        return False

    # Use Brick on Boarded Window
    if item_to_use.lower() == "brick" and target_object.lower() == "boarded window":
        if current_room == "Kitchen":
            print("You smash the heavy brick against the boarded-up window.")
            print("With a splintering crack, the boards break, revealing the outside... but also dislodging a loose gas pipe fitting near the window frame.")
            print(f"{COLOR_RED}Gas begins to hiss loudly into the room!{COLOR_RESET}") # Added color
            if "boarded window" in room_data['objects']:
                room_data['objects'].remove("boarded window")
            if "broken window" not in room_data['objects']:
                room_data['objects'].append("broken window") # Add broken window object
            # Update room description to reflect broken window and gas
            rooms[current_room]['description'] = "The kitchen is a scene of chaotic disarray. Broken plates and scattered utensils cover the floor. The back door is heavily boarded up. You see a glint of metal near the sink. The window is smashed, and the smell of gas is strong."
            # Add or update hazard
            room_data['hazard'] = "gas leak"
            room_data['hazard_info'] = { # Define full hazard info if not already present
                "description": "The room is filling with flammable gas!",
                "death_message": "A stray spark from your movement ignites the gas!",
                "trigger_chance": 0.4
            }
            room_data['hazard_description'] = room_data['hazard_info']['description']
            room_data['hazard_death'] = room_data['hazard_info']['death_message']
            room_data['hazard_chance'] = room_data['hazard_info']['trigger_chance']
            interaction_happened = True
            update_room_state(current_room, "broke_window") # Call the new function
        else:
            print("There's no boarded window here to use the brick on.")

    # Use Brick on Crate (New Interaction)
    elif item_to_use.lower() == "brick" and target_object.lower() == "crate":
        if current_room == "Attic":
            print("You bring the heavy brick down hard on the wooden crate.")
            # Check if the newspaper clipping is supposed to be here and hasn't been revealed yet
            newspaper_name = "Newspaper Clipping"
            if newspaper_name in evidence and \
               evidence[newspaper_name].get('location') == current_room and \
               evidence[newspaper_name].get('container') == "crate" and \
               newspaper_name not in room_data.get('revealed_items', []):
                print("The wood splinters and breaks apart. Pinned inside, you see a Newspaper Clipping!")
                room_data.setdefault('revealed_items', []).append(newspaper_name)
                # Optionally remove 'crate' and add 'broken crate'
                if "crate" in room_data['objects']:
                    room_data['objects'].remove("crate")
                if "broken crate" not in room_data['objects']:
                    room_data['objects'].append("broken crate")
                rooms[current_room]['description'] = "The attic is filled with dusty boxes and forgotten relics, along with the remains of a smashed crate. You feel a strange presence here." # Update description
            else:
                print("The crate splinters, but there doesn't seem to be anything significant hidden inside its remains.")
                # Optionally remove 'crate' and add 'broken crate' even if nothing found
                if "crate" in room_data['objects']:
                    room_data['objects'].remove("crate")
                if "broken crate" not in room_data['objects']:
                    room_data['objects'].append("broken crate")
                rooms[current_room]['description'] = "The attic is filled with dusty boxes and forgotten relics, along with the remains of a smashed crate. You feel a strange presence here." # Update description
            interaction_happened = True
        else:
            print("There's no crate here to use the brick on.")

    # --- Use Tools on Boarded Window/Door ---
    elif item_to_use.lower() == "rusty tools" and target_object.lower() == "boarded window":
        if current_room == "Kitchen":
            print("You wedge the prybar from your toolset between the planks on the window.")
            print("With a screech of protesting nails and splintering wood, you manage to pry off the boards.")
            print(f"{COLOR_YELLOW}The window is now open, but the noise might attract attention... or worse.{COLOR_RESET}")
            if "boarded window" in room_data['objects']:
                room_data['objects'].remove("boarded window")
            if "broken window" not in room_data['objects']: # Or just 'open window'?
                room_data['objects'].append("broken window")
            # Update room description
            rooms[current_room]['description'] = rooms[current_room]['description'].replace("There's also a boarded window.", "The window is broken open.")
            # Potential Hazard: Does noise trigger something? Or does opening window cause issue?
            if room_data.get('hazard') == 'gas leak':
                print(f"{COLOR_RED}Opening the window creates a draft, swirling the gas... hopefully dispersing it.{COLOR_RESET}")
                # Could potentially reduce gas leak chance? Or increase ignition near window? For now, just flavour.
            interaction_happened = True
        else:
            print("There's no boarded window here to use the tools on.")

    elif item_to_use.lower() == "rusty tools" and target_object.lower() == "boarded door": # Assuming a boarded door exists somewhere
        # Example: Boarded back door in Kitchen
        if current_room == "Kitchen" and "boarded door" in room_data.get('objects', []): # Need to add 'boarded door' to Kitchen objects
            print("You use the prybar on the heavily boarded back door.")
            print("It takes considerable effort, but you manage to loosen and remove the planks.")
            print(f"{COLOR_YELLOW}The back door is now accessible, leading outside.{COLOR_RESET}")
            # Add 'outside' exit to Kitchen
            rooms[current_room]['exits']['outside'] = "Backyard" # Define a 'Backyard' room
            # Update objects and description
            room_data['objects'].remove("boarded door")
            room_data['objects'].append("back door")
            rooms[current_room]['description'] = rooms[current_room]['description'].replace("The back door is heavily boarded up.", "The back door stands open, leading outside.")
            interaction_happened = True
            # Define the Backyard room (simple example)
            if "Backyard" not in rooms:
                rooms["Backyard"] = {"description": "A small, overgrown backyard. The fence is broken in places. The back door leads inside.", "exits": {"inside": "Kitchen"}, "objects": ["broken fence"], "possible_containers": []}
        else:
            print("There's no boarded door here to use the tools on.")

    # --- Use Chains on Ceiling Fan ---
    elif item_to_use.lower() == "chains" and target_object.lower() == "ceiling fan with chains": # Requires player to 'take chains'? Or just 'use chains'? Let's assume 'use chains' implies pulling them.
        if current_room == "Master Bedroom":
            print("You reach up and pull one of the chains dangling from the ceiling fan.")
            # Decide which chain does what randomly? Or fixed? Let's make it random.
            chain_effect = random.choice(["light", "fan", "stuck", "hazard"])
            if chain_effect == "light":
                print("A dim light flickers on, casting long shadows across the room.")
                # Could update room description or add 'light is on' state
            elif chain_effect == "fan":
                print("With a groan, the dusty fan blades begin to turn slowly, stirring up clouds of dust.")
                # Potential Hazard: Fan blades detach?
                if random.random() < 0.15:
                    print("One of the fan blades looks dangerously loose...")
                    if random.random() < 0.3:
                        print("...and detaches, flying across the room like a guillotine! It narrowly misses your head!")
                        print(f"{COLOR_YELLOW}That was way too close!{COLOR_RESET}")
                    else:
                        print("...but it holds on. For now.")
                # Potential Hazard: Dust triggers allergy/coughing fit? (Flavour)
                print("You cough as dust fills the air.")
            elif chain_effect == "stuck":
                print("You pull the chain, but it's stuck fast. Nothing happens.")
            elif chain_effect == "hazard":
                print("As you pull the chain, you hear a crackling sound from the fan's motor housing.")
                # Check for faulty wiring hazard
                if room_data.get('hazard') == 'faulty wiring':
                    if random.random() < room_data.get('hazard_chance', 0.15) * 2.0: # Increased chance
                        print("Sparks shower down! The faulty wiring ignites the motor!")
                        print(room_data.get('hazard_death', "The fan explodes in a shower of sparks and burning plastic, electrocuting you!"))
                        death_occurred = True
                    else:
                        print("Sparks shower down, and you smell burning plastic, but it doesn't fully ignite. You quickly let go.")
                else: # Generic hazard
                    if random.random() < 0.1:
                        print("A large spark jumps from the chain to your hand! The shock throws you backwards!")
                        # Minor injury/stun?
                        print("You land hard, stunned but alive.")
                    else:
                        print("It just crackles ominously. Probably best not to pull that again.")
            interaction_happened = True
        else:
            print("There's no ceiling fan with chains here.")

    # --- Add alias for pulling chains ---
    elif command[0].lower() == "pull" and ("chain" in command[1].lower() or "chains" in command[1].lower()):
        if current_room == "Master Bedroom" and "ceiling fan with chains" in room_data.get('objects', []):
            # Redirect to the 'use chains on ceiling fan' logic
            return use_item(["use", "chains", "on", "ceiling fan with chains"]) # Recursive call with standardized command
        else:
            print("There are no chains here to pull.")
            # No turn cost for failed alias if it wasn't a valid 'use' command initially
            return False # No death, no interaction
    else:
        if not interaction_happened and not death_occurred: # Added death check here
            print(f"You can't use the {item_to_use} on the {target_object} like that.")

    # Decrement turn only if an interaction happened or failed, and no death occurred
    if (interaction_happened or not target_exists or item_to_use not in player['inventory']) and not death_occurred:
        player['turns_left'] -= 1
    elif not interaction_happened and not death_occurred: # Case where use is invalid syntax/logic
        player['turns_left'] -= 1
        return False # No death, no interaction

    return death_occurred

def take(command):
    # ... (check command length - assuming this exists in your broader code) ...
    if len(command) < 2:
        print("Take what?")
        player['turns_left'] -= 1
        return

    item = " ".join(command[1:])
    current_room = player['location']
    room_data = rooms[current_room]
    item_taken = False
    points_awarded = 0
    death_occurred = False

    # --- Hazard Check: Taking unstable items ---
    # Example: Taking a book from unstable bookshelves in Library
    if item.lower() == "book" and current_room == "Library" and room_data.get('hazard') == 'unstable shelf':
        print("You reach for a dusty book on the overloaded shelf...")
        if random.random() < room_data.get('hazard_chance', 0.1) * 1.5: # Slightly increased chance when interacting
            print(room_data.get('hazard_death', "The shelf gives way under the slight shift!"))
            death_occurred = True
            return True # Death occurred
        else:
            print("The shelf groans ominously but holds. You snatch the book quickly.")
            # Note: We don't actually give the player a generic 'book' here,
            # this is just an example hazard trigger. If specific books are evidence,
            # handle taking them below. This interaction costs a turn even if no death.
            player['turns_left'] -= 1
            return False # No death, but action taken


    # --- Taking Keys ---
    for key_name, key_info in keys.items():
        if item.lower() == key_name.lower():
            # Check if the key is physically present and revealed in the current room
            if key_info.get('location') == current_room and key_name in room_data.get('revealed_items', []):
                if key_name not in player['inventory']:
                    print(f"You take the {COLOR_YELLOW}{key_name}{COLOR_RESET}.")
                    player['inventory'].append(key_name)
                    # Remove from revealed items so it doesn't show up in the room anymore
                    if key_name in room_data.get('revealed_items', []):
                        room_data['revealed_items'].remove(key_name)
                    item_taken = True
                    points_awarded = 7 # Points for key
                    player['score'] += 7
                    break # Exit loop once key is taken
                else:
                    print(f"You already have the {COLOR_YELLOW}{key_name}{COLOR_RESET}.")
                    return # Exit function immediately (no turn cost)
            # Check if the key is in the room but not revealed (e.g., still in container)
            elif key_info.get('location') == current_room:
                print(f"You see the {COLOR_YELLOW}{key_name}{COLOR_RESET}, but you need to find it first (e.g., 'look in {key_info.get('container', 'container')}').")
                return # Exit function immediately (no turn cost)
            # If key is not in this room, continue checking other keys
            else:
                continue

    # --- Taking Evidence ---
    if not item_taken: # Only check evidence if a key wasn't already taken
        for evidence_name, evidence_info in evidence.items():
            # Use 'in' for partial matches (e.g., 'take photo' might match 'Photo of X')
            if item.lower() in evidence_name.lower():
                # Check if the evidence is physically present, revealed, and not already found
                if evidence_info.get('location') == current_room and \
                   evidence_name in room_data.get('revealed_items', []) and \
                   not evidence_info.get('found', False):
                    print(f"You take the {COLOR_YELLOW}{evidence_name}{COLOR_RESET}.")
                    evidence[evidence_name]['found'] = True
                    player['found_evidence'] += 1
                    player['score'] += 10  # Points for finding evidence
                    
                    # Add this block to trigger escape mode
                    if player['found_evidence'] >= REQUIRED_EVIDENCE:
                        global escape_mode
                        escape_mode = True
                        print(f"\n{COLOR_RED}You've found enough evidence! Death's design is clear now. You need to escape before the demolition begins!{COLOR_RESET}")
                    
                    # Remove from revealed items
                    if evidence_name in room_data.get('revealed_items', []):
                        room_data.get('revealed_items', []).remove(evidence_name)
                    item_taken = True
                    points_awarded = 50 # Points for evidence
                    print(f"{COLOR_GREEN}Evidence found! +{points_awarded} points.{COLOR_RESET}")
                    break # Exit loop once evidence is taken
                # Check if evidence is in the room but not revealed
                elif evidence_info.get('location') == current_room and \
                     evidence_name not in room_data.get('revealed_items', []) and \
                     not evidence_info.get('found', False):
                    print(f"You suspect evidence like '{evidence_name}' might be here, but you need to find it first (e.g., 'look in {evidence_info.get('container', 'container')}').")
                    return # Exit function immediately (no turn cost)
                # Check if evidence is revealed but already found
                elif evidence_info.get('location') == current_room and \
                     evidence_name in room_data.get('revealed_items', []) and \
                     evidence_info.get('found', False):
                    print(f"You already found the {COLOR_YELLOW}{evidence_name}{COLOR_RESET}.")
                    return # Exit function immediately (no turn cost)
                # If evidence is not relevant here, continue checking others
                else:
                    continue

    # --- Taking Other Items (Brick, Tools) ---
    if not item_taken and item.lower() == "brick" and current_room == "Living Room" and "Brick" in room_data.get('objects', []):
        if "Brick" not in player['inventory']:
            print(f"You wiggle the loose {COLOR_YELLOW}Brick{COLOR_RESET} out of the fireplace. It feels heavy.")
            print(f"{COLOR_MAGENTA}Removing the brick reveals a small, dark cavity and loosens some mortar. The structure above looks less stable...{COLOR_RESET}") # Hint/warning
            player['inventory'].append("Brick")
            room_data['objects'].remove("Brick")
            room_data['fireplace_brick_removed'] = True # Flag needed
            item_taken = True
            points_awarded = 5 # Small points for potentially useful item
            player['score'] += 5
            # Potential Hazard: Does removing brick cause collapse?
            if room_data.get('hazard') == 'precarious object': # e.g. unstable mantelpiece
                 if random.random() < room_data.get('hazard_chance', 0.1) * 1.2:
                     print(f"{COLOR_RED}Removing the brick destabilizes the mantelpiece above! {room_data.get('hazard_death', 'It crashes down on you!')}{COLOR_RESET}")
                     death_occurred = True
                     # No points awarded if player dies
                     points_awarded = 0
                     # Don't decrement turn here, death ends turn implicitly
                     return True # Death occurred
        else:
            print(f"You already have the {COLOR_YELLOW}Brick{COLOR_RESET}.")
            # No turn cost if already have item
            return False # No death

    elif not item_taken and item.lower() == "rusty tools" and current_room == "Main Basement Area" and "rusty tools" in room_data.get('objects', []):
         if "rusty tools" not in player['inventory']:
             print(f"You pick up the {COLOR_YELLOW}rusty tools{COLOR_RESET} from the workbench. They include a prybar and some cutters.")
             player['inventory'].append("rusty tools")
             room_data['objects'].remove("rusty tools")
             item_taken = True
             points_awarded = 10 # Points for useful item
             player['score'] += 10
             # Potential Hazard: Touching tools near faulty wiring?
             if room_data.get('hazard') == 'faulty wiring':
                 if random.random() < room_data.get('hazard_chance', 0.15) * 0.5: # Lower chance, indirect contact
                     print(f"{COLOR_RED}As you grab the metal tools, your arm brushes against the sparking wires! {room_data.get('hazard_death', 'A jolt throws you back!')}{COLOR_RESET}")
                     # Decide if this is lethal or just a shock
                     # For now, let's make it lethal based on default message
                     death_occurred = True
                     points_awarded = 0
                     return True # Death occurred
         else:
             print(f"You already have the {COLOR_YELLOW}rusty tools{COLOR_RESET}.")
             # No turn cost if already have item
             return False # No death

    # --- Final Processing ---
    if not death_occurred: # Only process score/turn if player didn't die
        if item_taken:
            player['score'] += points_awarded
            if points_awarded > 0:
                print(f"{COLOR_GREEN}+{points_awarded} points!{COLOR_RESET}")
            player['turns_left'] -= 1 # Cost turn for successfully taking something
        else:
            # Only print "can't take" if no specific message was printed above
            # and no hazard interaction occurred (like the book example)
            if not any(k_info.get('location') == current_room and item.lower() == k_name.lower() for k_name, k_info in keys.items()) and \
               not any(e_info.get('location') == current_room and item.lower() in e_name.lower() for e_name, e_info in evidence.items()) and \
               not (item.lower() == "book" and current_room == "Library"): # Avoid double message for book hazard
                print(f"You can't take '{item}' or it's not here/revealed yet.")
                player['turns_left'] -= 1 # Cost turn for trying to take something invalid/unavailable

    return death_occurred # Return final death status


def drop(command):
    if len(command) < 2:
        print("Drop what?")
        player['turns_left'] -= 1
        return False # No death
    item_to_drop = " ".join(command[1:])
    current_room = player['location']
    room_data = rooms[current_room]
    death_occurred = False

    if item_to_drop in player['inventory']:
        if item_to_drop.endswith(" Key"): # Only allow dropping keys for now
            player['inventory'].remove(item_to_drop)
            print(f"You drop the {item_to_drop}.")
            # Potential Hazard: Dropping metal key near faulty wiring?
            if room_data.get('hazard') == 'faulty wiring' and 'metal' in item_to_drop.lower(): # Simplistic check
                if random.random() < room_data.get('hazard_chance', 0.15) * 0.3: # Low chance
                    print(f"{COLOR_RED}The dropped key clatters near the exposed wires, causing a large spark! {room_data.get('hazard_death', 'The resulting surge gets you!')}{COLOR_RESET}")
                    death_occurred = True
                    # Turn already decremented below
            # Add key back to room's revealed items? Or leave it dropped permanently?
            # For simplicity, let's just drop it. Player needs to be careful.
        else:
            print("You can only drop keys for now.")
            # No turn cost if invalid drop type? Or penalize? Let's penalize.
    else:
        print(f"You don't have a {item_to_drop} in your inventory.")
        # Penalize turn for trying to drop something not held

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

# Add a new function to track room state changes
def update_room_state(room_name, action_taken):
    """Updates room state based on player actions"""
    if room_name == "Kitchen" and action_taken == "broke_window":
        # Create a chain reaction
        if "gas leak" not in rooms[room_name].get('hazard', ''):
            rooms[room_name]['hazard'] = "gas leak"
            rooms[room_name]['hazard_chance'] = 0.2
            print(f"{COLOR_YELLOW}You hear a faint hissing sound. The gas pipe must have been damaged.{COLOR_RESET}")
            
            # Chain reaction: If there's also faulty wiring, increase danger
            if any('wiring' in obj.lower() for obj in rooms[room_name].get('objects', [])):
                rooms[room_name]['hazard_chance'] = 0.4
                print(f"{COLOR_RED}The exposed wiring near the gas leak creates an extremely dangerous situation!{COLOR_RESET}")

def play_game():
    global player, ceiling_fan_pulled, escape_mode
    global sink_interactions, crate_interactions, stairs_interactions, bookshelves_interactions
             action_taken = False # Or True if you want failed pull to cost a turn? Let's say False for now.
    # Reset player state and game variables1 and command[1] == "in":
    player = {
        "location": "Front Porch",
        "inventory": [],, action_taken, death_occurred
        "found_evidence": 0,
        "turns_left": 60,!")
        "actions_taken": 0,
        "visited_rooms": set(),
        "opening_disaster": Noneulled, escape_mode
    }lobal sink_interactions, crate_interactions, stairs_interactions, bookshelves_interactions
    ceiling_fan_pulled = False # Assuming this is still used elsewhere
    escape_mode = Falsee and game variables
    sink_interactions = 0
    crate_interactions = 0 Porch",
    stairs_interactions = 0
    bookshelves_interactions = 0
        "turns_left": 60,
    # Reset room states (like locked doors, revealed items, hazards) if necessary
    # This might require a separate function to reset room dictionaries to their initial state
    # For now, assuming randomize_item_locations handles item resets sufficiently
    # and locked status/hazards might need manual reset if changed during gameplay.
    # Example (needs refinement based on actual state changes):sewhere
    # reset_room_states() # Placeholder for a function that resets rooms dict
    sink_interactions = 0
    randomize_item_locations()
    game_intro()actions = 0
    bookshelves_interactions = 0
    while True:
        if player['location'] not in player['visited_rooms']:azards) if necessary
             player['visited_rooms'].add(player['location'])ictionaries to their initial state
        display_status()randomize_item_locations handles item resets sufficiently
    # and locked status/hazards might need manual reset if changed during gameplay.
        # Check for game ending conditions (win/loss/timeout)):
        if check_final_room(): # This now handles win/loss in escape modedict
            return True # Game ended
    randomize_item_locations()
        # Check for timeout (only if not already ended by check_final_room)
        # Use turns_left directly instead of actions_taken for timeout check
        if check_time(): # check_time returns True if turns_left <= 0
            print("\nGame Over - Ran out of time!")d_rooms']:
            return True # Game ended.add(player['location'])
        display_status()
        command = get_input()
        continue_game, action_taken, death_occurred = process_player_input(command)
        if check_final_room(): # This now handles win/loss in escape mode
        if not continue_game: # Player chose to quit
            return True # Game ended
        # Check for timeout (only if not already ended by check_final_room)
        if death_occurred:irectly instead of actions_taken for timeout check
            print("\nGame Over")_time returns True if turns_left <= 0
            return True # Game ended out of time!")
            return True # Game ended
        # No need to track actions_taken separately if turns_left is the primary timer
        # Turns are decremented within the action functions themselves
        continue_game, action_taken, death_occurred = process_player_input(command)
    # Main game loop (remains the same)
    while True:not continue_game: # Player chose to quit
        play_game() # Run the game, returns True when game ends
        play_again = input("Do you want to play again? (yes/no): ").lower()
        if play_again != 'yes':
            print("Thanks for playing!")
            breaketurn True # Game ended

            # No need to track actions_taken separately if turns_left is the primary timer
            # Turns are decremented within the action functions themselves

    # Main game loop (remains the same)
    while True:
        play_game() # Run the game, returns True when game ends
        play_again = input("Do you want to play again? (yes/no): ").lower()
        if play_again != 'yes':
            print("Thanks for playing!")
            break


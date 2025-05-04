import random
import textwrap
import os

# Game Setup
player = {
    "location": "Front Porch",
    "inventory": [],
    "found_evidence": 0,
    "turns_left": 45,
    "actions_taken": 0
}

# Define potential containers
containers = ["dresser", "cupboard", "drawer", "shelf", "box", "nightstand", "desk drawer", "medicine cabinet", "workbench"]

rooms = {
    "Front Porch": {"description": "The rotted wooden porch creaks under your feet. The front door, a heavy oak, is slightly ajar. A chilling breeze whispers through the overgrown ivy.", "exits": {"inside": "Foyer"}, "objects": [], "possible_containers": []},
    "Foyer": {"description": "A grand, yet decaying foyer. A crystal chandelier hangs precariously overhead, coated in dust. A wide staircase ascends to the upper floor. To the west, you see a shadowed living room, and to the east, a formal dining room.", "exits": {"upstairs": "Hallway", "west": "Living Room", "east": "Dining Room"}, "objects": ["dusty table"], "possible_containers": ["dusty table"]},
    "Living Room": {"description": "Overturned armchairs and a tattered sofa litter the living room. The air is thick with the smell of stale tobacco. A cold fireplace is the room's centerpiece. You might want to 'examine fireplace'.", "exits": {"east": "Foyer"}, "objects": ["fireplace"], "possible_containers": ["fireplace"]},
    "Dining Room": {"description": "A long, mahogany dining table is draped with a moth-eaten cloth. The silverware is tarnished, and cobwebs cling to the empty chairs.", "exits": {"west": "Foyer", "south": "Kitchen"}, "objects": ["dining table"], "possible_containers": ["cupboard"]},
    "Kitchen": {"description": "The kitchen is a scene of chaotic disarray. Broken plates and scattered utensils cover the floor. The back door is heavily boarded up. You see a glint of metal near the sink.", "exits": {"north": "Dining Room"}, "objects": ["sink", "broken plates"], "possible_containers": []},
    "Library": {"description": "Towering bookshelves line the walls, filled with crumbling books. A large, oak desk sits in the center - its drawers slightly ajar and a book about urban demolition sitting open on top, featuring a wrecking ball doing what they do best.", "exits": {"east": "Foyer"}, "objects": ["bookshelves"], "possible_containers": ["desk", "bookshelves"]},
    "Hallway": {"description": "The upstairs hallway is eerily silent. Moonlight spills through a grimy window at the end of the hall. Doors lead to several bedrooms and a bathroom. The attic entrance is a dark, imposing doorway.", "exits": {"downstairs": "Foyer", "north": "Master Bedroom", "south": "Guest Bedroom 1", "east": "Guest Bedroom 2", "west": "Bathroom", "up": "Attic Entrance"}, "objects": [], "possible_containers": []},
    "Master Bedroom": {"description": "A massive four-poster bed dominates the room, its velvet curtains ripped and faded.","exits": {"south": "Hallway"},"objects": ["bed"], "possible_containers": ["nightstand"]},
    "Guest Bedroom 1": {"description": "A small, spartan bedroom with a single bed. A child's toy, a red SUV, sits forlornly on the floor. You might want to 'examine toy red suv'.", "exits": {"north": "Hallway"}, "objects": ["bed"], "possible_containers": ["bed"]},
    "Guest Bedroom 2": {"description": "This room was clearly a study. A large, cluttered desk is covered in papers and strange diagrams. A camera rests on the desk. You might want to 'examine camera'.", "exits": {"west": "Hallway"}, "objects": [], "possible_containers": ["desk"]},
    "Bathroom": {"description": "The air is thick with the stench of mildew. A cracked mirror reflects your uneasy face. The medicine cabinet hangs open.", "exits": {"east": "Hallway"}, "objects": ["mirror"], "possible_containers": ["medicine cabinet"]},
    "Attic Entrance": {"description": "A dark and ominous entrance to the attic. It's secured with a heavy-looking lock.", "exits": {"down": "Hallway"}, "locked": True, "objects": [], "possible_containers": []},
    "Attic": {"description": "The attic is filled with dusty boxes and forgotten relics. You feel a strange presence here. A single newspaper clipping is pinned to a crate.", "exits": {"down": "Attic Entrance"}, "objects": ["crate"], "possible_containers": ["crate"]},
    "Basement Stairs": {"description": "A set of creaking wooden stairs leading down into the darkness. A padlock secures the entrance.", "exits": {"up": "Foyer", "down": "Main Basement Area"}, "locked": True, "objects": [], "possible_containers": []},
    "Main Basement Area": {"description": "The air in the basement is cold and damp. Pipes groan overhead, and the smell of mildew is overpowering. A workbench is covered in tools. A door to a Storage Room is to the south.", "exits": {"up": "Basement Stairs", "south": "Storage Room"}, "objects": [], "possible_containers": ["workbench"]},
    "Storage Room": {"description": "A cramped storage room filled with shelves of dusty jars and forgotten equipment. You feel an intense sense of dread.", "exits": {"north": "Main Basement Area"}, "objects": ["shelves"], "possible_containers": ["shelves"]}
}

ceiling_fan_pulled = False

escape_mode = False

# Initialize interaction counters globally (or within the play_game function if you prefer)
sink_interactions = 0
crate_interactions = 0
stairs_interactions = 0
bookshelves_interactions = 0

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
    "Photo of Ethel Newton": {"found": False, "location": "[]", "character": "Ethel Newton", "description": "Photo with writing on the back: Ethel Newton fell to her death from a malfunctioning elevator."},
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
    "Charred Mug": {"found": False, "location": "[]", "character": "Valerie Lewton", "description": "A burnt and broken ceramic mug. Ms. Lewton died in a house fire caused by a series of unfortunate accidents."},
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
    "Photo of Frankie": {"found": False, "location": "[]", "character": "Frankie Arnold", "description": "A photo of Frankie Arnold. He died in the highway pile-up."}
}

keys = {
    "Attic Key": {"found": False, "location": "[]"},
    "Basement Key": {"found": False, "location": "[]"},
    "Storage Room Key": {"found": False, "location": "[]"}
}

def play_game():
    """Encapsulates the main game loop."""
    global player, ceiling_fan_pulled, escape_mode  # Reset global variables

    # Reset game state
    player = {
        "location": "Front Porch",
        "inventory": [],
        "found_evidence": 0,
        "turns_left": 60,
        "actions_taken": 0
    }
    ceiling_fan_pulled = False
    escape_mode = False
    randomize_item_locations() # Re-randomize item locations for a new game

    game_intro()

    while True:
        display_status()

        if player['actions_taken'] > 0 and check_time():
            print("\nGame Over")
            return False  # Game ended due to time

        death_occurred = False
        if check_final_room():
            # check_final_room can also return True if the player dies in the attic
            death_occurred = True
            print("\nGame Over") # Death message might already be in check_final_room
            return False

        command = get_input()

        if not command:
            continue

        action_taken = False # Flag to track if a valid action was taken

        if command[0] == "go":
            if move(command): # move returns True if death occurred
                death_occurred = True
                print("\nGame Over") # Death message is inside move
                break
            action_taken = True
        elif command[0] == "examine":
            if examine(command): # examine returns True if death occurred
                death_occurred = True
                print("\nGame Over") # Death message is inside examine
                break
            action_taken = True
        elif command[0] == "take":
            take(command)
            action_taken = True
        elif command[0] == "unlock":
            unlock(command)
            action_taken = True
        elif command[0] == "look" and len(command) > 1 and command[1] == "in":
            look_in(command)
            action_taken = True
        elif command[0] == "look" and command[1] == "around":
            look_around()
            action_taken = True
        elif command[0] == "inventory":
            print("Inventory:", ", ".join(player['inventory']))
        elif command[0] == "time":
            print(f"Turns Left: {player['turns_left']}")
        elif command[0] == "list":
            list_actions()
        elif command[0] == "help":
            print("\nWelcome to Final Destination: Terminal.")
            print("Your goal is to find 3 pieces of evidence and escape before time runs out.")
            print("Explore the manor, interact with objects, and be careful.")
            print("Type 'list' to see available actions.")
        elif command[0] == "quit":
            print("Thanks for playing!")
            return False # Player quit

        else:
            print("I don't understand that command. Type 'list' for help.")

        if action_taken:
            player['actions_taken'] += 1

        # Check for game over due to turns (again, after action)
        if player['actions_taken'] > 0 and check_time():
            print("\nGame Over")
            return False

        # Winning Condition
        if player['location'] == "Front Porch" and player['found_evidence'] == 3:
            print("\nYou burst through the front door...")
            print("\nCongratulations, you survived McKinley Manor...")
            return True # Player won

        if death_occurred:
            break

    return False # Game over (death or other reason)

# Main game loop that allows restarting
while True:
    game_over = not play_game() # play_game returns True on win, False on game over
    if game_over:
        play_again = input("Do you want to play again? (yes/no): ").lower()
        if play_again != 'yes':
            break
    else:
        break # Player won, no need to ask to play again

def game_intro():
    width = get_terminal_width()
    print("\nFINAL DESTINATION: TERMINAL")
    print("\nWelcome to McKinley, population: Dropping like flies.")
    print("\nLocal tales speak of numerous accidental deaths, murders, and suicides attributed to something called 'Death's List'. It was always been nonsense to you. Past tense.")
    print("You've just arrived at the abandoned residence of one William Bludworth - who has not been seen in some time, but it is said he held evidence proving Death was a force of nature out to claim survivors of multiple casualty disasters.")
    print("\nYou are an investigative journalist determined to uncover the truth behind the legends of McKinley before the demolition of the place, which is supposed to be in 2 days.")

    disasters = {
    "massive plane crash": "You were seconds from boarding the flight when a chilling premonition stopped you cold. From the terminal window, you watched in horror as two passenger jets collided in a fiery explosion over McKinley, a catastrophe that claimed hundreds of lives.",
    "devastating highway pile-up on Route 42": "You were merging onto Route 42 when you had an inexplicable urge to pull over. Just moments later, a devastating chain reaction of mangled metal erupted behind you, leaving dozens dead in the highway pile-up.",
    "luxury ferry sinking in Lake Serenity": "You were on deck of the 'Queen Isabella' when a sudden wave of nausea hit you. Disembarking just minutes before its departure, you stood on the shore as the ferry tragically succumbed to the depths of Lake Serenity, taking countless souls with it.",
    "terrifying rollercoaster derailment at 'Demon's Peak'": "You were strapped into your seat on the 'Demon's Peak' coaster when a last-second decision made you unbuckle and step off. A moment later, the ride began its ascent, only to derail in a terrifying spectacle, turning a day of thrills into a nightmare.",
    "inferno at the 'Crimson Lounge' nightclub": "You were about to step into the 'Crimson Lounge' when a sudden feeling of dread washed over you, causing you to hesitate. Moments later, screams erupted from inside as the nightclub became an inferno, trapping many inside.",
    "collapse of the McKinley Memorial Bridge": "You were driving onto the McKinley Memorial Bridge when you felt an unsettling vibration. Trusting your gut, you slammed on the brakes and reversed off just as the bridge buckled and plunged into the river below, a horrifying collapse.",
    "explosion at the McKinley Chemical Plant": "You were walking near the McKinley Chemical Plant when an overwhelming sense of urgency compelled you to run. Barely out of range, you witnessed the devastating explosion that leveled the facility and took many lives.",
    "wildfire that swept through McKinley National Forest": "You were hiking in McKinley National Forest when you noticed an unusual smell of smoke and an unnatural stillness in the air. You immediately turned back, narrowly escaping the rapidly spreading wildfire that left a trail of destruction.",
    "freak storm that flooded downtown McKinley": "You were in downtown McKinley when an inexplicable feeling of unease made you seek higher ground. Minutes later, a freak storm unleashed torrential rain, flooding the streets and causing chaos and loss of life.",
    "high-speed train collision outside McKinley": "You were waiting on the platform for the commuter train when a strange feeling urged you to step back from the edge. Just then, a freight train collided head-on with your train in a brutal impact with a high death toll.",
    "ski lift malfunction": "You were halfway up the mountain on the ski lift when you heard a sickening grinding sound. A wave of dizziness washed over you, and you instinctively jumped onto a nearby snowdrift just as the lift cable snapped, sending chairs plummeting down the slope.",
    "apartment collapse": "You were about to enter your apartment building when you noticed a hairline crack running along the facade. A sudden wave of panic hit you, and you backed away rapidly as the entire structure imploded in a cloud of dust and debris.",
    "earthquake": "You were walking down a busy street when a subtle tremor ran through the ground. An overwhelming sense of danger made you dive under a sturdy awning just as the earthquake intensified, causing buildings to crumble around you.",
    "typhoon": "You were near the coast when the weather took a sudden and violent turn. An inexplicable fear urged you to seek shelter inland, mere hours before a devastating typhoon made landfall, unleashing its fury on the coastline.",
    "sinkhole": "You were walking across a seemingly normal patch of ground when you felt a slight give. An immediate sense of alarm made you leap backward as the earth opened up, swallowing the area you were just standing on into a massive sinkhole.",  
    "cruise ship fire": "You were enjoying the evening festivities on the cruise ship when a sudden acrid smell filled the air. A powerful instinct told you to head for an emergency exit, just as flames erupted, engulfing a large section of the vessel.",
    "dam break": "You were picnicking by the river downstream from the massive dam when you felt an unusual vibration in the ground. A primal urge to flee washed over you, and you ran uphill as a wall of water surged towards you, the dam having catastrophically failed.",
    "gas pipeline explosion": "You were driving down a rural road when you noticed a faint hissing sound in the distance. An overwhelming sense of unease made you accelerate rapidly, narrowly escaping the massive fireball that erupted behind you as a gas pipeline exploded.",
    "factory collapse": "You were visiting a local factory when you noticed some support beams groaning ominously. A sudden wave of claustrophobia made you rush towards the exit, just as the building's roof caved in, crushing everything below.",
    "ferris wheel malfunction": "You were at the amusement park, about to board the giant Ferris wheel, when you saw a worrying flicker in the machinery. A strong feeling of unease made you decline, watching in horror as the wheel malfunctioned, sending cars spinning wildly."
    }

    chosen_disaster = random.choice(list(disasters.keys()))
    disaster_description = disasters[chosen_disaster] # Get the description using the key
    print(f"You have a personal stake because, as fate would have it, you recently walked away from a {chosen_disaster} that ended many lives.")
    print(disaster_description) # Print the detailed description
    print("More were lost afterwards, the other survivors.. in increasingly gruesome accidents. You are the last one left.")

    print("\nYour goal is to find 3 key pieces of evidence related to people who saw Death coming before your own time runs out.")
    print("You have a limited number of turns before dawn.")
    print("Type 'list' to see available actions.")
    print("\nExplore the grounds, interact with objects or examine evidence, and watch your step!")
    print("\nGood luck...")
    input("\nPress Enter to begin...")

# Function to assign random containers to items
def randomize_item_locations():
    # Assign random containers to keys
    for key_name, key_info in keys.items():
        # Get the room where the key is supposed to be
        room_name = key_info['location']
        # Get the list of possible containers in that room
        containers_in_room = rooms[room_name]['possible_containers']
        if containers_in_room:
            # Choose a random container from the list
            keys[key_name]['container'] = random.choice(containers_in_room)
        else:
            # This should ideally not happen if all key locations have containers
            keys[key_name]['container'] = "somewhere in the room"
            print(f"Warning: No containers found in {room_name} for {key_name}")

    # Assign random containers to evidence (excluding Newspaper Clipping)
    for evidence_name, evidence_info in evidence.items():
        if evidence_name != "Newspaper Clipping":
            # Get the room where the evidence is supposed to be
            room_name = evidence_info['location']
            # Get the list of possible containers in that room
            containers_in_room = rooms[room_name]['possible_containers']
            if containers_in_room:
                # Choose a random container from the list
                evidence[evidence_name]['container'] = random.choice(containers_in_room)
            else:
                # This should ideally not happen if all evidence locations have containers
                evidence[evidence_name]['container'] = "somewhere in the room"
                print(f"Warning: No containers found in {room_name} for {evidence_name}")

# Call the randomization function at the start of the game
randomize_item_locations()

# Final Room (Attic)
final_room = "Attic"

def get_terminal_width():
    try:
        columns = os.get_terminal_size().columns
        return columns
    except OSError:
        # Handle cases where the terminal size can't be determined
        return 80  # Default width

def display_status():
    width = get_terminal_width()
    wrapped_description = textwrap.fill(rooms[player['location']]['description'], width=width)

    print(f"\n--- {player['location']} ---")
    print(wrapped_description)
    if rooms[player['location']]['objects']:
        print("You see the following objects here:", ", ".join(rooms[player['location']]['objects']))
    print(f"Turns Left: {player['turns_left']}")
    print("Inventory:", ", ".join(player['inventory']))
    found_evidence_names = [name for name, info in evidence.items() if info['found']]
    print("Evidence Found:", ", ".join(found_evidence_names) if found_evidence_names else "None")
    print("Exits:")
    for direction, room in rooms[player['location']]['exits'].items():
        locked_status = " (Locked)" if rooms[room].get('locked') else ""
        print(f"- {direction}: {room}{locked_status}")
    print("\nPossible Actions: look around, go [inside, west, upstairs, etc.], examine [object], take [item], unlock [room], look in [container], inventory, time, quit")
    if player['turns_left'] <= 14 and player['turns_left'] > 0:
        if random.random() < 0.6: # 60% chance
            print("\nThe roar of heavy machinery is deafening. You can hear the distinct sound of impacts nearby. You must have been mistaken about the demolition, it's happening now! Time is running out!")
    elif player['turns_left'] <= 29 and player['turns_left'] > 15:
        if random.random() < 0.4:
            print("\nThe mechanical sounds are getting louder. You can hear distinct grinding and the rumble of an engine.")
    elif player['turns_left'] <= 44 and player['turns_left'] > 30:
        if random.random() < 0.2:
            print("\nThe distant hum is more noticeable now, and you occasionally hear a metallic clank.")
    elif player['turns_left'] <= 60 and player['turns_left'] > 45 and random.random() < 0.1:
        print("\nYou hear a faint, distant hum, like machinery far away, getting ready for a busy day in the morning.")

def get_input():
    return input("> ").lower().split()

def move(command):
    if len(command) < 2:
        print("Go where?")
        return
    direction = command[1]
    current_room = player['location']
    if direction in rooms[current_room]['exits']:
        next_room = rooms[current_room]['exits'][direction]
        if next_room in rooms and rooms[next_room].get('locked') and not any(key in player['inventory'] for key, info in keys.items() if info['location'] == next_room):
            print("That way is locked.")
        else:
            if current_room == "Front Porch" and next_room == "Foyer":
                print("The porch floorboards bend and snap under your feet as your weight leaves them. It feels like they could break at any second if any more weight had been applied.")
                print("You jump through the doorway to avoid breaking the patio floorboards. The heavy front door slams shut behind you, causing the crystal chandelier overhead to shudder violently. The cable anchoring the bourgeoise behemoth groans under the new momentum as the wind from the door causes it to sway in your direction.")
            player['location'] = next_room
            player['turns_left'] -= 1
            if rooms[player['location']].get('hazard'):
                if rooms[player['location']]['hazard'] == "weak floor" and random.random() < 0.3: # 30% chance on entering
                    print("\n" + rooms[player['location']]['hazard_description'])
                    return True # Indicate death
                elif rooms[player['location']]['hazard'] == "unstable stairs" and next_room == "Main Basement Area":
                    print("\n" + rooms[player['location']]['hazard_description'])
                    return True # Indicate death
    else:
        print("You can't go that way.")
    return False # No death

def handle_evidence_examination(command, evidence_item):
    item = " ".join(command[1:])  # Get the item the player is trying to examine
    if player['location'] == evidence[evidence_item]["location"] and item.lower() in evidence_item.lower() and not evidence[evidence_item]["found"]:
        print(f"You find a piece of evidence: {evidence_item}.")
        evidence[evidence_item]["found"] = True
        player['found_evidence'] += 1
        return True
    return False

def examine(command):
    global ceiling_fan_pulled
    global sink_interactions, crate_interactions, stairs_interactions, bookshelves_interactions

    if len(command) < 2:
        print("Examine what?")
        return
    item = " ".join(command[1:])
    current_room = player['location']
    evidence_found_this_turn = False
    specific_interaction = False # Flag to track if a specific interaction occurred

    evidence_items_to_check = ["Brick", "Toy SUV", "Camera"]
    for ev_item in evidence_items_to_check:
        if handle_evidence_examination(command, ev_item): # Pass the 'command' here
            evidence_found_this_turn = True
            specific_interaction = True
            # Potentially add room object updates here if needed
            break

    # Specific evidence triggers on examination
    if player['location'] == evidence["Brick"]["location"] and item.lower() == "fireplace" and not evidence["Brick"]["found"]:
        print("\nYou examine the fireplace closely. You notice a loose brick. Carefully, you dislodge it. It's surprisingly heavy and stained with what looks like dried blood. Behind it, you find a small, faded photograph. On the back, you can make out the name 'Alex' and a date. You think you saw a shadow pass over something deeper in the fireplace, too. You can reexamine if you want to take a closer look..")
        evidence["Brick"]["found"] = True
        player['found_evidence'] += 1
        evidence_found_this_turn = True
        rooms["Living Room"]["objects"].append("Brick")
        specific_interaction = True

    # Collapsing Fireplace Hazard (after finding the brick)
    elif player['location'] == "Living Room" and item.lower() == "fireplace" and evidence["Brick"]["found"]:
        width = get_terminal_width()
        if random.random() < 0.6: # 60% chance of collapse after finding the brick
            print("\nYou examine the fireplace again. The structure seems unstable after you removed the brick. Suddenly, with a loud groan, parts of the mantelpiece and chimney collapse, sending debris crashing down on you. You are crushed beneath the weight of the falling stone.")
            return True
        else:
            print("You examine the fireplace again. It looks unstable, but nothing happens this time.")
        specific_interaction = True
    elif player['location'] == evidence["Toy SUV"]["location"] and item.lower() == "toy red suv" and not evidence["Toy SUV"]["found"]:
        print("\nYou pick up the small red toy SUV. It feels strangely heavy for its size. An unsettling feeling washes over you. This is a replica of the vehicle Kimberly C was driving when the Route 18 pileup happened. Her friends died in this truck, and you almost think you can see the outlines of people inside the tiny little die cast toy.")
        evidence["Toy SUV"]["found"] = True
        player['found_evidence'] += 1
        evidence_found_this_turn = True
        specific_interaction = True
    elif player['location'] == evidence["Camera"]["location"] and item.lower() == "camera" and not evidence["Camera"]["found"]:
        print("\nYou find a digital camera on the desk. Flipping through the photos, you see a series of disturbing images taken during a high school graduation night at the local amusement park, hinting at various accidents that took the lives of a bunch of students who were kind of garbage. Like, not actively bad, but nobody really missed them when they were gone, you know?")
        evidence["Camera"]["found"] = True
        player['found_evidence'] += 1
        evidence_found_this_turn = True
        specific_interaction = True
    elif player['location'] == "Master Bedroom" and item.lower() == "nightstand":
        print("\nYou examine the nightstand. It's a simple wooden table. You notice a bloodstained journal on top.")
        if "bloodstained journal" not in rooms["Master Bedroom"]["objects"]:
            rooms["Master Bedroom"]["objects"].append("bloodstained journal")
        specific_interaction = True
    elif player['location'] == "Master Bedroom" and item.lower() == "bloodstained journal" and "bloodstained journal" in rooms["Master Bedroom"]["objects"]:
        print("\nYou examine the bloodstained journal. A faint, unsettling energy seems to emanate from its aged pages. You cautiously open it and read a final, desperate entry, the words scrawled with a chilling urgency: 'The accidents... you've witnessed them, haven't you? Dismissed them as mere chance? Folly. It is the List. Always has been. Death... a meticulous architect, reclaiming what is due. I have glimpsed the design, the terrible elegance of its purpose. The key, I believe... the key lies in understanding its hunger, its need for balance. To truly defy it, one must...' The ink here is smeared, as if the writer was interrupted by a sudden, violent act. The final words are lost to time and blood.")
        specific_interaction = True
    elif player['location'] == "Master Bedroom" and item.lower() == "ceiling fan with chains":
        if not ceiling_fan_pulled:
            ceiling_fan_pulled = True
            if random.random() < 0.4: # 40% chance of collapse on the first pull
                print("\nYou reach up and pull one of the chains on the ceiling fan. With a sudden, terrifying crack, the aged plaster around the fan mount gives way. The entire fixture, blades and all, tears free from the ceiling, plummeting towards you.")
                print("The heavy motor slams into your skull, and the spinning blades slice through the air. You collapse, a mangled mess, as the rest of the ceiling rains down, burying you in dust and debris.")
                return True
            else:
                print("You pull one of the chains on the ceiling fan. It seems to adjust the speed. The fixture wobbles slightly, making you uneasy.")
        else:
            print("\nYou reach up and pull the chain again. This time, there's no wobble, only a sickening ripping sound. The remaining support gives way entirely.")
            print("The ceiling fan detaches completely, falling with lethal force. The edge of a blade catches your neck, tearing through flesh and artery. You gasp, blood spurting, as the weight of the motor crushes your chest. Darkness takes you swiftly.")
            return True

    # Environmental Hazard Checks with Increasing Probability
    if current_room == "Kitchen" and "sink" in item.lower():
        sink_interactions += 1
        width = get_terminal_width()
        # Increase probability based on interactions (example: 0.1 + interactions * 0.05)
        death_chance = 0.1 + sink_interactions * 0.05
        if random.random() < death_chance:
            print("\nYou examine the sink closely again. The sparking intensifies. You reach out...")
            print("A massive electrical shock courses through your body. You are instantly killed.")
            return True
        else:
            print("You examine the sink. The wiring sparks at you like you owe it money, but nothing happens ..this time.")
        specific_interaction = True
    elif current_room == "Attic" and "crate" in item.lower():
        crate_interactions += 1
        width = get_terminal_width()
        death_chance = 0.05 + crate_interactions * 0.04
        if random.random() < death_chance:
            print("\nYou examine the crate again. You hear a worrying creak from above...")
            print("The stack of boxes collapses, and one hits you squarely on the head. You die instantly.")
            return True
        else:
            print("You examine the crate. It seems sturdy, but the boxes above shift slightly.")
        specific_interaction = True
    elif current_room == "Basement Stairs" and "stairs" in item.lower():
        stairs_interactions += 1
        width = get_terminal_width()
        death_chance = 0.15 + stairs_interactions * 0.06
        if random.random() < death_chance:
            print("\nYou examine the stairs again. The wood is clearly rotting.")
            print("As you step onto a weak-looking step, it gives way entirely, and you fall down the stairs, breaking your neck.")
            return True
        else:
            print("You examine the stairs carefully. They feel unstable.")
        specific_interaction = True
    elif current_room == "Library" and "bookshelves" in item.lower():
        bookshelves_interactions += 1
        width = get_terminal_width()
        death_chance = 0.03 + bookshelves_interactions * 0.03
        if random.random() < death_chance:
            print("\nYou examine the bookshelves again. One shelf is leaning precariously.")
            print("The shelf topples over, burying you under a mountain of books. You are crushed.")
            return True
        else:
            print("You examine the bookshelves. They are still imposing and dusty.")
        specific_interaction = True

    if not evidence_found_this_turn and not specific_interaction:
        # ... (rest of your default examine logic) ...

        player['turns_left'] -= 1
    return False # No death

def take(command):
    if len(command) < 2:
        print("Take what?")
        return
    item = " ".join(command[1:])
    current_room = player['location']

    # Check if it's a key
    for key_name, key_info in keys.items():
        if key_info['location'] == current_room.lower() and item.lower() == key_name.lower():
            if key_name not in player['inventory']:
                print(f"You take the {key_name}.")
                player['inventory'].append(key_name)
                player['turns_left'] -= 1
                return
            else:
                print(f"You already have the {key_name}.")
                player['turns_left'] -= 1
                return

    # Check if it's evidence that can be taken
    for evidence_name, evidence_info in evidence.items():
        # Only allow taking evidence if it's in the current room and hasn't been found yet
        if evidence_info['location'] == current_room.lower() and item.lower() in evidence_name.lower() and not evidence_info['found']:
            print(f"You take the {evidence_name}.")
            player['inventory'].append(evidence_name)
            evidence[evidence_name]['found'] = True # Mark it as found
            player['found_evidence'] += 1
            player['turns_left'] -= 1
            return

    print(f"You can't take that.")
    player['turns_left'] -= 1

def drop(command):
    if len(command) < 2:
        print("Drop what?")
        return
    item_to_drop = " ".join(command[1:])
    if item_to_drop in player['inventory']:
        if item_to_drop.endswith(" Key"): # Only allow dropping keys
            player['inventory'].remove(item_to_drop)
            print(f"You drop the {item_to_drop}.")
        else:
            print("You can only drop keys.")
    else:
        print(f"You don't have a {item_to_drop} in your inventory.")
    player['turns_left'] -= 1

def unlock(command):
    if len(command) < 2:
        print("Unlock what?")
        return
    target = " ".join(command[1:])
    current_room = player['location']

    for direction, room in rooms[current_room]['exits'].items():
        if room == target and rooms[room].get('locked'):
            for key_name, key_info in keys.items():
                if key_info['location'] == current_room.lower() and key_name in player['inventory'] and key_name.lower().startswith(target.lower().split()[0]): # Basic key matching
                    print(f"You use the {key_name} to unlock the {target}.")
                    rooms[room]['locked'] = False
                    player['turns_left'] -= 1
                    return
            print(f"You need a key to unlock the {target}.")
            player['turns_left'] -= 1
            return
    print(f"There's no locked {target} here.")
    player['turns_left'] -= 1

def look_in(command):
    if len(command) < 3:
        print("Look in what?")
        return
    container_name = " ".join(command[2:])
    current_room = player['location']

    if container_name.lower() in [obj.lower() for obj in rooms[current_room].get('objects', [])]:
        found_item = False
        # Check for keys in this container
        for key_name, key_info in keys.items():
            if key_info['location'] == current_room.lower() and key_info['container'].lower() == container_name.lower() and not key_info['found']:
                print(f"Inside the {container_name}, you find the {key_name}!")
                player['inventory'].append(key_name)
                keys[key_name]['found'] = True
                found_item = True
                break # Found a key, no need to check for evidence in the same container

        # If no key was found, check for evidence
        if not found_item:
            for evidence_name, evidence_info in evidence.items():
                if evidence_name != "Newspaper Clipping" and evidence_info['location'] == current_room.lower() and evidence_info['container'].lower() == container_name.lower() and not evidence_info['found']:
                    print(f"Inside the {container_name}, you find a piece of evidence: {evidence_name}!")
                    evidence[evidence_name]['found'] = True
                    player['found_evidence'] += 1
                    found_item = True
                    break

        if not found_item:
            print(f"You look inside the {container_name} but find nothing of interest.")
    else:
        print(f"You don't see a {container_name} here to look inside.")
    player['turns_left'] -= 1

def look_around():
    current_room = player['location']
    print(f"You take a closer look at your surroundings in the {current_room}.")
    print(rooms[current_room]['description'])
    if rooms[current_room]['objects']:
        print("You see the following objects:", ", ".join(rooms[current_room]['objects']))
    print("Exits:")
    for direction, room in rooms[current_room]['exits'].items():
        locked_status = " (Locked)" if rooms[room].get('locked') else ""
        print(f"- {direction}: {room}{locked_status}")
    player['turns_left'] -= 1

def check_time():
    width = get_terminal_width()
    if player['turns_left'] <= 0:
        print("\nThe last of the night fades, and the first rays of dawn creep through the grimy windows.")
        print("You hear the distant rumble of heavy machinery getting closer...")
        print("A wrecking ball crashes through the front of the manor! You didn't make it in time.")
        return True
    return False

def check_final_room():
    global escape_mode  # Add this line here
    width = get_terminal_width()
    if player['location'] == final_room:
        if player['found_evidence'] < 3: # Still need the initial 3 pieces
            # ... (existing code for random accident in the attic) ...
            return True
        else:
            print("\nDust motes dance in the single ray of moonlight illuminating the attic.")
            print("Pinned to a crate, you find a newspaper clipping. The headline screams about survivors of a recent disaster...")
            print("As you read, a cold dread washes over you. The events described mirror your own recent past. There's even a picture of you! You realize...")
            print("Death has been following you. This manor... this was all a setup. You're in danger! Time to escape!")
            escape_mode = True # Set a flag indicating escape mode
            return False # Game continues, player needs to escape
    elif player['location'] == "Front Porch" and escape_mode: # Check if in escape mode and at the front porch
        num_keys = sum(1 for item in player['inventory'] if item.endswith(" Key"))
        print("\nYou burst through the front door, the chilling realization about Death's plan still echoing in your mind.")
        print("You manage to stumble off the porch, gasping for breath, just as a monstrous sound fills the air.")
        print("The ground trembles, and the silhouette of a massive wrecking ball swings into view, obliterating the manor behind you.")

        if num_keys >= 3:
            print("\nThe weight of the keys in your pockets causes you to fall heavily, breaking through the rotted patio. You drop just low enough to avoid the initial impact of the wrecking ball.")
            print("However, the force of the impact sends debris flying back towards you. A large piece of splintered wood pierces your chest.")
            print("\nYou escaped the manor, but not Death's design.")
        elif num_keys == 1 or num_keys == 2:
            print("\nThe weight of the keys in your pockets causes you to fall slightly as you leave the porch. You manage to duck low, and the wrecking ball narrowly misses the top half of your head.")
            print("You survive the initial impact, but the shock and the near miss are too much. You collapse, your heart giving out.")
        else: # num_keys == 0
            print("\nYou sprint off the porch, light and agile. You manage to clear the immediate impact zone of the wrecking ball.")
            print("You survived... for now.") # Standard escape if no keys
            return True # Indicate a successful escape (for now)

        print("\nGame Over")
        return True # End the game in all key-related death scenarios
    return False

def list_actions():
    print("\nAvailable actions:")
    print("  look around - Observe your current surroundings in detail.")
    print("  go [direction] - Move to an adjacent room (north, south, east, west, upstairs, downstairs, inside).")
    print("  examine [object] - Look closely at something in the room.")
    print("  take [item] - Pick up an item.")
    print("  unlock [room] - Use a key to unlock a door.")
    print("  look in [container] - Look inside something like a drawer or cupboard.")
    print("  inventory - View items you are carrying.")
    print("  drop [item] - Drop an item from your inventory.")
    print("  time - Check the number of turns left.")
    print("  quit - End the game.")

print("Thanks for playing!")

    # Winning Condition (Reaching Front Porch with all evidence after the twist)
    if player['location'] == "Front Porch" and player['found_evidence'] == 3:
        print("\nYou burst through the front door, the chilling realization about Death's plan still echoing in your mind.")
        print("You manage to stumble off the porch, gasping for breath, the cold air stinging your lungs, a desperate reprieve earned in blood and fear.")
        print("A monstrous roar, the guttural cry of metal and destruction, rips through the pre-dawn silence. The very ground beneath your trembling feet begins to shudder violently.")
        print("Then you see it, a colossal shadow arcing against the bruised twilight sky - the wrecking ball, a mechanical leviathan of iron, swinging back with terrifying speed, an inevitable pendulum of doom.")
        print("\nYou survived the night, clawed your way through the macabre theater of Death's design, and found proof of its insidious work. But in that final, fleeting moment of triumph, a horrifying truth slams into you: Death is not a force you outrun; it is a patient hunter, always circling back, its will an unyielding decree.")
        print("A silent scream catches in your throat as the world dissolves into a deafening, apocalyptic impact. The last thing you feel is the crushing weight of oblivion, the manor and its secrets, and you, pulverized into dust and memory.")
        break

print("\nGame Over")

# Reset interaction counters when starting a new game in play_game()
def play_game():
    global player, ceiling_fan_pulled, escape_mode
    global sink_interactions, crate_interactions, stairs_interactions, bookshelves_interactions

    # Reset game state
    player = { ... }
    ceiling_fan_pulled = False
    escape_mode = False
    randomize_item_locations()

    # Reset interaction counters for a new game
    sink_interactions = 0
    crate_interactions = 0
    stairs_interactions = 0
    bookshelves_interactions = 0

    game_intro()
#######################
# Dennis MUD          #
# perform.py          #
# Copyright 2018-2020 #
# Michael D. Reiley   #
#######################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

from lib.color import *
import random

NAME = "perform"
CATEGORIES = ["actions","users"]
ALIASES = ["miracle", "cast", "ritual"]
SCOST=0
USAGE = "perform <ritual> <optional ...>"
DESCRIPTION = """Perform the ritual called <ritual>. 

Current rituals: telepathy, identify, reveal, seer, ghost, cleanse.

TELEPATHY can send someone an anonymous message.
IDENTIFY can show you additional information about an object.
REVEAL can reveal hidden things in a room.
SEER can show you information about the location of someone.
GHOST can hide you almost completely for continual spirit cost.
CLEANSE can cleanse someone and the cursed items they have.
WHIRLPOOL can teleport an asleep player to a random room.

Ex. `perform telepathy seisatsu Hello there!`
Ex1. `perform reveal`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1, awake=True):
        return False

    #elif args[0]=="force":
    #    console.msg("Not implemented yet.")
    #    return False
    #print(args)
    if args[0]=="whirlpool":
        SCOST=5
        # Make sure the named user exists, is online, and is in the same room as us.
        thisreceiver=' '.join(args[1:])
        #print(thisreceiver)
        targetuser = COMMON.check_user(NAME, console, thisreceiver, room=True, online=True, live=True, reason=False,
                                   wizardskip=["room", "online"])
        if not targetuser:
            # Check for a partial user match, and try running again if there's just one.
            partial = COMMON.match_partial(NAME, console, thisreceiver.lower(), "user")
            if partial:
                partial=["whirlpool"]+partial
                return COMMAND(console, partial)
            console.msg("{0}: No such user in this room.".format(NAME))
            return False

        # Found the user, wake them up!
        userconsole = console.shell.console_by_username(targetuser["name"])
        if not userconsole:
            return False
        elif userconsole["posture"]=="sleeping":
            console.shell.broadcast_room(console,"{0} whispers some words in the ears of {1}.".format(console.user["nick"],targetuser["nick"]))
            destroom=random.choice(console.database.rooms.all())
            #destroom = COMMON.check_room(NAME, console, roomsc)
            thisroom = COMMON.check_room(NAME, console, console.user["room"])
            # The telekey is paired to a nonexistent room. Report and ignore it.
            if not destroom:
                console.msg("{0}: ERROR: Tried to teleport a sleeper into a nonexistent room!".format(NAME))
                console.log.error("Tried to teleport a sleeper into a nonexistent room!")

            # Proceed with teleportation.
            else:
                if userconsole["posture_item"]: userconsole["posture_item"]=""
                # Remove us from the current room.
                if targetuser["name"] in thisroom["users"]:
                    thisroom["users"].remove(targetuser["name"])

                # Add us to the destination room.
                if targetuser["name"] not in destroom["users"]:
                    destroom["users"].append(targetuser["name"])

                # Broadcast our teleportation to the origin room.
                console.shell.broadcast_room(console, "{0} vanished from the room.".format(targetuser["nick"]))

                # Set our current room to the new room.
                targetuser["room"] = destroom["id"]

                # Broadcast our arrival to the destination room, but not to ourselves.
                console.shell.broadcast_room(userconsole, "{0} appeared.".format(targetuser["nick"]))

                # Save the origin room, the destination room, and our user document.
                console.database.upsert_room(thisroom)
                console.database.upsert_room(destroom)
                console.database.upsert_user(targetuser)

                # Update console's exit list.
                userconsole.exits = []
                for exi in range(len(destroom["exits"])):
                    userconsole.exits.append(destroom["exits"][exi]["name"])

                # Take a look around.
                # console.shell.command(console, "look", False)
        else:
            if userconsole.user["pronouns"]=="male":
                console.msg("He is not asleep.")
            elif userconsole.user["pronouns"]=="female":
                console.msg("She is not asleep.")
            elif userconsole.user["pronouns"]=="neutral":
                console.msg("They are not asleep.")
            else: console.msg("{0} is not asleep.".format(userconsole.user["pronouns"].capitalize()))
            return False
    elif args[0]=="cleanse":
        SCOST=5
        #if thisreceiver==console.user["name"] or thisreceiver==console.user["nick"] or thisreceiver==console.user["nick"].lower():
        #    console.msg("Can't cleanse yourself.")
        #    return False        
        if not COMMON.check(NAME, console, args, argmin=2, spiritcost=SCOST, spiritenabled=CONFIG["spiritenabled"], awake=True):
            return False

        thisreceiver = ' '.join(args[1:])
        targetuser = COMMON.check_user(NAME, console, thisreceiver, room=True, online=True, live=True, reason=False,
                                   wizardskip=["room", "online"])
        if not targetuser:
            # Check for a partial user match, and try running again if there's just one.
            partial = COMMON.match_partial(NAME, console, thisreceiver, "user", message=False)
            if partial:
                return COMMAND(console,["cleanse"]+partial)
            console.msg("{0}: No such user in this room.".format(NAME))
            return False
        if console.user["name"]==targetuser["name"]:
            if console.user["pronouns"]=="male":
                msg = "{0} focuses on himself for a moment.".format(console.user["nick"])
            elif console.user["pronouns"]=="female":
                msg = "{0} focuses on herself for a moment.".format(console.user["nick"])
            elif console.user["pronouns"]=="neutral":
                msg = "{0} focuses on themself for a moment.".format(console.user["nick"])
            else:
                msg = "{0} focuses on {1}self for a moment.".format(console.user["nick"],console.user["pronouno"])
        else:
            msg = "{0} focuses on {1} for a moment.".format(console.user["nick"],targetuser["nick"])
        console.shell.broadcast_room(console, msg)
        
        for it in targetuser["inventory"]:
            thisitem = COMMON.check_item(NAME, console, it, owner=False, holding=False)
            if thisitem["cursed"]["enabled"]:
                thisitem["cursed"]["enabled"]=False
                console.database.upsert_item(thisitem)
                if not console.user["name"]==targetuser["name"]:
                    console.shell.msg_user(targetuser["name"],"{0} cleansed some of your items.".format(console.user["nick"]))
                    if targetuser["pronouns"]=="male":
                        console.msg("You cleansed some of his items.")
                    elif targetuser["pronouns"]=="female":
                        console.msg("You cleansed some of her items.")
                    elif targetuser["pronouns"]=="neutral":
                        console.msg("You cleansed some of their items.")
                    else:
                        console.msg("You cleansed some of {0} items.".format(targetuser["pronouno"]))
                else:
                    console.msg("You cleansed some of your items.")
        return True

    elif args[0]=="seer":
        # Spirit cost of telepathy.
        SCOST=5
        if not COMMON.check(NAME, console, args, argmin=2, spiritcost=SCOST, spiritenabled=CONFIG["spiritenabled"]):
            return False
        thisreceiver = ' '.join(args[1:])
        # Make sure the named user exists and is online.
        targetuser = COMMON.check_user(NAME, console, thisreceiver, online=True)

        if not targetuser:
            # Check for a partial user match, and try running again if there's just one.
            partial = COMMON.match_partial(NAME, console, thisreceiver, "user", message=False)
            if partial:
                return COMMAND(console,["seer"]+partial)
            console.msg("{0}: No such user was found.".format(NAME))
            return False

        # Look up room.
        targetroom = COMMON.check_room(NAME, console, roomid=targetuser["room"])
        msg = "{0} looks into the distance for a moment.".format(console.user["nick"])
        console.shell.broadcast_room(console, msg)
        #console.msg("You see a vision... \n{0}\n{1}".format(targetroom["name"], targetroom["desc"]))
        console.msg("You see a vision... \n{0}\nThe vision ends...".format(targetroom["desc"]))
        return True
    
    elif args[0]=="ghost":
        SCOST=50
        if not COMMON.check(NAME, console, args, argmax=1, spiritcost=SCOST, spiritenabled=CONFIG["spiritenabled"]):
            return False
        if console.user["ghost"]:
            console.user["spirit"]+=50
            msg = "{0} suddenly appears.".format(console.user["nick"])
            console.shell.broadcast_room(console, msg)
            console.user["ghost"]=False
        else:
            msg = "{0} mutters a few words and disappears.".format(console.user["nick"])
            console.shell.broadcast_room(console, msg)
            console.user["ghost"]=True
        console.database.upsert_user(console.user)
        return True
        
    elif args[0]=="reveal":
        SCOST=5
        if not COMMON.check(NAME, console, args, argmax=1, spiritcost=SCOST, spiritenabled=CONFIG["spiritenabled"]):
            return False
        msg = "{0} tries to reveal hidden things with a ritual.".format(console.user["nick"])
        console.shell.broadcast_room(console, msg)
        destroom = COMMON.check_room(NAME,console)
        dexits = destroom["exits"]
        for dex in range(len(dexits)):
            # Check for randomized chance
            if dexits[dex]["chance"] and dexits[dex]["hidden"]==True:
                if random.randint(1,dexits[dex]["chance"])==1: 
                    dexits[dex]["hidden"]=False

        # Random items check.
        ditems = destroom["items"]
        for dit in ditems:
            dit = console.database.item_by_id(dit)
            # Check for randomized chance
            if dit["chance"] and dit["hidden"]==True:
                if dit["truehide"]==True:
                    console.msg("You sense {0} being hidden around here.".format(COMMON.format_item(NAME, dit["name"])))
                elif random.randint(1,dit["chance"])==1: 
                    #dit["truehide"]=False
                    dit["hidden"]=False
                # A small chance to reveal truly hidden stuff.
                    
        #for uss in destroom["users"]:
        #    duss = console.database.user_by_name(uss)
        #    if duss["ghost"]:
        #        if random.randint(1,4)==1:
        #            duss["ghost"]=False
        #            console.shell.msg_user(duss["name"],"Someone revealed you.")            
        return True

    elif args[0]=="identify":
        # Spirit cost of identify.
        SCOST=2
        found_something = False
        partials = []
        target=' '.join(args[1:])
        if not COMMON.check(NAME, console, args, argmin=2, spiritcost=SCOST, spiritenabled=CONFIG["spiritenabled"]):
            return False
                        
        # Lookup the current room and perform room checks.
        thisroom = COMMON.check_room(NAME, console)
        if not thisroom:
            return False

        # It wasn't us, so maybe it's an item in the room.
        for itemid in thisroom["items"]:
            item = console.database.item_by_id(itemid)
            # A reference was found to a nonexistent item. Report this and continue searching.
            if not item:
                console.log.error("Item referenced in room does not exist: {room} :: {item}", room=console.user["room"],
                                  item=itemid)
                console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, itemid))
                continue
            attributes = []

            # Record partial matches.
            if target in item["name"].lower() or target.replace("the ", "", 1) in item["name"].lower():
                partials.append(item["name"].lower())

            # It was an item in the room. Show the item's name, ID, owners, description, and attributes.
            if target in [item["name"].lower(), "the " + item["name"].lower()]:
                # Only enumerate item attributes if we are the item owner or a wizard.
                if item["duplified"]:
                    attributes.append("This thing can be anywhere, somehow at the same time.")
                if item["cursed"]["enabled"]:
                    attributes.append("A dark presence haunts it.")
                if item["glued"]:
                    attributes.append("This object can't be carried with you.")
                if item["truehide"]:
                    attributes.append("Maybe it's invisible, but something truly hides it from sight.")
                if item["hidden"]:
                    attributes.append("Somehow it blends into it's environment.")
                if item["lang"]:
                    attributes.append("You sense that this thing can teach you and alter your language.")
                if item["container"]["enabled"]:
                    attributes.append("Something else could easily fit into the insides of this object.")
                if item["telekey"]:
                    attributes.append("Using this thing would take you somewhere else.")

                # Send the info for this item.
                if len(attributes)>0:
                    console.msg("You sense the {0}. {1}".format(item["name"], ' '.join(attributes)))    
                else:
                    console.msg("You sense the {0}.".format(item["name"]))
                console.msg("It seems to be connected to {0}.".format(', '.join(item["owners"])))

                # Description exists, so show it.
                #if item["desc"]:
                #    console.msg(item["desc"])

                # List content if it's a container
                if item["container"]["enabled"]:
                    if len(item["container"]["inventory"])>0:
                        console.msg("{0} seems to contain some items.".format(item["name"].capitalize()))
                    else:
                        console.msg("{0} seems to be empty.".format(item["name"].capitalize()))
                found_something = True
                msg = "{0} performs a ritual of knowledge.".format(console.user["nick"])
                console.shell.broadcast_room(console, msg)
                return True

        # Maybe it's an item in our inventory.
        for itemid in console.user["inventory"]:
            item = console.database.item_by_id(itemid)
            # A reference was found to a nonexistent item. Report this and continue searching.
            if not item:
                console.log.error("Item referenced in user inventory does not exist: {user} :: {item}",
                                  user=console.user["name"], item=itemid)
                console.msg("{0}: ERROR: Item referenced in your inventory does not exist: {1}".format(NAME, itemid))
                continue
            attributes = []

            # Record partial matches.
            if target in item["name"].lower() or target.replace("the ", "", 1) in item["name"].lower():
                partials.append(item["name"].lower())

            # It was an item in our inventory. Show the item's name, ID, owners, description, and attributes,
            # but only if we didn't already see it in the current room. Also check if the user prepended "the ".
            if target in [item["name"].lower(), "the " + item["name"].lower()]:
                # Only enumerate item attributes if we are the item owner or a wizard.
                if item["duplified"]:
                    attributes.append("This thing can be anywhere, somehow at the same time.")
                if item["cursed"]["enabled"]:
                    attributes.append("A dark presence haunts it.")
                if item["glued"]:
                    attributes.append("This object can't be carried with you.")
                if item["truehide"]:
                    attributes.append("Maybe it's invisible, but something truly hides it from sight.")
                if item["hidden"]:
                    attributes.append("Somehow it blends into it's environment.")
                if item["lang"]:
                    attributes.append("You sense that this thing can teach you and alter your language.")
                if item["container"]["enabled"]:
                    attributes.append("Something else could easily fit into the insides of this object.")
                if item["telekey"]:
                    attributes.append("Using this thing would take you somewhere else.")

                # Send the info for this item.
                if len(attributes)>0:
                    console.msg("You sense the {0}. {1}".format(item["name"], ' '.join(attributes)))    
                else:
                    console.msg("You sense the {0}.".format(item["name"]))
                console.msg("It seems to be connected to {0}.".format(', '.join(item["owners"])))

                # Description exists, so show it.
                #if item["desc"]:
                #    console.msg(item["desc"])

                # List content if it's a container
                if item["container"]["enabled"]:
                    if len(item["container"]["inventory"])>0:
                        console.msg("{0} seems to contain some items.".format(item["name"].capitalize()))
                    else:
                        console.msg("{0} seems to be empty.".format(item["name"].capitalize()))

                found_something = True
                msg = "{0} performs a ritual of knowledge.".format(console.user["nick"])
                console.shell.broadcast_room(console, msg)
                return True
        # We didn't find anything by that name. See if we found partial matches.
        if not found_something:
            # Eliminate duplicate matches.
            if partials:
                partials = list(dict.fromkeys(partials))

            # We got exactly one partial match. Assume that one.
            if len(partials) == 1:
                #console.msg("Assuming {0}.".format(partials[0]))
                console.user["spirit"]+=SCOST
                partials[0]="identify "+partials[0]
                return COMMAND(console, partials[0].split(' '))

            # We got up to 5 partial matches. List them.
            elif partials and len(partials) <= 5:
                console.msg("{0}: Did you mean one of: {1}".format(NAME, ', '.join(partials)))
                return False

            # We got too many matches.
            elif len(partials) > 5:
                console.msg("{0}: Too many possible matches.".format(NAME))
                return False

            # Really nothing.
            else:
                console.msg("{0}: No such thing: {1}".format(NAME, ' '.join(args[1:])))
            return False
        
    elif args[0]=="telepathy":
        # Spirit cost of telepathy.
        SCOST=5
        if not COMMON.check(NAME, console, args, argmin=3, spiritcost=SCOST, spiritenabled=CONFIG["spiritenabled"]):
            return False
        
        # Make sure the named user exists and is online.
        targetuser = COMMON.check_user(NAME, console, args[1].lower(), online=True)
        if not targetuser:
            return False

        # Finished. Message the user, and echo the message to ourselves, if it wasn't a self-message.
        console.shell.msg_user(args[1].lower(), mcolor(CBYELLO,"You hear a whisper in your mind: '{0}'".format(' '.join(args[2:])),targetuser["colors"]))
        if targetuser["name"] != console.user["name"]:
            console.msg(mcolor(CBYELLO,"You plant a message in the mind of {0}, that says: '{1}'".format(targetuser["name"], ' '.join(args[2:])),console.user["colors"]))
        msg = "{0} focuses for a moment to perform a ritual.".format(console.user["nick"])
        console.shell.broadcast_room(console, msg)
        return True
    else:
        console.msg("You never heard of such a ritual.")
        return False


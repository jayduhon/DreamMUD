#######################
# Dennis MUD          #
# lock.py             #
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
from lib.litnumbers import *

NAME = "look"
CATEGORIES = ["exploration"]
ALIASES = ["look at", "l", "examine", "x"]
USAGE = "look [name]"
DESCRIPTION = """Look at the current room or the named object or user.

If used by itself without any arguments, this command gives information about the current room.
Otherwise, you can look at yourself, an item in the room or your inventory, or an exit.
You can also look at a user by their username or their nickname.
Look does not work on IDs, a name is required. Partial matches will work.

Ex. `look` to look at the current room.
Ex2. `look self` to look at yourself.
Ex3. `look at crystal ball` to look at the item "crystal ball".
Ex4. `l ball` to look at the item "crystal ball".
Ex5. `examine crys` to look at the item "crystal ball"."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, awake=True):
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    # There were no arguments, so just look at the current room.
    if len(args) == 0:
        # Show the room name, ID, owners, and description.
        if console.user["builder"]["enabled"]: console.msg("{0} (ID: {1})".format(mcolor(CCYAN,thisroom["name"],console.user["colors"]),thisroom["id"]))
        else: console.msg(mcolor(CCYAN,thisroom["name"],console.user["colors"]))
        if console.user["builder"]["enabled"]: console.msg("Owned by: {0}".format(', '.join(thisroom["owners"])))
        if thisroom["desc"]:
            console.msg(thisroom["desc"])
        else:
            console.msg("A room of void, a room of nothingness.") # Print default no-desc message.

        # Build and show the user list.
        userlist = []
        for user in thisroom["users"]:
            if console.database.user_by_name(user)["ghost"]!=True: userlist.append(console.database.user_by_name(user)["nick"])
        if len(userlist)>2:
            for aex in range(len(userlist)):
                if aex==len(userlist)-1: userlist[aex]="and "+userlist[aex]
                elif aex==len(userlist)-2: userlist[aex]=userlist[aex]+" "
                else: userlist[aex]=userlist[aex]+", " 
            console.msg(mcolor(CYELLO,"\n{0} are here.".format("".join(userlist)),console.user["colors"]))
        elif len(userlist)==2:
            console.msg(mcolor(CYELLO,"\n{0} are here.".format(" and ".join(userlist)),console.user["colors"]))
        elif len(userlist)==1:
            console.msg(mcolor(CYELLO,"\n{0} is here.".format(" ".join(userlist)),console.user["colors"]))

        # Build and show the item list.
        itemlist = []
        for itemid in thisroom["items"]:
            item = console.database.item_by_id(itemid)
            if item:
                if item["hidden"] == False:
                    if console.user["builder"]["enabled"]: itemlist.append("{0} (ID: {1})".format(item["name"], item["id"]))
                    else: itemlist.append("{0}".format(item["name"]))
                elif (console.user["wizard"] and item["hidden"] == True):
                    if console.user["builder"]["enabled"]: itemlist.append("{0} (ID: {1}) (Hidden)".format(item["name"], item["id"]))
                    else: itemlist.append("{0} (Hidden)".format(item["name"]))
            else:
                console.log.error("Item referenced in room does not exist: {room} :: {item}", room=console.user["room"],
                                  item=itemid)
                console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, itemid))
        if itemlist:
            console.msg(mcolor(CMAG,"Items: {0}.".format(", ".join(itemlist)),console.user["colors"]))

        # Build and show the exit list.
        exitlist = []
        for ex in range(len(thisroom["exits"])):
            if thisroom["exits"][ex]["hidden"]==False or console.user["wizard"]==True:
                if console.user["builder"]["enabled"]: exitlist.append("{0} (ID: {1})".format(thisroom["exits"][ex]["name"].lower(), ex))
                else: exitlist.append("{0}".format(thisroom["exits"][ex]["name"].lower()))
        if exitlist:
            #console.msg(mcolor(CGRN,"Exits: {0}".format(", ".join(exitlist)),console.user["colors"]["enabled"]))
            if(len(exitlist)>2):
                for aex in range(len(exitlist)):
                    if aex==len(exitlist)-1: exitlist[aex]="and "+exitlist[aex]
                    elif aex==len(exitlist)-2: exitlist[aex]=exitlist[aex]+" "
                    else: exitlist[aex]=exitlist[aex]+", "
            elif (len(exitlist)==2):
                    exitlist.insert(1, " and ") 
            console.msg(mcolor(CGRN,"You can go {0} from here.".format("".join(exitlist)),console.user["colors"]))
        else:
            console.msg(mcolor(CGRN,"No exits in this room. Make one or use `xyzzy` to return to the first room.",console.user["colors"]))
        return True

    # There were arguments. Figure out what in the room they might be referring to.
    # Also keep track of whether we found anything, and whether we found a certain item
    # in the current room so we don't list it twice if it was duplified and also in our inventory.
    else:
        # See if the user tried to look at an ID instead of a name.
        try:
            int(' '.join(args))
            console.msg("{0}: Requires a name, not an ID.".format(NAME))
            return False

        # Nope, just looking for something that isn't there.
        except:
            pass

        # Keep track of whether we found stuff during our search.
        found_something = False
        found_item = None
        partials = []

        # Save a bit of line space.
        target = ' '.join(args).lower()
        if target == "the":
            console.msg("{0}: Very funny.".format(NAME))
            return False

        # Looking at ourselves. Show user nickname real name, and description.
        if target in ["self","me","myself"]:
            found_something=True
            console.msg("{0} ({1})".format(console.user["nick"], console.user["name"]))

            # Description exists, so show it.
            if console.user["desc"]:
                console.msg(console.user["desc"])

            # Some message about our spirit. Currently just the number.
            if console.user["spirit"] and not console.user["wizard"]: 
                console.msg("Your current spirit seems to be at {0}%.".format(str(console.user["spirit"])))
            else:
                console.msg("Your spirit is completely depleted.")
            # Holding stuff
            if len(console.user["equipment"])>0:
                #Currently only 1 item is supported
                hitem = console.database.item_by_id(console.user["equipment"][0])
                console.msg("\nYou are holding {0}.".format(COMMON.format_item(NAME, hitem["name"])))
                    
            
            # If we are sitting or laying down, format a message saying so after the description.
            if console["posture"] and console["posture_item"]:
                console.msg("\nYou are {0} on {1}.".format(console["posture"],COMMON.format_item(NAME, console["posture_item"])))
            elif console["posture"]:
                console.msg("\nYou are {0}.".format(console["posture"]))
            return True
            
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
                if console.user["name"] in item["owners"] or console.user["wizard"]:
                    if item["duplified"]:
                        attributes.append("[duplified]")
                    if item["container"]["enabled"]:
                        attributes.append("[container]")
                    if item["glued"]:
                        attributes.append("[glued]")
                    if item["cursed"]["enabled"]:
                        attributes.append("[cursed]")
                    if item["truehide"]:
                        attributes.append("[hidden]")
                    if item["lang"]:
                        attributes.append("[language book]")
                    if item["telekey"] is not None:
                        attributes.append("[telekey:{0}]".format(item["telekey"]))

                # Send the info for this item.
                if console.user["builder"]["enabled"]: console.msg("{0} (ID: {1}) {2}".format(item["name"], item["id"], ' '.join(attributes)))
                else: console.msg("{0} {1}".format(item["name"], ' '.join(attributes)))
                if console.user["builder"]["enabled"]: console.msg("Owned by: {0}".format(', '.join(item["owners"])))

                # Description exists, so show it.
                if item["desc"]:
                    console.msg(item["desc"])
                else:
                    console.msg(CONFIG["nodesc"]) # Print default no-desc message.

                # List content if it's a container
                if item["container"]["enabled"]:
                    citemlist=[]
                    for c in range(len(item["container"]["inventory"])):
                        citem=console.database.item_by_id(item["container"]["inventory"][c])
                        if console.user["builder"]["enabled"]: citemlist.append("{0} (ID: {1})".format(citem["name"],item["container"]["inventory"][c]))
                        else: citemlist.append(citem["name"])
                    if len(citemlist)>0:
                        console.msg("Contains the following items: {0}".format(', '.join(citemlist)))
                    else:
                        console.msg("{0} seems to be empty.".format(item["name"].capitalize()))
                found_something = True
                found_item = itemid
                break

        # Maybe it's an item in our inventory.
        for itemid in console.user["inventory"]+console.user["equipment"]:
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
            if target in [item["name"].lower(), "the " + item["name"].lower()] and item["id"] != found_item:
                # Only enumerate item attributes if we are the item owner or a wizard.
                if console.user["name"] in item["owners"] or console.user["wizard"]:
                    if item["duplified"]:
                        attributes.append("[duplified]")
                    if item["glued"]:
                        attributes.append("[glued]")
                    if item["truehide"]:
                        attributes.append("[hidden]")
                    if item["cursed"]["enabled"]:
                        attributes.append("[cursed]")
                    if item["lang"]:
                        attributes.append("[language book]")
                    if item["container"]["enabled"]:
                        attributes.append("[container]")
                    if item["telekey"]:
                        attributes.append("[telekey:{0}]".format(item["telekey"]))

                # Send the info for this item.
                if console.user["builder"]["enabled"]: console.msg("{0} (ID: {1}) {2}".format(item["name"], item["id"], ' '.join(attributes)))
                else:  console.msg("{0}".format(item["name"]))
                if console.user["builder"]["enabled"]: console.msg("Owned by: {0}".format(', '.join(item["owners"])))

                # Description exists, so show it.
                if item["desc"]:
                    console.msg(item["desc"])  # Print item description.
                else:
                    console.msg(CONFIG["nodesc"]) # Print default no-desc message.

                # List content if it's a container
                if item["container"]["enabled"]:
                    citemlist=[]
                    for c in range(len(item["container"]["inventory"])):
                        citem=console.database.item_by_id(item["container"]["inventory"][c])
                        if console.user["builder"]["enabled"]: citemlist.append("{0} (ID: {1})".format(citem["name"],item["container"]["inventory"][c]))
                        else: citemlist.append(citem["name"])
                    if len(citemlist)>0:
                        console.msg("Contains the following items: {0}.".format(', '.join(citemlist)))
                    else:
                        console.msg("{0} seems to be empty.".format(item["name"].capitalize()))

                found_something = True
                break

        # Maybe it's an exit in the room.
        for ex in range(len(thisroom["exits"])):
            # Record partial matches.
            if target in thisroom["exits"][ex]["name"].lower() or \
                    target.replace("the ", "", 1) in thisroom["exits"][ex]["name"].lower():
                partials.append(thisroom["exits"][ex]["name"].lower())

            # It was an exit in the current room. Show the exit name, destination,
            # description, ID, owners, and any key information.
            if target in [thisroom["exits"][ex]["name"].lower(), "the " + thisroom["exits"][ex]["name"].lower()]:
                if console.user["builder"]["enabled"]: 
                    console.msg("{0} (ID: {1}) leads to ID: {2}".format(thisroom["exits"][ex]["name"], ex, thisroom["exits"][ex]["dest"]))
                    console.msg("Owned by: {0}".format(', '.join(thisroom["exits"][ex]["owners"])))

                # Description exists, so show it.
                if thisroom["exits"][ex]["desc"]:
                    console.msg(thisroom["exits"][ex]["desc"])
                else:
                    console.msg(CONFIG["nodesc"]) # Print default no-desc message.

                # Key info is visible or we own the exit or are a wizard, so show it.
                if thisroom["exits"][ex]["key"] and (console.user["name"] in thisroom["exits"][ex]["owners"]
                                                     or console.user["wizard"]
                                                     or not thisroom["exits"][ex]["key_hidden"]):
                    item = console.database.item_by_id(thisroom["exits"][ex]["key"])
                    # Key does not exist, remove it and log the event.
                    if not item:
                        console.log.error("Key item referenced in the exit does not actually exist: {thisitem}",
                                          thisitem=exits[ex]["key"])
                        exits[ex]["key"]=None
                        console.database.upsert_room(thisroom)
                    if console.user["builder"]["enabled"]: console.msg("Unlocked with: {0} (ID: {1})".format(item["name"], item["id"]))
                    else: console.msg("Unlocked with: {0}.".format(item["name"]))
                found_something = True
                break

        # Maybe it's the username of a user.
        # Record partial matches.
        for username in thisroom["users"]:
            if target in username:
                partials.append(username)

        # Look for an exact username match.
        user = console.database.user_by_name(target)
        if user and console.database.online(user["name"]) and user["name"] in thisroom["users"]:
            console.msg("{0} ({1})".format(user["nick"], user["name"]))

            # Description exists, so show it.
            if user["desc"]:
                console.msg(user["desc"])  # Print user description.
            else:
                if user["pronouns"] == "male": console.msg("Nothing unusual about him.")
                elif user["pronouns"] == "female": console.msg("Nothing unusual about her.")
                elif user["pronouns"] == "neutral": console.msg("Nothing unusual about them.")
                else: console.msg("Nothing unusual about {0}.".format(user["pronouno"].capitalize()))  # Print user description.

            # If they are sitting or laying down, format a message saying so after the description.
            userconsole = console.shell.console_by_username(user["name"])
            if user["pronouns"] == "female":
                
                # Holding stuff
                if len(user["equipment"])>0:
                    #Currently only 1 item is supported
                    hitem = console.database.item_by_id(user["equipment"][0])
                    console.msg("\nShe is holding {0}.".format(COMMON.format_item(NAME, hitem["name"])))   
                
                if userconsole["posture"] and userconsole["posture_item"]:
                    console.msg("\nShe is {0} on {1}.".format(userconsole["posture"],
                                                              COMMON.format_item(NAME, userconsole["posture_item"])))
                elif userconsole["posture"]:
                    console.msg("\nShe is {0}.".format(userconsole["posture"]))
            elif user["pronouns"] == "male":
                if len(user["equipment"])>0:
                    #Currently only 1 item is supported
                    hitem = console.database.item_by_id(user["equipment"][0])
                    console.msg("\nHe is holding {0}.".format(COMMON.format_item(NAME, hitem["name"])))
                
                if userconsole["posture"] and userconsole["posture_item"]:
                    console.msg("\nHe is {0} on {1}.".format(userconsole["posture"],
                                                             COMMON.format_item(NAME, userconsole["posture_item"])))
                elif userconsole["posture"]:
                    console.msg("\nHe is {0}.".format(userconsole["posture"]))
            elif user["pronouns"] == "neutral":
                if len(user["equipment"])>0:
                    #Currently only 1 item is supported
                    hitem = console.database.item_by_id(user["equipment"][0])
                    console.msg("\nThey are holding {0}.".format(COMMON.format_item(NAME, hitem["name"])))
                
                if userconsole["posture"] and userconsole["posture_item"]:
                    console.msg("\nThey are {0} on {1}.".format(userconsole["posture"],
                                                             COMMON.format_item(NAME, userconsole["posture_item"])))
                elif userconsole["posture"]:
                    console.msg("\nThey are {0}.".format(userconsole["posture"]))
            else:
                if len(user["equipment"])>0:
                    #Currently only 1 item is supported
                    hitem = console.database.item_by_id(user["equipment"][0])
                    console.msg("\n{0} is holding {1}.".format(user["pronouns"].capitalize(),COMMON.format_item(NAME, hitem["name"])))
                
                if userconsole["posture"] and userconsole["posture_item"]:
                    console.msg("\n{0} is {1} on {2}.".format(user["pronouns"].capitalize(),userconsole["posture"],
                                                                COMMON.format_item(NAME, userconsole["posture_item"])))
                elif userconsole["posture"]:
                    console.msg("\n{0} is {1}.".format(user["pronouns"].capitalize(),userconsole["posture"]))
            found_something = True
        
        if not found_something:
            # Maybe it's the nickname of a user.
            # Record partial matches.
            for username in thisroom["users"]:
                usertemp = console.database.user_by_name(username)
                if usertemp:
                    if target.lower() in usertemp["nick"].lower():
                        partials.append(usertemp["nick"])

            # Look for an exact nickname match.
            user = console.database.user_by_nick(target)
            if user and console.database.online(user["name"]):
                console.msg("{0} ({1})".format(user["nick"], user["name"]))

                # Description exists, so show it.
                if user["desc"]:
                    console.msg(user["desc"])  # Print user description.

                # If they are sitting or laying down, format a message saying so after the description.
                userconsole = console.shell.console_by_username(user["name"])
                if user["pronouns"] == "female":
                    # Holding stuff
                    if len(user["equipment"])>0:
                        #Currently only 1 item is supported
                        hitem = console.database.item_by_id(user["equipment"][0])
                        console.msg("\nShe is holding {0}.".format(COMMON.format_item(NAME, hitem["name"])))
                    
                    if userconsole["posture"] and userconsole["posture_item"]:
                        console.msg("\nShe is {0} on {1}.".format(userconsole["posture"],
                                                                  COMMON.format_item(NAME, userconsole["posture_item"])))
                    elif userconsole["posture"]:
                        console.msg("\nShe is {0}.".format(userconsole["posture"]))
                elif user["pronouns"] == "male":
                    # Holding stuff
                    if len(user["equipment"])>0:
                        #Currently only 1 item is supported
                        hitem = console.database.item_by_id(user["equipment"][0])
                        console.msg("\nHe is holding {0}.".format(COMMON.format_item(NAME, hitem["name"])))
                        
                    if userconsole["posture"] and userconsole["posture_item"]:
                        console.msg("\nHe is {0} on {1}.".format(userconsole["posture"],
                                                                 COMMON.format_item(NAME, userconsole["posture_item"])))
                    elif userconsole["posture"]:
                        console.msg("\nHe is {0}.".format(userconsole["posture"]))
                elif user["pronouns"] == "neutral":
                    # Holding stuff
                    if len(user["equipment"])>0:
                        #Currently only 1 item is supported
                        hitem = console.database.item_by_id(user["equipment"][0])
                        console.msg("\nThey are holding {0}.".format(COMMON.format_item(NAME, hitem["name"])))
                    
                    if userconsole["posture"] and userconsole["posture_item"]:
                        console.msg("\nThey are {0} on {1}.".format(userconsole["posture"],
                                                                 COMMON.format_item(NAME, userconsole["posture_item"])))
                    elif userconsole["posture"]:
                        console.msg("\nThey are {0}.".format(userconsole["posture"]))
                else:
                    # Holding stuff
                    if len(user["equipment"])>0:
                        #Currently only 1 item is supported
                        hitem = console.database.item_by_id(user["equipment"][0])
                        console.msg("\n{0} is holding {1}.".format(user["pronouns"].capitalize(),COMMON.format_item(NAME, hitem["name"])))
                    
                    if userconsole["posture"] and userconsole["posture_item"]:
                        console.msg("\n{0} is {1} on {2}.".format(user["pronouns"].capitalize(),userconsole["posture"],
                                                                    COMMON.format_item(NAME, userconsole["posture_item"])))
                    elif userconsole["posture"]:
                        console.msg("\n{0} is {1}.".format(user["pronouns"].capitalize(),userconsole["posture"]))
                found_something = True

        # We didn't find anything by that name. See if we found partial matches.
        if not found_something:
            # Eliminate duplicate matches.

            if partials:
                partials = list(dict.fromkeys(partials))

            # We got exactly one partial match. Assume that one.
            if len(partials) == 1:
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
                console.msg("{0}: No such thing: {1}".format(NAME, ' '.join(args)))
            return False

        # Finished.
        return True

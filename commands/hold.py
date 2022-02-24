#######################
# Dennis MUD          #
# hold.py             #
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

NAME = "hold"
CATEGORIES = ["items"]
ALIASES = ["wear","wield"]
USAGE = "hold <item>"
DESCRIPTION = """Hold the item called <item>.

You may use a full or partial item name, or the item ID.
At the moment you can only hold a single item.

Ex. `hold crystal ball`
Ex2. `hold 4`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1, awake=True):
        return False

    # Get item name/id.
    target = ' '.join(args).lower()
    if target == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False
    
    # Currently only 2 items are supported.
    if len(console.user["equipment"])>1:
        console.msg("Your hands are full.")
        return False
    
    # Search our inventory for the target item.
    for itemid in console.user["inventory"]:
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid, reason=False)
        if not thisitem:
            console.log.error("Item referenced in room does not exist: {room} :: {item}", room=console.user["room"],
                              item=itemid)
            console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, itemid))
            continue

        # Check for name or id match. Also check if the user prepended "the ". Figure out how to hold it.
        if target in [thisitem["name"].lower(), "the " + thisitem["name"].lower()] or str(thisitem["id"]) == target:
            # Only non-owners lose duplified items when holding them.
            if thisitem["id"] in console.user["equipment"]:
                console.msg("{0}: You are already holding this item.".format(NAME))
            else:
                console.user["inventory"].remove(thisitem["id"])
                console.user["equipment"].append(thisitem["id"])
                console.shell.broadcast_room(console, "{0} starts to hold {1}.".format(console.user["nick"], COMMON.format_item(NAME, thisitem["name"])))            
                # Update the user document.
                console.database.upsert_user(console.user)
            # Finished.
            return True

    # We didn't find the requested item. Check for a partial match.
    partial = COMMON.match_partial(NAME, console, target, "item", room=False, inventory=True, equipment=False)
    if partial:
        return COMMAND(console, partial)

    # Maybe the user accidentally typed "hold item <item>".
    if args[0].lower() == "item":
        console.msg("{0}: Maybe you meant \"hold {1}\".".format(NAME, ' '.join(args[1:])))

    return False

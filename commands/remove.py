#######################
# Dennis MUD          #
# remove.py             #
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
# AUTHORS OR COPYRIGHT removeERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

NAME = "remove"
CATEGORIES = ["items"]
ALIASES = ["unwear","unwield"]
USAGE = "remove <item>"
DESCRIPTION = """Remove the item called <item> so you don't hold it any more.

You may use a full or partial item name, or the item ID.
At the moment you can only remove a single item.

Ex. `remove crystal ball`
Ex2. `remove 4`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Get item name/id.
    target = ' '.join(args).lower()
    if target == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Search our inventory for the target item.
    for itemid in console.user["equipment"]:
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid, reason=False)
        if not thisitem:
            console.log.error("Item referenced in room does not exist: {room} :: {item}", room=console.user["room"],
                              item=itemid)
            console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, itemid))
            continue

        # Check for name or id match. Also check if the user prepended "the ". Figure out how to remove it.
        if target in [thisitem["name"].lower(), "the " + thisitem["name"].lower()] or str(thisitem["id"]) == target:
            # Only non-owners lose duplified items when removeing them.
            if thisitem["id"] in console.user["inventory"]:
                console.msg("{0}: You already have this item in your inventory.".format(NAME))
            else:
                console.user["equipment"].remove(thisitem["id"])
                console.user["inventory"].append(thisitem["id"])
                console.shell.broadcast_room(console, "{0} stops holding {1}.".format(console.user["nick"], COMMON.format_item(NAME, thisitem["name"])))
                # Update the user document.
                console.database.upsert_user(console.user)
            # Finished.
            return True

    # We didn't find the requested item. Check for a partial match.
    partial = COMMON.match_partial(NAME, console, target, "item", room=False)
    if partial:
        return COMMAND(console, partial)

    # Maybe the user accidentally typed "remove item <item>".
    if args[0].lower() == "item":
        console.msg("{0}: Maybe you meant \"remove {1}\".".format(NAME, ' '.join(args[1:])))

    return False

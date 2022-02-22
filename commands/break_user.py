#######################
# Dennis MUD          #
# break_room.py       #
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

NAME = "break user"
CATEGORIES = ["wizard"]
ALIASES = ["delete user", "destroy user", "remove user"]
USAGE = "break user <username>"
DESCRIPTION = """(WIZARDS ONLY) Break the user with name <username>.

Or rather deletes a user. All ownership will be deleted, unowned items will be owned by <world>.

Ex. `break user alice` to remove the user called alice."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1, wizard=True):
        return False

    if "<world>" in args or args[0]=="<world>":
        console.msg("{0}: Not even a wizard should do that.".format(NAME))
        return False
        

    # Lookup the target room and perform room checks.
    targetuser = COMMON.check_user(NAME, console, args[0], offline=True)
    if not targetuser:
        return False

    # Make sure they are offline.
    #if targetroom["users"]:
    #    console.msg("{0}: You cannot break an occupied room.".format(NAME))
    #    return False

    for thisroom in console.database.rooms.all():
        # Lookup the target item and perform item checks.
        #thisroom = COMMON.check_room(NAME, console, roomid)
        if targetuser["name"] in thisroom["owners"]:
            if len(thisroom["owners"])<2: thisroom["owners"]=["<world>"]
            else: thisroom["owners"].remove(targetuser["name"])
            
            for exitid in thisroom["exits"]:
                if targetuser["name"] in exitid["owners"]:
                    if len(exitid["owners"])<2: exitid["owners"]=["<world>"]
                    else: exitid["owners"].remove(targetuser["name"])
            console.database.upsert_room(thisroom)

    # If the room contains items, return them to their primary owners.
    for thisitem in console.database.items.all():
        # Lookup the target item and perform item checks.
        #thisitem = COMMON.check_item(NAME, console, itemid)
        if targetuser["name"] in thisitem["owners"]:
            if len(thisitem["owners"])<2: thisitem["owners"]=["<world>"]
            else: thisitem["owners"].remove(targetuser["name"])
            console.database.upsert_item(thisitem)

    for user in console.database.users.all():
        if user["name"] == targetuser["name"]:
            console.database.delete_user(user)
            # Finished.
            console.msg("{0}: Done.".format(NAME))
            return True
    console.msg("{0}: Couldn't find that user. This shouldn't happen. Ownerships have been altered.".format(NAME))
    return False



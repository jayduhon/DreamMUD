#####################
# Dennis MUD        #
# make_exit.py      #
# Copyright 2018    #
# Michael D. Reiley #
#####################

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

NAME = "make exit"
CATEGORIES = ["exits"]
USAGE = "make exit <destination> <name>"
DESCRIPTION = "Create a new exit called <name> in the current room, leading to the room with ID <destination>."


def COMMAND(console, database, args):
    if len(args) < 2:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Make sure an integer was passed as the destination.
    try:
        dest = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False
    name = ' '.join(args[1:])

    # Make sure the name is not an integer, as this would be confusing.
    if len(args) == 2:
        try:
            test = int(args[1])
            console.msg(NAME + ": exit name cannot be an integer")
            return False
        except ValueError:
            # Not an integer.
            pass

    # Check if an exit by this name already exists. Case insensitive.
    thisroom = database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!
    exits = thisroom["exits"]
    if len(exits):
        for e in exits:
            if e["name"].lower() == name.lower():
                return False  # An exit by this name already exists.

    # Check if the destination room exists.
    destroom = database.room_by_id(dest)
    if not destroom:
        console.msg(NAME + ": destination room does not exist")
        return False  # The destination room does not exist.

    if thisroom["sealed"]["outbound"] and not console.user["wizard"] and console.user["name"] not in thisroom["owners"]:
        console.msg(NAME + ": this room is outbound sealed")
        return False

    if destroom["sealed"]["inbound"] and not console.user["wizard"] and console.user["name"] not in destroom["owners"]:
        console.msg(NAME + ": the destination room is inbound sealed")
        return False

    # Create our new exit.
    newexit = {"dest": dest, "name": name, "owners": [console.user["name"]], "desc": "", "action": "", "locked": False}
    thisroom["exits"].append(newexit)

    # Save.
    database.upsert_room(thisroom)
    console.msg(NAME + ": done (id: " + str(len(thisroom["exits"])-1) + ")")
    return True

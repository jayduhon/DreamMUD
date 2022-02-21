#######################
# Dennis MUD          #
# write.py             #
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

NAME = "write"
CATEGORIES = ["items"]
ALIASES = ["w"]
USAGE = "write <note> on <item>"
DESCRIPTION = """Write the message <note> on the item called <item>.

You may use a full or partial item name, or the item ID. 
You need to hold something to read and write.

Ex. `write Wow crystal! on ball`
Ex2. `write This stinks. on 4`"""

# this should be changed asap to work with "" or any escape character
# because right now you cant use the word on in the message itself.
def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=2, awake=True):
        return False

    # Iterate through the args to split it into two
    args=COMMON.split_list(args,"on")
    thisitemname=args[1]
    thismessage=args[0]
    #sw=0
    #for ar in args:
    #    if ar=="on": sw=1
    #    elif sw==0: thismessage.append(ar)
    #    elif sw==1: thisitemname.append(ar)
    #thisitemname=' '.join(thisitemname)
    #thismessage=' '.join(thismessage)

    # Get item name/id.
    target = thisitemname.lower()
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

        # Check for name or id match. Also check if the user prepended "the ". Figure out how to write it.
        if target in [thisitem["name"].lower(), "the " + thisitem["name"].lower()] or str(thisitem["id"]) == target:
            # Only non-owners lose duplified items when writing them.
            if thisitem["message"]=="":
                thisitem["message"]=thismessage
                thisitem["mlang"]=console.user["lang"]
                console.msg("You wrote {0} on {1}".format(thisitem["message"],COMMON.format_item(NAME, thisitem["name"])))
                console.shell.broadcast_room(console, "{0} writes something on {1}.".format(
                        console.user["nick"], COMMON.format_item(NAME, thisitem["name"])),exclude=console.user["name"])
                console.database.upsert_item(thisitem)
            else:
                console.msg("There is something written on that already.")
            return True
            # Update the user document.
        #return False


    # We didn't find the requested item. Check for a partial match.
    partial = COMMON.match_partial(NAME, console, target, "item", room=False, inventory=False, equipment=True)
    if partial:
        partial=thismessage.split()+["on"]+partial
        return COMMAND(console, partial)

    # Maybe the user accidentally typed "write item <item>".
    if args[0].lower() == "item":
        console.msg("{0}: Maybe you meant \"write {1}\".".format(NAME, ' '.join(args[1:])))

    return False

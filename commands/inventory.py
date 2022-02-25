#######################
# Dennis MUD          #
# inventory.py        #
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

from lib.litnumbers import *
from lib.vigenere import *
import random

NAME = "inventory"
CATEGORIES = ["items"]
ALIASES = ["inv", "i"]
USAGE = "inventory"
DESCRIPTION = "List all of the items in your inventory."


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0, awake=True):
        return False

    # Check if our inventory is empty.
    if not console.user["equipment"]:
        console.msg("You are not holding anything.")
    
    cursedinv=False
    for item in console.user["inventory"]+console.user["equipment"]:
        item = COMMON.check_item(NAME, console, item, reason=False)
        try:
            if item["cursed"]["cursetype"]=="invmess": 
                cursedinv=True
                break
        except:
            pass
    mylang=console.database.user_by_name(console.user["name"])["lang"]

    # Holding items
    if console.user["equipment"]:
        hitemlist=[]
        for hitem in console.user["equipment"]:
            hitem = console.database.item_by_id(hitem)
            hitemname=hitem["name"]
            hitemid=hitem["id"]
            if cursedinv: 
                hitemname=encvigenere(hitemname, mylang)
                hitemid=random.randint(1,100)
            if console.user["builder"]["enabled"]: hitemlist.append("{0} (ID: {1})".format(COMMON.format_item(NAME, hitemname),hitemid))
            else: hitemlist.append("{0}".format(COMMON.format_item(NAME, hitemname)))
        hitemlist=' and '.join(hitemlist)
        console.msg("You are holding {0}.".format(hitemlist))

    # Check if our inventory is empty.
    if not console.user["inventory"]:
        console.msg("Your inventory is empty.")
       
    # Enumerate our inventory.
    itemcount = 0
    for itemid in sorted(console.user["inventory"]):
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid, reason=False)

        # Uh oh, an item in our inventory doesn't actually exist.
        if not thisitem:
            console.log.error("Item referenced in user inventory does not exist: {user} :: {item}",
                              user=console.user["name"], item=itemid)
            console.msg("{0}: ERROR: Item referenced in your inventory does not exist: {1}".format(NAME, itemid))
            continue

        # Show the item's name and ID.
        hitemname=thisitem["name"]
        if cursedinv: 
            hitemname=encvigenere(hitemname, mylang)
            itemid=random.randint(1,100)
        if console.user["builder"]["enabled"]: console.msg("{0} (ID: {1})".format(hitemname, itemid))
        else: console.msg("{0}".format(hitemname))

        # Keep count.
        itemcount += 1

    # Finished.
    if itemcount>1:
        console.msg("There are {0} items in your inventory.".format(int_to_en(itemcount)))
    elif itemcount==1:
        console.msg("There is one item in your inventory.".format(int_to_en(itemcount)))
    else:
        console.msg("There are no items in your inventory.")
    return True

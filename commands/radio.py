#######################
# Dennis MUD          #
# radio.py             #
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
from lib.vigenere import *

NAME = "radio"
CATEGORIES = ["messaging"]
SPECIAL_ALIASES = ['#']
USAGE = "radio <message>/<frequency>"
DESCRIPTION = """Send a message with a radio to the given frequency.

You must have a radio in your hands to broadcast anything. Anyone with a radio tuned to the same frequency will hear you.
If you use a single number after radio, you will tune your held radios to the given frequency.

Ex. `radio Hello everyone!`
Ex2. `radio 120`"""

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()

def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False
    if len(args)==1 and is_integer(args[0]):
        freqtoset = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
        if freqtoset is None:
            return False
        for radio in console.user["equipment"]:
            radio=COMMON.check_item(NAME, console, radio)
            if radio["radio"]["enabled"]:
                radio["radio"]["frequency"]=freqtoset
                if freqtoset<=0: console.msg("You turn {0} off.".format(COMMON.format_item(NAME,radio["name"])))
                elif freqtoset>1000:
                    console.msg("The maximum frequency you can tune to is 1000.")
                    return False
                else: console.msg("You tune {0} to the frequency {1}.".format(COMMON.format_item(NAME,radio["name"]),str(freqtoset)))
                console.database.upsert_item(radio)
                return True
        console.msg("You do not hold any radios to tune.")
        return False
    else:    
        mylang=console.database.user_by_name(console.user["name"])["lang"]
        emsg=encvigenere(' '.join(args),mylang)
        for radio in console.user["equipment"]:
            radio=COMMON.check_item(NAME, console, radio)
            if radio["radio"]["enabled"]:
                if radio["radio"]["frequency"]>0: 
                    console.shell.radiocast(' '.join(args), radio["radio"]["frequency"], mtype="say", enmsg=emsg,tlang=mylang)
                else: 
                    console.msg("{0} is turned off.".format(COMMON.format_item(NAME,radio["name"]).capitalize()))
                return True
        console.msg("You do not hold any radios to talk into.")
        return False
        
    # Finished.
    return True

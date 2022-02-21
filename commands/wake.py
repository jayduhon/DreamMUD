#####################
# Dennis MUD        #
# sit.py            #
# Copyright 2020    #
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

NAME = "wake"
CATEGORIES = ["actions", "settings", "users"]
ALIASES = ["wake up"]
USAGE = "wake [target_name]"
DESCRIPTION = """Wake up from sleep or wake up [target_name].

You can use username or nickname, whole or partial names for your target.

Ex. `wake`
Ex2. `wake up Seisatsu`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args):
        return False

    # Check if we are already sitting down. If so, stand up, unless arguments are given.
    if console["posture"] and not args:
        if console["posture"] == "sleeping":
            return COMMON.posture(NAME, console)

    # If no arguments were given, we are done.
    if not args:
        if not console["posture"]: console.msg("You are not sleeping.")
        return True

    # Lookup the current room.
    #thisroom = COMMON.check_room(NAME, console)
    #if not thisroom:
    #    return False
    
    if console["posture"] == "sleeping":
        console.msg("You are asleep, dreaming you could do things.")
        return False
    thisreceiver=' '.join(args[0:])
    # Make sure the named user exists, is online, and is in the same room as us.
    targetuser = COMMON.check_user(NAME, console, thisreceiver, room=True, online=True, live=True, reason=False,
                                   wizardskip=["room", "online"])
    if not targetuser:
        # Check for a partial user match, and try running again if there's just one.
        partial = COMMON.match_partial(NAME, console, thisreceiver.lower(), "user")
        if partial:
            return COMMAND(console, partial)
        else: console.msg("{0}: No such user in this room.".format(NAME))
        return False

    # Found the user, wake them up!
    userconsole = console.shell.console_by_username(targetuser["name"])
    if not userconsole:
            return False
    if userconsole["posture"]=="sleeping":
        console.shell.msg_user(console.user["name"],"You wake {0} up.".format(targetuser["nick"]))
        console.shell.broadcast_room(console,"{0} wakes {1} up.".format(console.user["nick"],targetuser["nick"]),exclude=console.user["name"])
        console.shell.msg_user(targetuser["name"],"{0} wakes you up.".format(console.user["nick"]))
        return COMMON.posture(NAME, userconsole)
    else:
        if userconsole.user["pronouns"]=="male":
            console.msg("He is not asleep.")
        elif userconsole.user["pronouns"]=="female":
            console.msg("She is not asleep.")
        elif userconsole.user["pronouns"]=="neutral":
            console.msg("They are not asleep.")
        else: console.msg("{0} is not asleep.".format(userconsole.user["pronouns"].capitalize()))
        return False
    
    # Finished.
    return True
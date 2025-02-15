#######################
# Dennis MUD          #
# shell.py            #
# Copyright 2018-2021 #
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

import importlib.machinery
import importlib.util
import os
import string
import sys
import random

from lib.logger import Logger
from lib.color import *
from lib.dreamgen import *
import unicodedata as ud

import builtins
from lib import common
builtins.COMMON = common

# The directory where command modules are stored, relative to this directory.
COMMAND_DIR = "commands/"

# A string list of all characters allowed in user commands.
ALLOWED_CHARACTERS = string.ascii_letters + string.digits + string.punctuation + ' '
# Whats the point of UTf-8 if we cant use it?
DISALLOWED_CHARACTERS = "{}"

class Shell:
    """Shell

    The Shell loads command modules, enumerates help, and provides command access to the user consoles.

    :ivar router: The Router instance, which handles interfacing between the server backend and the user consoles.
    """
    def __init__(self, database, router, log=None):
        """Console Initializer

        :param database: The DatabaseManager instance to use.
        :param router: The Router instance, which handles interfacing between the server backend and the user consoles.
        :param log: Alternative logging facility, if not set.
        """
        self.router = router
        self._log = log or Logger("shell")

        self._database = database
        self._commands = {}
        self._help = {}
        self._special_aliases = {}
        self._disabled_commands = []

        self._load_modules()
        self._build_help()

    def _load_modules(self):
        """Enumerate and load available command modules.

        Command modules are stored in COMMAND_DIR, and their filename defines their command name.

        :return: True
        """
        self._log.info("Loading command modules...")
        command_modules = os.listdir(COMMAND_DIR)

        # Run through the list of all files in the command directory.
        for command in command_modules:
            # Python files in this directory are command modules. Construct modules.
            if command.endswith(".py") and not command.startswith('_'):
                command_path = os.path.join(os.getcwd(), COMMAND_DIR, command)
                cname = command[:-3].replace('_', ' ')

                # Give an error if another command with the same name is already loaded.
                if cname in self._commands:
                    self._log.error("A command by this name was loaded twice: {cname}", cname=cname)

                # Different import code recommended for different Python versions.
                if sys.version_info[1] < 5:
                    self._commands[cname] = importlib.machinery.SourceFileLoader(cname, command_path).load_module()
                else:
                    spec = importlib.util.spec_from_file_location(cname, command_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    self._commands[cname] = mod

                # Set up Aliases for this command.
                # Aliases are alternative names for a command.
                if hasattr(self._commands[cname], "ALIASES"):
                    for alias in self._commands[cname].ALIASES:
                        self._commands[alias] = self._commands[cname]

                # Set up Special Aliases for this command.
                # Special Aliases are single character aliases that don't need a space after them.
                if hasattr(self._commands[cname], "SPECIAL_ALIASES"):
                    for special_alias in self._commands[cname].SPECIAL_ALIASES:
                        self._special_aliases[special_alias] = cname

        # Check for partially overlapping command names.
        found_overlaps = []
        for cname in self._commands:
            for cname2 in self._commands:
                if cname == cname2:
                    continue

                # Check if any command starts with the name of any other command,
                # where they are not aliases for each other. This is bad.
                if cname.startswith(cname2 + ' ') and not (
                        (hasattr(self._commands[cname2], "ALIASES") and
                         cname in self._commands[cname2].ALIASES) or
                        (hasattr(self._commands[cname], "ALIASES") and
                         cname2 in self._commands[cname].ALIASES)):

                    # Only warn about each overlap once.
                    if not ([cname, cname2] in found_overlaps or [cname2, cname] in found_overlaps):
                        found_overlaps.append([cname, cname2])
                        self._log.warn("Overlapping command names: {cname}, {cname2}", cname=cname,
                                       cname2=cname2)

        self._log.info("Finished loading command modules.")
        return True

    def _build_help(self):
        """Enumerate available help categories and commands.

        Categories and commands are read from constants in the command modules.

        :return: True
        """
        self._help["all"] = []
        for cmd in self._commands.keys():
            if hasattr(self._commands[cmd], "CATEGORIES"):
                for category in self._commands[cmd].CATEGORIES:
                    if category not in self._help.keys():
                        self._help[category] = []
                    if not self._commands[cmd].NAME in self._help[category]:
                        self._help[category].append(self._commands[cmd].NAME)
            if not self._commands[cmd].NAME in self._help["all"]:
                self._help["all"].append(self._commands[cmd].NAME)

        return True

    def command(self, console, line, show_command=True):
        """Command Handler

        Parse and execute a command line, discerning which arguments are part of the command name
        and which arguments should be passed to the command.

        :param console: The console calling the command.
        :param line: The command line to parse.
        :param show_command: Whether or not to echo the command being executed in the console.

        :return: Command result or None.
        """
        # Return if we got an empty line.
        if not line:
            return None

        # Strip whitespace from the front and back.
        line = line.strip()

        # Process any special aliases.
        if line[0] in self._special_aliases:
            line = line.replace(line[0], self._special_aliases[line[0]]+' ', 1)

        # Check for illegal characters, except in passwords.
        if line.split(' ')[0] not in ["register", "login", "password"]:
            for c in line:
                if c in DISALLOWED_CHARACTERS:
                    console.msg("Command contains illegal characters.")
                    return None
                #if c not in ALLOWED_CHARACTERS:
                #    console.msg("Command contains illegal characters.")
                #    return None

        # Split the command line into a list of arguments.
        line = line.split(' ')

        # Remove extraneous spaces.
        line = [elem for elem in line if elem != '']

        # Find out which part of the line is the command, and which part is its arguments.
        for splitpos in range(len(line)):
            # Check if the whole line is a command with no arguments.
            if splitpos == 0:
                # Call with no arguments.
                if ' '.join(line).lower() in self._commands.keys():
                    if not console.user:
                        console.msg("> " + ' '.join(line))
                        console.msg('='*20)
                    elif show_command and console.user["cecho"]["enabled"]:
                        console.msg("> " + ' '.join(line))
                        console.msg('='*20)
                    return self.call(console, ' '.join(line).lower(), [])

                # Keep searching.
                continue

            # Only part of the line is a command. Call that segment and pass the rest as arguments.
            if ' '.join(line[:-splitpos]).lower() in self._commands.keys():
                # Log and echo commands to the console that don't involve passwords.
                if line[0] not in ["register", "login", "password"]:
                    if not console.user:
                        console.msg("> " + ' '.join(line))
                        console.msg('='*20)
                    elif show_command and console.user["cecho"]["enabled"]:
                        console.msg("> " + ' '.join(line))
                        console.msg('=' * 20)
                return self.call(console, ' '.join(line[:-splitpos]), line[-splitpos:])

        # We haven't found a command. Maybe it's an exit name, but only if we're logged in.
        if console.user:
            partial = COMMON.match_partial("console", console, ' '.join(line).lower(), "exit", message=False)
            if partial:
                return self.call(console, "go", partial)

        # We're still here and haven't found a command or exit in this line. Must be gibberish.
        if line:
            console.msg("Unknown command: " + ' '.join(line))

            # Suggest similar commands.
            if len(line[0]) > 3:
                suggestions = []
                for segment in line:
                    for possible in self._commands.keys():
                        if (possible in segment.lower() or segment.lower() in possible) and len(possible) > 3:
                            suggestions.append(possible)
                if suggestions:
                    console.msg("Possibly related commands: {0}".format(', '.join((sorted(suggestions)))))

        # We didn't find anything.
        return None

    def help(self, console, line):
        """Help Handler

        Retrieve the help for a category or command.

        :param console: The console requesting help.
        :param line: The help line to parse.

        :return: True if succeeded, False if failed.
        """
        # If help was called by itself, assume we want the help for help itself.
        if not line:
            line = "help"

        line = line.lower()

        # Check for command names overlapping category names.
        if line in self._help.keys() and line in self._commands.keys():
            self._log.warn("Command name overlaps with category name: {line}", line=line)

        # Return a formatted help message for the named category.
        # Thanks to:
        # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        # https://stackoverflow.com/questions/9989334/create-nice-column-output-in-python
        elif line in self._help.keys():
            cn = self._database.defaults["help"]["columns"]
            cols = [sorted(self._help[line])[i:i + cn] for i in range(0, len(sorted(self._help[line])), cn)]
            col_width = max(len(word) for row in cols for word in row) + 2  # padding
            console.msg("Available commands in category {0}:".format(line))
            for row in cols:
                console.msg("".join(word.ljust(col_width) for word in row), True)

        # Return a help message for the named command.
        elif line in self._commands.keys():
            # Return a help message for the named command.
            usage = "Usage: " + self._commands[line].USAGE
            desc = "Description: " + self._commands[line].DESCRIPTION + '\n'

            # Enumerate the aliases and list them at the end of the description.
            alias_list = ""
            if hasattr(self._commands[line], "ALIASES"):
                alias_list = (', '.join(self._commands[line].ALIASES))
                desc += "\nCommand Aliases: " + alias_list
            if hasattr(self._commands[line], "SPECIAL_ALIASES"):
                alias_list = (', '.join(self._commands[line].SPECIAL_ALIASES))
                desc += "\nSpecial Aliases: " + alias_list
            if hasattr(self._commands[line], "CATEGORIES"):
                desc += "\nCategories: " + ', '.join(self._commands[line].CATEGORIES)

            # If this is the help command with no arguments, show available categories as well.
            if line == "help":
                desc += ("\n\nAvailable Categories: " + ', '.join(sorted(self._help.keys())))

            console.msg(usage)
            console.msg(desc)

        # Couldn't find anything.
        else:
            console.msg("help: Unknown command or category: {0}".format(line))

            # Suggest similar commands and categories.
            if len(line.split(' ')[0]) > 3:
                cats = []  # meow
                suggestions = []
                for segment in line.lower().split(' '):
                    for possible in self._help.keys():
                        if (possible in segment or segment in possible) and len(possible) > 3:
                            cats.append(possible)
                    for possible in self._commands.keys():
                        if (possible in segment or segment in possible) and len(possible) > 3:
                            suggestions.append(possible)
                if cats:
                    console.msg("help: Possibly related categories: {0}".format(', '.join(sorted(cats))))
                if suggestions:
                    console.msg("help: Possibly related commands: {0}".format(', '.join(sorted(suggestions))))
                return False

        # Success.
        return True

    def usage(self, console, line):
        """Usage Handler

        Retrieve just the usage string for a command.

        :param console: The console requesting help.
        :param line: The help line to parse.

        :return: True if succeeded, False if failed.
        """
        # If usage was called by itself, assume we want the usage string for usage itself.
        if not line:
            line = "usage"

        line = line.lower()

        # Return a usage string for the usage command.
        if line == "usage":
            console.msg("Usage: usage <command>")

        # Return a usage string for the named command.
        elif line in self._commands.keys():
            usage = "Usage: " + self._commands[line].USAGE
            console.msg(usage)

        # Couldn't find anything.
        else:
            console.msg("usage: Unknown command: " + line)
            return False

        # Success.
        return True

    def msg_user(self, username, message, mtype=None):
        """Send a message to a particular user.

        :param username: The username of the user to message.
        :param message: The message to send.

        :return: True if succeeded, False if failed.
        """
        for u in self.router.users:
            if self.router.users[u]["console"].user and \
                    self.router.users[u]["console"].user["name"] == username.lower():
                self.router.users[u]["console"].msg(message)
                return True
        return False

    def radiocast(self, message, radiofreq, exclude=None, excludelist=None, mtype=None, enmsg=None, tlang=None):
        # Iterate through users and see if they have a radio with same freq.
        # Message could depend on where the radio is.
        print(radiofreq)
        for u in self.router.users:
            if self.router.users[u]["console"].user:
                for potradio in self.router.users[u]["console"].user["inventory"]+self.router.users[u]["console"].user["equipment"]:
                    potradio=COMMON.check_item("radiocast", self.router.users[u]["console"], potradio)
                    # print(potradio["name"])
                    if potradio["radio"]["enabled"] and potradio["radio"]["frequency"]==int(radiofreq):
                        # print("Found a radio to broadcast to: "+message)
                        fmessage="{0} broadcasts: \"{1}\"".format(potradio["name"],message)
                        fenmsg="{0} broadcasts: \"{1}\"".format(potradio["name"],enmsg)
                        self.broadcast_room(self.router.users[u]["console"], fmessage, exclude, excludelist, mtype, fenmsg, tlang)
        # Iterate through rooms if they have an item dropped with same freq.
        for room in self._database.rooms.all():
            for itemid in room["items"]:
                iitem=COMMON.check_item("radiocast", self.router.users[u]["console"], itemid)
                if iitem:
                    if iitem["radio"]["enabled"] and iitem["radio"]["frequency"]==int(radiofreq):
                        # print("Found a radio in a room to broadcast to: "+message)
                        fmessage="{0} broadcasts: \"{1}\"".format(iitem["name"],message)
                        fenmsg="{0} broadcasts: \"{1}\"".format(iitem["name"],enmsg)
                        if len(room["users"])>0:
                            talkto=self.console_by_username(room["users"][0])
                            self.broadcast_room(talkto, fmessage, exclude, excludelist, mtype, fenmsg, tlang)
                else:
                    pass
        return True

    def broadcast(self, message, exclude=None, mtype=None):
        """Broadcast Message

        Send a message to all users connected to consoles.

        :param message: The message to send.
        :param exclude: If set, username to exclude from broadcast.
        :param mtype: Message type. Announce, chat, say, message.

        :return: True
        """
        self._log.info(message)
        self.router.broadcast_all(message, exclude, mtype)
        return True

    def broadcast_room(self, console, message, exclude=None, excludelist=None, mtype=None, enmsg=None, tlang=None):
        """Broadcast Message to Room

        Send a message to all users who are in the same room as the user connected to this console.

        :param console: The console sending the message.
        :param message: The message to send.
        :param exclude: If set, username to exclude from broadcast.
        :param mtype: Message type. Announce, chat, say, message.

        :return: True
        """
        self._log.info(message)
        self.router.broadcast_room(console.user["room"], message, exclude, excludelist, mtype, enmsg, tlang)
        return True
    
    def moveplayer(self,console,towhere):
        targetuser=console.user
        destroom = COMMON.check_room("update", console, towhere)
        thisroom = COMMON.check_room("update", console, console.user["room"])
        # The telekey is paired to a nonexistent room. Report and ignore it.
        if not destroom:
            console.msg("ERROR: Tried to teleport a sleeper into a nonexistent room!")
            console.log.error("Tried to teleport a sleeper into a nonexistent room!")

        # Proceed with teleportation.
        if console["posture_item"]: console["posture_item"]=""
        
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
        console.shell.broadcast_room(console, "{0} appeared.".format(targetuser["nick"]))

        # Save the origin room, the destination room, and our user document.
        console.database.upsert_room(thisroom)
        console.database.upsert_room(destroom)
        console.database.upsert_user(targetuser)

        # Update console's exit list.
        console.exits = []
        for exi in range(len(destroom["exits"])):
            console.exits.append(destroom["exits"][exi]["name"])
        return True
    
    def updatespirit(self):
        for u in self.router.users:
            if self.router.users[u]["console"].user and self.router.users[u]["console"].user["wizard"]==False:
                #if not self.router.users[u]["console"].user["spirit"]:
                #    self.router.users[u]["console"].user["spirit"]=1
                if self.router.users[u]["console"].user["ghost"]:
                        self.router.users[u]["console"].user["spirit"]-=15
                if self.router.users[u]["console"].user["spirit"]<=0:
                    # Not enough spirit to keep being a ghost.
                    if self.router.users[u]["console"].user["ghost"]:
                        self.router.users[u]["console"].user["ghost"]=False
                        self.broadcast_room(self.router.users[u]["console"],"{0} is visible again.".format(self.router.users[u]["console"].user["nick"]),exclude=self.router.users[u]["console"].user["name"])
                        self.router.users[u]["console"].msg("You are visible again.")
                    self.router.users[u]["console"].user["spirit"]=0
                if self.router.users[u]["console"].user["spirit"]<100:
                    # Bool if they are cursed or not by an item.
                    cursed = False
                    nightm = False
                    # Bool if they are asleep and an item will move them.
                    ported= False
                    # Iterate through inventory to see if they are cursed.
                    for it in self.router.users[u]["console"].user["inventory"]+self.router.users[u]["console"].user["equipment"]:
                        it2 = self.router.users[u]["console"].database.item_by_id(it)
                        if it2["cursed"]["enabled"]:
                            try:
                                if it2["cursed"]["cursetype"]=="spirit": cursed = True
                                elif it2["cursed"]["cursetype"]=="nightmare": nightm = True
                            except:
                                pass
                        if CONFIG["telekey_sport"]>0 and it2["telekey"]!=self.router.users[u]["console"].user["room"]:
                            if it2["telekey"] and self.router.users[u]["console"]["posture"]=="sleeping" and ported==False:
                                # Do a random roll and see if we will move.
                                if(random.randint(1,CONFIG["telekey_sport"])==1):
                                    self.router.users[u]["console"].msg("You dream of your {0}.".format(it2["name"]))
                                    self.moveplayer(self.router.users[u]["console"],it2["telekey"])
                                    ported=True
                            #if it2["whirlpool"]["enabled"]: willport = True
                    # Only gain spirit if we are not cursed.
                    if nightm == True:
                        if self.router.users[u]["console"]["posture"]=="sleeping": 
                            self.router.users[u]["console"].msg(nightmgen())
                        else: 
                            self.router.users[u]["console"].user["spirit"]+=CONFIG["spiritrate"]
                            self.router.users[u]["console"].msg("You regain some spirit.")
                    elif cursed == False:
                        self.router.users[u]["console"].user["spirit"]+=CONFIG["spiritrate"]
                        if self.router.users[u]["console"]["posture"]!="sleeping": self.router.users[u]["console"].msg("You regain some spirit.")
                    else:
                        if self.router.users[u]["console"]["posture"]!="sleeping": self.router.users[u]["console"].msg("You shiver for a moment.")
                elif self.router.users[u]["console"].user["spirit"]>100: 
                    self.router.users[u]["console"].user["spirit"]=100
                self.router.users[u]["console"].database.upsert_user(self.router.users[u]["console"].user) 
                #except:
                #    self.router.users[u]["console"].user["spirit"]=0
                #    self.router.users[u]["console"].msg("You start to gain some spirit.")
                #    self.router.users[u]["console"].database.upsert_user(self.router.users[u]["console"].user) 
        return True

    def user_by_name(self, username):
        """Get a user by their name.

        It is necessary to modify user records through the console before updating the database, if they are logged in.
        Otherwise their database record will be overwritten next time something is changed in their console record.
        If the user is logged in, return their console record.
        Otherwise, return their record directly from the database.

        :return: Console or Database User Document, or None
        """
        for u in self.router.users:
            if self.router.users[u]["console"].user and \
                    self.router.users[u]["console"].user["name"].lower() == username.lower():
                return self.router.users[u]["console"].user
        return self._database.user_by_name(username.lower())

    def user_by_nick(self, nickname):
        """Get a user by their nickname.

        It is necessary to modify user records through the console before updating the database, if they are logged in.
        Otherwise their database record will be overwritten next time something is changed in their console record.
        If the user is logged in, return their console record.
        Otherwise, return their record directly from the database.

        :return: Console or Database User Document, or None
        """
        for u in self.router.users:
            if self.router.users[u]["console"].user and \
                    self.router.users[u]["console"].user["nick"].lower() == nickname.lower():
                return self.router.users[u]["console"].user
        return self._database.user_by_nick(nickname.lower())

    def console_by_username(self, username):
        """Get the console of a user by their username.

        :return: Console if succeeded, None if failed.
        """
        for u in self.router.users:
            if self.router.users[u]["console"].user and \
                    self.router.users[u]["console"].user["name"].lower() == username.lower():
                return self.router.users[u]["console"]

    def call(self, console, command, args):
        """Call a command, making sure it isn't disabled. (Unless we're a wizard, then it doesn't matter.)

        :param console: The console calling the command.
        :param command: The name of the command to call.
        :param args: Arguments to the command.

        :return: True if succeeded, False if failed
        """
        command = command.lower()
        if command in self._disabled_commands and not console.user["wizard"]:
            console.msg("{0}: Command disabled.".format(command))
            return False
        return self._commands[command].COMMAND(console, args)

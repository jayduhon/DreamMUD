# molylepke MUD - Multiplayer Text Adventure Sandbox

Molylepke MUD is a DennisMUD fork that was mainly modeled after ifmud's capabilities. Here with this fork I focus on the multiplayer aspect, abandoning the single-player branch and implementing modern mud protocols like MSSP.


Current changes to mainline DennisMUD
================================
- Xterm colors over telnet,
- MSSP support,
- Optional builder flag for stripping ID and ownership data,
- Randomize exit/item commands,
- Languages,
- Containers,
- Custom pronouns system,
- Hidden items,
- Separate equipment list (items can be held),
- Writing on items that can be read after,
- Timeflow,
- Recover phrases instead of 6 digit recovery numbers,
- Spirit system (certain commands cost spirit if enabled in server config),
- Sleeping (on items or ground),
- Rituals to perform (telepathy, identify, reveal, seer, ghost, cleanse, whirlpool),
- Cursed items,
- Command history and command shortcuts on the websocket client,
- Radio items that can be used to broadcast to tuned frequencies,
- Optional IRC gateway that relays the chat command back and forth.

Defaults Configuration
======================

There is a configuration file `defaults.config.example.json` which contains a number of default values to use when creating new in-game rooms, items, and users. It is necessary before running Dennis to copy this file to `defaults.config.json`, and make changes if desired.

Multi-player Server
===================

To run a multi-player server, you can run `server.py`, which will start a websocket service and a telnet service by default. `websocket-client.example.html` provides an example in-browser client for the websocket service. You will also have to copy `server.config.example.json` to `server.config.json` and change any necessary settings. If you would like, you can also copy `motd.telnet.example.txt` to `motd.telnet.txt` and modify it as needed to provide a message to telnet users upon connection. To run the services, you will need [Python 3](https://www.python.org/), [TinyDB](https://tinydb.readthedocs.io/en/latest/), [jsonschema](https://python-jsonschema.readthedocs.io/en/stable/), [Twisted](https://twistedmatrix.com/trac/), [Autobahn](https://crossbar.io/autobahn/), [pyOpenSSL](https://www.pyopenssl.org/en/stable/), and [service_identity](https://service-identity.readthedocs.io/en/stable/installation.html).

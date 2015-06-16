# Goals #

  * This python module should provide easy access to the OpenTTD Game.
  * This library will be used to code a bot that has certain functions (see below)
  * This library should help to improve certain security holes and issues with the current network protocol

# Library #
Requirements:
  * platform independent
  * splitting into several layers of complexity (like basic communication class and complete client) to ease the usage
  * robust: the library may not crash servers or clients in any way
  * fast: it should not create lag when running on the same host as the server
  * easy to configure: using a configfile like openttd.cfg

# Bot #
  * 3 way connection interface:
    * per spectator account (not modifying the server sources)
    * per special connection to the server (by modifying the server sources, not coded yet)
    * per console wrapper (like autopilot)
  * Basic Functions:
    * logging user statistics and actions into a file (partly working)
    * providing an IRC bridge in order to connect the ingame chat and the IRC chat (working)
    * webserver to view statistics (only basics done)
  * advanced Functions (nothing done of this)(mostly brainstorm ideas):
    * controlling the server via rcon
    * votes: enables users to vote for changed settings of the server and server reset
    * user authentication: only certain users are able to give the bot important commands via ingame chat or IRC
    * parsing and understanding the map data (high goal to achieve, much work would have to be put into this to get it working properly)
    * removing/locking/unlocking companies with certain conditions
    * webinterface to download backups of the game
    * chat widget with ingame live chat on the webserver
    * log game aspects (some ideas):
      * town growth, used vehicles, travel distance, ...
    * advanced gameplay aspects when the bot runs a company (not necessary for all):
      * detect errors and jams and place signs and/or notify users of that
      * tree removal helper: place a sign and give money to the bot so it will remove trees for you at the place where you placed the sign

# User proxy (not written yet) #
  * Basic ideas:
    * users would join the proxy that forwards all traffic to the main server isntead of directly connecting to it.
    * this enables the proxy to enforce server rules, as he can reject client commands.
      * for example: large terrain manipulation: each manipulation that affects more than 10 tiles its rejected

# GRF crawler 2 (better name?) #
  * Basic Ideas:
    * real crawler: gets all used GRFS and finds download locations to them
    * script to download all missing GRFs in order to join a certain server
    * logging of server statistics in all kind of ways
    * usage of the original GRF crawler as source as well as the tt-forums

# Implementation Details #
here we will discuss the design and implementation of several components:
  * PluginSystem
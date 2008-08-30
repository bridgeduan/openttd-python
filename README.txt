OpenTTD-Python README
Last updated:      $Date$
From svn:          $HeadURL$
-----------------------------------------------------------------------------------------


Table of Contents:
------------------
1.0) About
2.0) Contacting
 * 2.1 Reporting Bugs
3.0) Supported Platforms
4.0) Running the 'examples'

1.0) About:
---- ------
OpenTTD-Python is a python library that will provide access to certain game aspects via the python scripting language.
It also contains a few example scripts, such as a client and a serverstats script.

OpenTTD-Pyhton is licensed under the GNU General Public License version 3.

2.0) Contacting:
---- -----------
The easiest way to contact the creators of OpenTTD-Python is by joining #openttd-python on irc.oftc.net.
The google code project page is on http://openttd-python.googlecode.com.

2.1) Reporting Bugs:
---- ---------------
To report a bug, please create a Google Code account and follow the issues
link from the google code project page. Please make sure the bug is reproducible and
still occurs in the current SVN version. Also
please look through the existing bug reports briefly to see whether the bug
is not already known.

The bug tracker URL is: http://code.google.com/p/openttd-python/issues

Please include the following information in your bug report:
        - Revision
		- Bug details, including instructions how to reproduce it
		- Operating System (Windows, Linux, FreeBSD, ...)
		- Python version
		- OpenTTD revision, in case you are connecting to a single server
        - If this bug only occurred recently please note the last
          version without the bug and the first version including
          the bug. That way we can fix it quicker by looking at the
          changes made.

3.0) Supported Platforms:
---- --------------------
OpenTTD-Python supports all platforms that can run the python interpreter

4.0) Running the 'example' client or server stats:
---- ---------------------------------------------
First edit the config.cfg to configure the client to your needs, then run (in a command prompt/terminal)
python ottd-client.py ip.ad.re.ss:port.
To run the serverstats, simply execute ottd-serverstats.py
ottd-gameinfo.py takes the same form of arguments as the client.

5.0) The plugin system:
---- ------------------
The openttd 'example' client also has a plugin system.
All plugins are loaded from the plugins directory, except for the files called __init__.py and pluginclass.py.

5.1) Writing your own plugin:
---- ------------------------
To write your own plugin, simply create a file in the plugins/ directory.
A plugin needs to contain a class, that is a subclass from the Plugin lass, in the pluginclass.py file.
import pluginclass
class MyRandomClassName(pluginclass.Plugin):
The init method for these classes is "init" (not __init__!), you can set the delete method yourself.
You do not have to create a class instance, the plugin system will do that for you. So congratulations, now you're done with your plugin.

5.1.1) Adding chatcommands:
------ --------------------
The pluginsystem has a very simple way to add chatcommands. From your plugin class, you can do self.registerChatCommand(commandname, commandcallback)
The callback is just a function that gets executed when the chatcommand is called. The event the command came from and the command given are passed as an argument. You can respond to the command with event.respond("msg")

5.1.2) Adding callbacks:
------ -----------------
The plugin system also has a way to register certain callbacks. From your plugin class, you can do self.registerCallback(callbackname, callbackfunction).
The following callbacks are available:
on_map_done         Called when the map download is done,     no arguments
on_user_join        Called when someone joins the game,          arguments: dict containing 'name', 'id', 'company', and 'uniqueid'
on_user_quit        Called when someone quits the game,          arguments: playername, message
on_user_disconnect  Called when someone disconnects,             arguments: playername, errortype
on_self_join        Called when the own join message is seen, no arguments
on_self_quit        Called when the own quit message is seen,    arguments: errortype, [quitmessage]. If errortype == -1, quitmessage is given
on_server_newmap    Called when the server loads a new map,   no arguments
on_server_shutdown  Called when the server shuts down,        no arguments
on_irc_user_join    Called when someone joins IRC,               arguments: IRC connection object, IRC event, see ircbot.py for more info
on_irc_user_quit    Called when someone leaves the IRC channel,  arguments: IRC connection object, IRC event, see ircbot.py for more info
on_irc_user_part    Called when someone disconnects from IRC,    arguments: IRC connection object, IRC event, see ircbot.py for more info
on_irc_joined       Called when the welcome-msg is received,  no arguments
on_irc_kicked       Called when the bot is kicked,            no arguments
on_receive_command  Called when a command is received,           arguments: player, command2, p1, p2, tile, text, callback, frame, my_cmd
on_receive_packet   Called when a packet is received,            arguments: packet-id, packet contents
on_frame            Called when a frame is received,             arguments: current framecounter

5.1.3) Adding event dispatchers:
------ -------------------------
Your plugin can also register event dispatchers, simply call self.registerEventDispatcher(eventClass, callback) and you're done! For getting the event classes, you need to import ottd_client_event in your script.
The callback has one argument, the event instance.

OpenTTD-Python README
Last updated:      $Date$
From svn:          $HeadURL$
------------------------------------------------------------------------


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



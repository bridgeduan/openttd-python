import ConfigParser
config = ConfigParser.SafeConfigParser()
config.read('config.cfg')

if not config.has_section('openttd') is True:
	config.add_section('openttd')
if not config.has_section('irc') is True:
	config.add_section('irc')
if not config.has_section('webserver') is True:
	config.add_section('webserver')
if not config.has_section('irccommands') is True:
	config.add_section('irccommands')
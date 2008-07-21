import ConfigParser
config = ConfigParser.SafeConfigParser()
config.read('config.cfg')

for section in ['openttd', 'irc', 'webserver', 'irccommands']:
	if not config.has_section(section):
		config.add_section(section)
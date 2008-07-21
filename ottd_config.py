import ConfigParser
config = ConfigParser.SafeConfigParser()

def LoadConfig():
	config.read('config.cfg')

LoadConfig()

for section in ['openttd', 'irc', 'webserver', 'irccommands']:
	if not config.has_section(section):
		config.add_section(section)
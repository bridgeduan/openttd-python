import ConfigParser
config = ConfigParser.RawConfigParser()

def LoadConfig():
	config.read('config.cfg')

LoadConfig()

for section in ['main', 'openttd', 'irc', 'webserver', 'irccommands', 'stats']:
	if not config.has_section(section):
		config.add_section(section)
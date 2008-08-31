import ConfigParser
config = ConfigParser.RawConfigParser()

configvalues = {
    "main":{
        "productive":"On",
        "commandprefix":"!"
    },
    "openttd":{
        "nickname":"ottd-bot",
        "uniqueid":"a4782b224f3cc3fb94743f992f19fb40",
        "quitmessage":"The openttd-bot flies away!",
        "savemap":"On",
        "savemapname":"network_tmp.sav"
    },
    "irc":{
        "enable":"On",
        "autojoin":"Off",
        "usecolors":"On",
        "server":"irc.oftc.net",
        "serverport":"6667",
        "nickname":"ottd-bot",
        "channel":"#openttd-python",
        "quitmessage":"bot shutting down..."
    },
    "webserver":{
        "enable":"On",
        "autostart":"Off",
        "port":"8080"
    },
    "irccommands":{},
    "serverstats":{
        "verbose":"Off",
        "savenewgrfs":"On",
        "savehistory":"On"
    },
    "timewarning":{
        "enable":"On",
        "starttimefile":"starttime.txt",
        "time_running":"604800",
        "warnings":"On",
        "warning_interval":"21600"
    }
}
def LoadConfig():
    config.read('config.cfg')
    configchanged = False
    for section in configvalues:
        if not config.has_section(section):
            config.add_section(section)
            configchanged = True
        for option in configvalues[section]:
            if not config.has_option(section, option):
                config.set(section, option, configvalues[section][option])
                configchanged = True
    if configchanged:
        WriteConfig()
def WriteConfig():
    file = open('config.cfg', 'wb')
    config.write(file)
    file.close()

LoadConfig()

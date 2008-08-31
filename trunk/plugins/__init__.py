#!/bin/env python
import os
import pluginclass
import StringIO
import traceback
import sys
INSTANCES = {}
MODULES = {}

def load_plugin(plugin):
    """
    Load a plugin
    @type  plugin: string
    @param plugin: plugin to import
    """
    try:
        if not plugin in MODULES:
            MODULES[plugin] = __import__(plugin, globals(), None, [''])
    except Exception, e:
        print('error in plugin %s: %s' % (plugin, str(e)))
        errorMsg = StringIO.StringIO()
        traceback.print_exc(file=errorMsg)
        print(errorMsg.getvalue())
def initialize_plugin(plugin, parent):
    """
    Initialize a plugin

    Calls a plugin constructor
    @type  plugin: Plugin-derived class
    @param plugin: the plugin to initialize
    @type  parent: SpectatorClient instance
    @param parent: the parent to pass to the plugin
    """
    if not plugin in INSTANCES:
        INSTANCES[plugin] = plugin(parent) 

def initialize_plugins(parent=None, module=None):
    """
    Initialize all plugins

    Calls initialize_plugin on all plugins (of a module if module is given)
    @type  parent: SpectatorClient instance
    @param parent: the parent to pass to the plugins
    @type  module: plugin module name
    @param module: (optional) module
    """
    for plugin in pluginclass.Plugin.__subclasses__():
        if module is None or plugin.__module__ == "plugins." + str(module):
            initialize_plugin(plugin, parent)
def load_plugins():
    """
    Load all plugins found in the plugins directory

    Calls load_plugin for each plugin
    """
    pluginlist = os.listdir(os.path.dirname(os.path.abspath(__file__)))
    for plugin in pluginlist:
        if plugin.endswith(".py"):
            plugin = plugin[:-3]
            if not plugin in ["__init__", "pluginclass"]:
                load_plugin(plugin)
def main():
    load_plugins()
    initialize_plugins()
if __name__ == '__main__':
    main()
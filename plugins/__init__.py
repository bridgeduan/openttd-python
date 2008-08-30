#!/bin/env python
import os
import pluginclass
import StringIO
import traceback
INSTANCES = []
MODULES = []

def load_plugin(plugin):
    try:
        MODULES.append(__import__(plugin, globals(), None, ['']))
    except Exception, e:
        print('error in plugin %s: %s' % (plugin, str(e)))
        errorMsg = StringIO.StringIO()
        traceback.print_exc(file=errorMsg)
        print(errorMsg.getvalue())

def initialize_plugins(parent=None):
    for plugin in pluginclass.Plugin.__subclasses__():
        INSTANCES.append(plugin(parent))
def load_plugins():
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
class Plugin(object):
    """
    The Plugin class, all plugins should be subclassed from this. It also provides an interface.
    @ivar callbacks  : All callbacks registered by the plugin.
    @ivar commands   : All chatcommands registered by the plugin
    @ivar dispatchers: All dispatchers registered by the plugin
    @type callbacks  : dict
    @type commands   : dict
    @type dispatchers: dict
    """
    callbacks = {}
    commands = {}
    dispatchers = {}
    def __init__(self, parentclient=None):
        """
        plugin constructor, please do not overwrite, but use init.
        @type  parentclient: SpectatorClient class instance
        @param parentclient: the client that is using the plugin
        """
        self.client = parentclient
        try:
            function = self.init
        except AttributeError:
            pass
        else:
            function()
    def registerCallback(self, type, callback):
        """
        Method to register a callback. The callbacks are documented in README.txt.
        @type      type: string
        @param     type: the callback type. I.e. on_mainloop
        @type  callback: function
        @param callback: The callback
        @rtype:          boolean
        @return:         True if the callback was added
        @postcondition:  plugin.client must not be none
        @postcondition:  the type must exist
        """
        if not self.client is None and type in self.client.callbacks:
            self.client.callbacks[type].append(callback)
            if not type in self.callbacks:
                self.callbacks[type] = []
            self.callbacks[type].append(callback)
            return True
        else:
            return False
    def unregisterCallback(self, type, callback):
        """
        Method to unregister a callback. The callbacks are documented in README.txt
        @type      type: string
        @param     type: the callback type. I.e. on_mainloop
        @type  callback: function
        @param callback: The callback
        @rtype:          Boolean
        @return:         True if it was unregistered
        @postcondition:  plugin.client must not be none
        @postcondition:  the callback must be registered
        """
        if not self.client is None and type in self.client.callbacks:
            if callback in self.client.callbacks[type]:
                self.client.callbacks[type].remove(callback)
                self.callbacks[type].remove(callback)
                return True
        return False
    def unregisterAllCallbacks(self):
        """
        Method to unregister all callbacks.
        """
        for callbacktype in self.callbacks:
            callbacklist = self.callbacks[callbacktype][:]
            for callback in callbacklist:
                self.unregisterCallback(callbacktype, callback)
    def registerChatCommand(self, command, callback):
        """
        Method to register a chatcommand.
        @type   command: string
        @param  command: the command name
        @type  callback: function
        @param callback: The callback
        @rtype:          boolean
        @return:         True if it was added
        @postcondition:  plugin.client must not be none
        @postcondition:  the command must not already be registered
        """
        if not self.client is None and not command in self.client.commands:
            self.client.commands[command] = callback
            self.commands[command] = callback
            return True
        else:
            return False
    def unregisterChatCommand(self, command):
        """
        Method to register a chatcommand.
        @type   command: string
        @param  command: the command name
        @rtype:          boolean
        @return:         True if it was removed
        @postcondition:  plugin.client must not be none
        @postcondition:  the command must be registered
        """
        if not self.client is None and command in self.client.commands and command in self.commands:
            del self.client.commands[command]
            del self.commands[command]
            return True
        else:
            return False
    def unregisterAllChatCommands(self):
        """
        Method to unregister all chatcommands.
        """
        commandlist = self.commands.copy()
        for command in commandlist:
            self.unregisterChatCommand(command)
    def registerEventDispatcher(self, toevent, callback):
        """
        Method to add an event dispatcher.
        Event dispatchers are called when an event is received.
        @type   toevent: Event-derived class
        @param  toevent: The class where the dispatcher should be added to
        @type  callback: function
        @param callback: The callback
        @rtype:          boolean
        @return:         True if it was registered
        @postcondition:  the callback must not already be registered
        """
        if not callback in toevent.dispatchTo:
            toevent.dispatchTo.append(callback)
            if not toevent in self.dispatchers:
                self.dispatchers[toevent] = []
            self.dispatchers[toevent].append(callback)
            return True
        else:
            return False
    def unregisterEventDispatcher(self, toevent, callback):
        """
        Method to remove an event dispatcher.
        @type   toevent: Event-derived class
        @param  toevent: The class where the dispatcher should be added to
        @type  callback: function
        @param callback: The callback
        @rtype:          boolean
        @return:         True if it was unregistered
        @postcondition:  the callback must be registered
        """
        if callback in toevent.dispatchTo and callback in self.dispatchers[toevent]:
            toevent.dispatchTo.remove(callback)
            self.dispatchers[toevent].remove(callback)
            return True
        else:
            return False
    def unregisterAllEventDispatchers(self):
        """
        Method to unregister all event dispatchers
        """
        for dispatcher in self.dispatchers:
            thisdispatcher = self.dispatchers[dispatcher][:]
            for dispatchto in thisdispatcher:
                unregisterEventDispatcher(dispatcher, dispatchto)
    def unregisterEveryThing(self):
        """
        Method to unregister everything that was ever registered by the plugin
        """
        self.unregisterAllCallbacks()
        self.unregisterAllChatCommands()
        self.unregisterAllEventDispatchers()

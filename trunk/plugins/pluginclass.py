class Plugin(object):
    callbacks = {}
    commands = {}
    dispatchers = {}
    def __init__(self, parentclient=None):
        self.client = parentclient
        try:
            function = self.init
        except AttributeError:
            pass
        else:
            function()
    def registerCallback(self, type, callback):
        if not self.client is None and type in self.client.callbacks:
            self.client.callbacks[type].append(callback)
            if not type in self.callbacks:
                self.callbacks[type] = []
            self.callbacks[type].append(callback)
    def unregisterCallback(self, type, callback):
        if not self.client is None and type in self.client.callbacks:
            if callback in self.client.callbacks[type]:
                self.client.callbacks[type].remove(callback)
                self.callbacks[type].remove(callback)
    def unregisterAllCallbacks(self):
        for callbacktype in self.callbacks:
            callbacklist = self.callbacks[callbacktype][:]
            for callback in callbacklist:
                self.unregisterCallback(callbacktype, callback)
    def registerChatCommand(self, command, callback):
        if not self.client is None and not command in self.client.commands:
            self.client.commands[command] = callback
            self.commands[command] = callback
            return True
        else:
            return False
    def unregisterChatCommand(self, command):
        if not self.client is None and command in self.client.commands and command in self.commands:
            del self.client.commands[command]
            del self.commands[command]
            return True
        else:
            return False
    def unregisterAllChatCommands(self):
        commandlist = self.commands.copy()
        for command in commandlist:
            self.unregisterChatCommand(command)
    def registerEventDispatcher(self, toevent, callback):
        if not callback in toevent.dispatchTo:
            toevent.dispatchTo.append(callback)
            if not toevent in self.dispatchers:
                self.dispatchers[toevent] = []
            self.dispatchers[toevent].append(callback)
            return True
        else:
            return False
    def unregisterEventDispatcher(self, toevent, callback):
        if callback in toevent.dispatchTo and callback in self.dispatchers[toevent]:
            toevent.dispatchTo.remove(callback)
            self.dispatchers[toevent].remove(callback)
            return True
        else:
            return False
    def unregisterAllEventDispatchers(self):
        for dispatcher in self.dispatchers:
            thisdispatcher = self.dispatchers[dispatcher][:]
            for dispatchto in thisdispatcher:
                unregisterEventDispatcher(dispatcher, dispatchto)
    def unregisterEveryThing(self):
        # a __del__ method, but called explicitly when a plugin is about to be reloaded
        self.unregisterAllCallbacks()
        self.unregisterAllChatCommands()
        self.unregisterAllEventDispatchers()

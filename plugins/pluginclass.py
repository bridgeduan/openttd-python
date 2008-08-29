class Plugin(object):
    def __init__(self, parentclient=None):
        self.client = parentclient
        try:
            function = self.init
        except AttributeError:
            pass
        else:
            function()
    def registerCallback(self, type, callback):
        if not self.client is None and type in self.client.callback:
            self.client.callbacks[type].append(callback)
    def registerChatCommand(self, command, callback):
        if not self.client is None and not command in self.client.commands:
            self.client.commands[type] = callback
            return True
        else:
            return False

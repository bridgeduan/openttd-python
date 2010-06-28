import pluginclass
from ottd_config import config, WriteConfig
from log import LOG
import time
from datetime import timedelta
import os
from openttd import const
from ottd_client_event import IngameChat, Broadcast, IngameToIRC, InternalCommand, IRCToIngame

class PlayerInfoPlugin(pluginclass.Plugin):
	"""
	A plugin that distributes information of what other players do :)
	"""
	
	companyLastAction = {}
	companyIdling = []
	
	def init(self):
		LOG.debug("PlayerInfoPlugin started")
		self.updateConfig()
		self.enabled  = config.getboolean('playerinfos', 'enable')
		self.idletime = config.getint    ('playerinfos', 'idletime')
		self.registerCallback("on_receive_command", self.commandReceived)
		self.registerCallback("on_mainloop", self.onMainLoop)
		self.registerChatCommand("stopinfo", self.stopInfo)
		self.registerChatCommand("idleinfo", self.idleInfo)

	def wordPlural(self, word, count):
		if count == 0:
			return ''
		if count > 1:
			return '%d '%count + word + 's'
		return '%d '%count + word

	def timeFormat(self, secs):
		return str(timedelta(seconds = secs))

	def commandReceived(self, cmd):
		if cmd.commandid in const.command_names.keys():
			LOG.debug("got command: %d(%s) from company %d: '%s'" % (cmd.cmd, const.command_names[cmd.commandid].__str__(), cmd.company + 1, cmd.text))

		ctime = time.time()
		companystr = self.client.getCompanyString(cmd.company)

		if cmd.company in self.companyIdling and cmd.company != const.PLAYER_SPECTATOR:
			# remove from that list
			idx = self.companyIdling.index(cmd.company)
			del self.companyIdling[idx]
			timediff = ctime - self.companyLastAction[cmd.company]
			if timediff > self.idletime:
				# we were here already, check if we got back from idling
				Broadcast("%s is back from idling after %s" % (companystr, self.timeFormat(timediff)), parentclient=self.client)
			
		self.companyLastAction[cmd.company] = ctime
		
		if cmd.commandid == const.commands['CMD_PLACE_SIGN'] and cmd.text != '':
			Broadcast("%s placed a sign: '%s'" % (companystr, cmd.text), parentclient=self.client)
		elif cmd.commandid == const.commands['CMD_RENAME_SIGN'] and cmd.text != '':
			Broadcast("%s renames a sign: '%s'" % (companystr, cmd.text), parentclient=self.client)
		elif cmd.commandid == const.commands['CMD_SET_COMPANY_COLOUR']:
			Broadcast("%s changed their color" % companystr, parentclient=self.client)
		elif cmd.commandid == const.commands['CMD_RENAME_COMPANY']:
			Broadcast("%s changed their company name to '%s'"%(companystr, cmd.text), parentclient=self.client)
		elif cmd.commandid == const.commands['CMD_SET_COMPANY_MANAGER_FACE']:
			Broadcast("%s changed their company face"%(companystr), parentclient=self.client)
		elif cmd.commandid == const.commands['CMD_RENAME_PRESIDENT']:
			Broadcast("%s changed their presidents name to '%s'"%(companystr, cmd.text), parentclient=self.client)
		elif cmd.commandid == const.commands['CMD_BUILD_INDUSTRY']:
			Broadcast("%s built a new industry"%(companystr), parentclient=self.client)
		elif cmd.commandid == const.commands['CMD_BUILD_COMPANY_HQ']:
			Broadcast("%s built or relocated their HQ"%(companystr), parentclient=self.client)
	
	def stopInfo(self, event, commandstr, recursion_depth=0):
		pass
		
	def idleInfo(self, event, commandstr, recursion_depth=0):
		t = time.time()
		for cid in self.companyLastAction:
			if cid == const.PLAYER_SPECTATOR:
				continue
			companystr = self.client.getCompanyString(cid)
			timestr = self.timeFormat(t - self.companyLastAction[cid])
			event.respond("%s idle time: %s" % (companystr, timestr))
	
	def checkForIdlingClients(self):
		t = time.time()
		for cid in self.companyLastAction:
			if cid in self.companyIdling:
				# client already idling, ignore that one
				continue
			if cid == const.PLAYER_SPECTATOR:
				continue
			companystr = self.client.getCompanyString(cid)
			timediff = t - self.companyLastAction[cid]
			if timediff > self.idletime:
				timestr = self.timeFormat(time.time() - self.companyLastAction[cid])
				Broadcast("%s is now idling after %s"%(companystr, timestr), parentclient=self.client)
				self.companyIdling.append(cid)
	
	def onMainLoop(self):
		# check for new idling clients
		if self.idletime > 0:
			self.checkForIdlingClients()

	def updateConfig(self):
		configchanged = False
		if not config.has_section("playerinfos"):
			config.add_section("playerinfos")
			configchanged = True
		options = {
			"enable":"On",
			"idletime":"300",
		}
		for option in options: 
			if not config.has_option("playerinfos", option):
				config.set("playerinfos", option, options[option])
				configchanged = True
		if configchanged:
			WriteConfig()
	
from ottd_config import config

class GrfDB:
	canSaveLoad = True
	listchanged = False
	def __init__(self):
		self.file = None
		self.__database = {}
	def loadfromfile(self, filename):
		try:
			import pickle
		except ImportError:
			LOG.error("error while loading the pickle module...")
			self.__database = {}
			self.canSaveLoad = False
			return
		try:
			f = open(filename, 'rb')
			self.__database = pickle.load(f)
			f.close()
		except IOError:
			LOG.error("error while opening newgrf cache file!")
			self.__database = {}
	def savetofile(self, filename):
		if not self.canSaveLoad or not self.listchanged or not config.getboolean("serverstats", "savenewgrfs"):
			return
		import pickle
		try:
			f = open(filename, 'wb')
			pickle.dump(self.__database, f, 1)
			f.close()
		except IOError:
			LOG.error("error while saving newgrf cache file!")
	def hasgrf(self, md5):
		if md5 in self.__database:
			return True
		return False
	def getdbcount(self):
		return len(self.__database)
	def getgrfsnotinlist(self, list):
		requestlist = []
		for grf in list:
			if not self.hasgrf(grf[1]):
				requestlist.append(grf)
		return requestlist
	def addgrf(self, id, md5, name):
		self.__database[md5] = [id, md5, name]
		self.listchanged = True
	def getgrfname(self, grf):
		if self.hasgrf(grf[1]):
			return self.__database[grf[1]][2]
		else:
			return "<unknown name(%s)>" % grf[0].encode('hex')
	def addgrfinlist(self, list, grfid):
		# comparing grfids is ok, because you can't have duplicates in one server
		for unknowngrf in list:
			if unknowngrf[0] == grfid:
				self.addgrf(unknowngrf[0], unknowngrf[1], unknowngrf[2])
				return unknowngrf
		return None
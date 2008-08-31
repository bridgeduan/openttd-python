from ottd_config import config

class GrfDB:
    """
    The GRF Database used for looking up names
    @ivar canSaveLoad: set to False as soon as saving or loading failed, so we won't retry
    @type canSaveLoad: boolean
    @ivar listchanged: if the GRF database changed, i.e. if anything needs to be saved
    @type canSaveLoad: boolean
    @ivar        file: The grf database file
    @type        file: file
    @ivar  __database: The grf database
    @type __database: dict
    """
    canSaveLoad = True
    listchanged = False
    def __init__(self):
        """
        Class constructor
        """
        self.file = None
        self.__database = {}
    def loadfromfile(self, filename):
        """
        Load the grf database from a file
        @type  filename: string
        @param filename: the filename to load from
        """
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
        """
        Save the grf database from a file
        @type  filename: string
        @param filename: the filename to save to
        """
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
        """
        Look a grf up in the database
        @rtype:  boolean
        @return: If the database contains the grf
        """
        if md5 in self.__database:
            return True
        return False
    def getdbcount(self):
        """
        Get the number of grfs in the database
        @rtype:  int
        @return: Count of grfs in database
        """
        return len(self.__database)
    def getgrfsnotinlist(self, list):
        """
        Get all grfs that are not in the database
        
        Used for looking them up to the server
        @type  list: list
        @param list: list of grfs to check
        @rtype:  list
        @return: all grfs not in the database
        """
        requestlist = []
        for grf in list:
            if not self.hasgrf(grf[1]):
                requestlist.append(grf)
        return requestlist
    def addgrf(self, id, md5, name):
        """
        Add a grf to the databse
        @type    id: grfid
        @param   id: the grfid
        @type   md5: md5sum
        @param  md5: the md5sum
        @type  name: string
        @param name: The grfname
        @postcondition: listchanged is set to True
        """
        self.__database[md5] = [id, md5, name]
        self.listchanged = True
    def getgrfname(self, grf):
        """
        Get a grfname from the database
        @type  grf: list
        @param grf: grf in list: [grfid, md5sum]
        @rtype:     string
        @return:    grf name
        """
        if self.hasgrf(grf[1]):
            return self.__database[grf[1]][2]
        else:
            return "<unknown name(%s)>" % grf[0].encode('hex')
    def addgrfinlist(self, list, grfid):
        """
        Add the grf with grfid in the list to the database
        @type   list: list
        @param  list: list of grfs
        @type  grfid: grfid
        @param grfid: The grfid of the grf to add
        @rtype:       list/None if not found
        @return:      if found, a list with [grfid, md5sum, name], otherwise, None
        """
        # comparing grfids is ok, because you can't have duplicates in one server
        for unknowngrf in list:
            if unknowngrf[0] == grfid:
                self.addgrf(unknowngrf[0], unknowngrf[1], unknowngrf[2])
                return unknowngrf
        return None

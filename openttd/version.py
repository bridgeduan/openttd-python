#!/usr/bin/env python
# OpenTTD Version Parser
import constants as const
import httplib
import dateutil.parser
from log import LOG
class OTTDFingerConnection(httplib.HTTPConnection):
    def __init__(self):
        httplib.HTTPConnection.__init__(self, const.OPENTTD_FINGER_SERVER, const.OPENTTD_FINGER_PORT)
        self.tags = None
    def get_tags(self):
        LOG.info("Getting tags from openttd finger server")
        LOG.debug("HTTP GET %s" % const.OPENTTD_FINGER_TAGS_URL)
        self.request("GET", const.OPENTTD_FINGER_TAGS_URL)
        r1 = self.getresponse()
        LOG.debug("%d %s" % (r1.status, r1.reason))
        if r1.status != 200:
            raise Exception("Couldn't request tags list")
        data1 = r1.read()
        data2 = [i.strip().split() for i in data1.split('\n') if i]
        data2 = [(int(i[0]), dateutil.parser.parse(i[1]).date(), i[2].strip()) for i in data2]
        self.tags = data2
    def gettaginfo(self, tag):
        if not self.tags:
            self.get_tags()
        search = tag.strip()
        for i in self.tags:
            if i[2] == search:
                return i
        return None
    def gettagrev(self, tag):
        tinfo = self.gettaginfo(tag)
        if tinfo:
            return tinfo[0]
        return 0
    def gettagdate(self, tag):
        tinfo = self.gettaginfo(tag)
        if tinfo:
            return tinfo[1]
        return None
    def __del__(self):
        self.close()
def generate_newgrf_version(major, minor, build, release=False, revision=0):
    """
    The NewGRF revision of OTTD:
    bits  meaning.
    28-31 major version
    24-27 minor version
    20-23 build
       19 1 if it is a release, 0 if it is not.
     0-18 revision number; 0 for releases and when the revision is unknown.

    The 19th bit is there so the development/betas/alpha, etc. leading to a
    final release will always have a lower version number than the released
    version, thus making comparisions on specific revisions easy.
    """
    return major << 28 | minor << 24 | build << 20 | (release & 1) << 19 | (revision & ((1 << 19) - 1))
class OpenTTDVersion(object):
    """ OpenTTD Version Base Class """
    @classmethod
    def parsefull(cls, version):
        return cls(*cls.parse(version))
    def get_newgrf_version(self, fingerconnection):
        return 0

class OpenTTDVersionStable(OpenTTDVersion):
    """ OpenTTD Stable version (like 1.0.0) """
    def __init__(self, major, minor, build, subbuild=0):
        self.major = major
        self.minor = minor
        self.build = build
        self.subbuild = subbuild
        self.stable = True
        self.beta = False
        self.modified = False
        self.releasecandidate = False
    def __str__(self):
        if self.subbuild > 0:
            return "%d.%d.%d.%d" % (self.major, self.minor, self.build, self.subbuild)
        else:
            return "%d.%d.%d" % (self.major, self.minor, self.build)
    @classmethod
    def parse(cls, version):
        spl = version.strip().split('.')
        if len(spl) != 3 and len(spl) != 4:
            raise ValueError("Incorrect number of dots")
        major = int(spl[0])
        minor = int(spl[1])
        build = int(spl[2])
        subbuild = 0
        if len(spl) == 4:
            subbuild = int(spl[3])
        return major, minor, build, subbuild
    def get_newgrf_version(self, fingerconnection):
        tag_rev = fingerconnection.gettagrev(str(self))
        return generate_newgrf_version(self.major, self.minor, self.build, True, tag_rev)
class OpenTTDVersionRC(OpenTTDVersionStable):
    """ OpenTTD Release Candidate builds (like 1.0.0-RC1) """
    def __init__(self, major, minor, build, rcno, subbuild=0):
        OpenTTDVersionStable.__init__(self, major, minor, build, subbuild)
        self.rcno = rcno
        self.stable = True
        self.releasecandidate = True
    def __str__(self):
        return OpenTTDVersionStable.__str__(self) + ("-RC%d" % self.rcno)
    @classmethod
    def parse(cls, version):
        ver = version.strip().split('-RC')
        if not len(ver) == 2:
            raise ValueError("Doesn't contain -RC once")
        rcno = int(ver[1])
        major, minor, build, subbuild = OpenTTDVersionStable.parse(ver[0])
        return major, minor, build, rcno, subbuild
class OpenTTDVersionBeta(OpenTTDVersionStable):
    """ OpenTTD beta builds (like 1.0.0-beta1) """
    def __init__(self, major, minor, build, betano, subbuild=0):
        OpenTTDVersionStable.__init__(self, major, minor, build, subbuild)
        self.betano = betano
        self.stable = False
        self.beta = True
    def __str__(self):
        return OpenTTDVersionStable.__str__(self) + ("-beta%d" % self.betano)
    @classmethod
    def parse(cls, version):
        ver = version.strip().split('-beta')
        if not len(ver) == 2:
            raise ValueError("Doesn't contain -beta once")
        rcno = int(ver[1])
        major, minor, build, subbuild = OpenTTDVersionStable.parse(ver[0])
        return major, minor, build, rcno, subbuild
class OpenTTDVersionSVNNightly(OpenTTDVersion):
    """ OpenTTD SVN builds """
    def __init__(self, revision, modified=False, branch=""):
        self.revision = revision
        self.modified = modified
        self.stable = False
        self.beta = False
        self.releasecandidate = False
        self.branch = branch
    def __str__(self):
        rev = "r%d" % self.revision
        if self.modified:
            rev += "M"
        if self.branch:
            rev += "-" + self.branch
        return rev
    @classmethod
    def parse(cls, version):
        ver = version.strip()
        if not ver.startswith('r'):
            raise ValueError("Doesn't start with 'r'")
        ver = ver.split('-')
        rev = ver[0]
        branch = ""
        modified = False
        if len(ver) == 2:
            branch = ver[1]
        elif len(ver) != 1:
            raise ValueError("Contains '-' more than once")
        if rev.endswith('M'):
            modified = True
            rev = rev[:-1]
        rev = rev[1:] # strip away the 'r'
        rev = int(rev)
        return rev, modified, branch
class OpenTTDVersionOther(OpenTTDVersion):
    """ OpenTTD Custom Builds/hg builds/git builds/tar builds """
    def __init__(self, version):
        self.version = version
        self.modified = True
        self.stable = False
        self.beta = False
        self.releasecandidate = False
    def __str__(self):
        return self.version
    @classmethod
    def parse(cls, version):
        return version.strip(),
VERSION_CLASSES = [OpenTTDVersionStable, OpenTTDVersionRC, OpenTTDVersionBeta, OpenTTDVersionSVNNightly, OpenTTDVersionOther]
def parse_version(version):
    obj = None
    for cls in VERSION_CLASSES:
        try:
            obj = cls.parsefull(version)
            if obj: return obj
        except ValueError:
            continue
    return None

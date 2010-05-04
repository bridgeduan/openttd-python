#!/usr/bin/env python
# OpenTTD Version Parser

class OpenTTDVersion(object):
    """ OpenTTD Version Base Class """
    @classmethod
    def parsefull(cls, version):
        return cls(*cls.parse(version))

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

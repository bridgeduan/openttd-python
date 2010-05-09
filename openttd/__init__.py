# OpenTTD python module
# http://openttd-python.googlecode.com/

# Ensure the user is running the version of python we require.
import sys
if not hasattr(sys, "version_info") or sys.version_info < (2,4):
    raise RuntimeError("OpenTTD-Python requires Python 2.4 or later.")
del sys

from datastorageclass import DataStorageClass
from packet import DataPacket
import structz
import constants as const

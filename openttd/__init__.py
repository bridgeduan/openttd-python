# OpenTTD python module
# http://openttd-python.googlecode.com/

# Ensure the user is running the version of python we require.
import sys
if not hasattr(sys, "version_info") or sys.version_info < (2,4):
    raise RuntimeError("OpenTTD-Python requires Python 2.4 or later.")
del sys

import client
import networking
import savegame
from datastorageclass import DataStorageClass
import date
import grfdb
import structz
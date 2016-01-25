import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict  # noqa


if PY3:
    open = open
else:
    from io import open  # noqa

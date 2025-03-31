from importlib.metadata import version

__version__ = version(__package__)

from .api import Strats as Strats
from .core import Data as Data
from .core import Monitor as Monitor
from .core import State as State
from .core import Strategy as Strategy

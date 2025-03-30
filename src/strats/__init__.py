from importlib.metadata import version

__version__ = version(__package__)

from .api import Strats as Strats
from .core import DataWithMetrics as DataWithMetrics
from .monitor import Monitor as Monitor
from .strategy import Strategy as Strategy

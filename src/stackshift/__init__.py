"""Public StackShift SDK surface."""

from stackshift.config import StackShiftSettings
from stackshift.errors import PreconditionError

__version__ = "0.0.1"
__all__ = ["PreconditionError", "StackShiftSettings", "__version__"]

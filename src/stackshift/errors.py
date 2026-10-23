"""Typed errors raised when StackShift safety checks fail."""


class StackShiftError(Exception):
    """Base error for expected StackShift failures."""


class PreconditionError(StackShiftError):
    """A required condition for a requested operation was not met."""


class LeakageError(PreconditionError):
    """Training, evaluation, or candidate document sets overlap."""


class QuantizedVectorsError(PreconditionError):
    """Stored vectors are compressed or quantized and cannot form reliable pairs."""


class MissingTextError(PreconditionError):
    """Source text is unavailable for one or more sampled document IDs."""


class ArtifactIntegrityError(StackShiftError):
    """An adapter artifact failed hash or compatibility verification."""


class StateUnavailableError(StackShiftError):
    """The configured remote live-state backend could not be read or written."""

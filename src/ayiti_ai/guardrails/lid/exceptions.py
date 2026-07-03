class LIDError(Exception):
    """Base exception for all Language Identification (LID) errors."""
    pass


class LIDConfigError(LIDError):
    """Raised when the LID configuration is invalid or missing."""
    pass


class LIDModelLoadError(LIDError):
    """Raised when a level fails to load its model files (FastText or CharCNN)."""
    pass


class LIDInvalidInputError(LIDError):
    """Raised when the input text fails validation constraints."""
    pass


class LIDInferenceError(LIDError):
    """Raised when a model fails during the prediction phase."""
    pass

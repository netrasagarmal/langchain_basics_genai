# Custom Exceptions
class UnsupportedFileTypeError(Exception):
    """Raised when an unsupported file type is encountered"""
    pass

class FileLoadError(Exception):
    """Raised when there's an error loading the file"""
    pass

class InvalidConfigurationError(Exception):
    """Raised when invalid configuration is provided"""
    pass

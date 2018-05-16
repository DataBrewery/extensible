class ExtensibleError(Exception):
    pass

class InternalError(ExtensibleError):
    """Exception raised when there is an error due to incorrect internal use of
    the library."""
    pass

class ConfigurationError(ExtensibleError):
    """Exception raised when there is an issue with configuration options."""
    pass

class OptionRequiredError(ConfigurationError):
    """Exception raised when a required option is not provided in the
    configuration."""
    pass

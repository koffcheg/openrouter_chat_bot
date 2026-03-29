class BotError(Exception):
    """Base application error."""


class ConfigurationError(BotError):
    """Raised when required configuration is missing or invalid."""


class ProviderError(BotError):
    """Raised when the upstream AI provider fails."""


class UserInputError(BotError):
    """Raised when user input is invalid."""

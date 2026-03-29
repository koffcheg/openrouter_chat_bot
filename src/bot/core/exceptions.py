class BotError(Exception):
    """Base application error."""


class ConfigurationError(BotError):
    pass


class ProviderError(BotError):
    pass


class ProviderTimeoutError(ProviderError):
    pass


class ProviderRateLimitError(ProviderError):
    pass


class ProviderUnavailableError(ProviderError):
    pass


class UserInputError(BotError):
    pass


class PermissionDeniedError(BotError):
    pass

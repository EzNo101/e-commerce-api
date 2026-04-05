class AppError(Exception):
    pass


class InvalidPasswordError(AppError):
    pass


class EmailAlreadyUsedError(AppError):
    pass


class UsernameAlreadyUsedError(AppError):
    pass


class UserNotFoundError(AppError):
    pass


class UserIsNotActiveError(AppError):
    pass


class InvalidTokenError(AppError):
    pass


class InvalidTokenTypeError(AppError):
    pass

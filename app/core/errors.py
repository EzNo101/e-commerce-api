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


class ProductNotFoundError(AppError):
    pass


class ProductQuantityError(AppError):
    pass


class ProductNotInCart(AppError):
    pass


class ProductAlreadyExistsError(AppError):
    pass


class ProductCreateError(AppError):
    pass


class CategoryNotFoundError(AppError):
    pass


class CategoryAlreadyExistsError(AppError):
    pass


class CategoryCreateError(AppError):
    pass


class OrderEmptyCartError(AppError):
    pass


class OrderCheckoutError(AppError):
    pass


class OrderNotFoundError(AppError):
    pass


class OrderAccessDeniedError(AppError):
    pass


class StripeRateLimitError(AppError):
    pass


class StripeUnavalaibleError(AppError):
    pass


class StripeAuthError(AppError):
    pass


class StripeRequestError(AppError):
    pass


class OrderPersistenceError(AppError):
    pass

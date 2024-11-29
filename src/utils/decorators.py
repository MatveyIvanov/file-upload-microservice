import functools
import logging
from typing import Any, Callable

from sqlalchemy.exc import SQLAlchemyError

orm_logger = logging.getLogger("orm")
common_logger = logging.getLogger("common")


def handle_orm_error(func: Callable) -> Callable:
    """
    Decorator that handles any sqlalchemy error and logs this error

    :param func: function to decorate
    :type func: Callable
    :return: decorated function
    :rtype: Callable
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            orm_logger.error(
                f"Error while processing orm query - {str(e)}",
                extra={"func_args": args, "func_kwargs": kwargs},
                exc_info=e,
            )
            raise

    return wrapper


def handle_any_error(
    func: Callable | None = None,
    *,
    logger: logging.Logger = common_logger,
) -> Callable:
    """
    Decorator that handles any error and logs this error to specified logger

    :param func: function to decorate, defaults to None
    :type func: Callable | None, optional
    :param logger: logger for errors, defaults to common_logger
    :type logger: logging.Logger, optional
    :return: decorated function
    :rtype: Callable
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logging.debug(str(e))
                logger.error(
                    f"Unexpected error - {str(e)}",
                    exc_info=e,
                )
                raise

        return wrapper

    if func is not None:
        return decorator(func)

    return decorator


def session(func: Callable) -> Callable:
    """
    Decorator that injects session as `session` kwarg.
    If session already in kwargs, new session will not be injected

    :param func: function to decorate
    :type func: Callable
    :return: decorated function
    :rtype: Callable
    """

    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        from config.di import Container

        if "session" in kwargs.keys():
            return await func(*args, **kwargs)

        async with Container.db().session() as session:
            kwargs["session"] = session
            return await func(*args, **kwargs)

    return wrapper

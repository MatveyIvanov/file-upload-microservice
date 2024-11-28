"""Results of some weird experimenting at midnight"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Any, Callable, Dict, Generic, Iterable, Literal, Type, TypeVar

from sqlalchemy import (
    BinaryExpression,
    Column,
    ColumnElement,
    ColumnExpressionArgument,
    and_,
    or_,
)

from config.db import Base

TModel = TypeVar("TModel", bound=Base)


class operator(IntEnum):
    eq = 0
    lt = 1
    le = 2
    gt = 3
    ge = 4
    in_ = 5
    is_ = 6


class mode(IntEnum):
    and_ = 0
    or_ = 1


_OPERATOR_TO_ORM: Dict[
    operator,
    Callable[[Column, Any], BinaryExpression | ColumnElement],
] = {
    operator.eq: Column.__eq__,
    operator.lt: Column.__lt__,
    operator.le: Column.__le__,
    operator.gt: Column.__gt__,
    operator.ge: Column.__ge__,
    operator.in_: Column.in_,
    operator.is_: Column.is_,
}


_MODE_TO_ORM: Dict[
    mode,
    Callable[
        [
            ColumnExpressionArgument[bool] | Literal[False, True],
            Iterable[ColumnExpressionArgument[bool]],
        ],
        ColumnElement[bool],
    ],
] = {
    mode.and_: and_,
    mode.or_: or_,
}


class IFilter(ABC, Generic[TModel]):
    column: Column
    value: Any | None
    operator_: operator

    @abstractmethod
    def __init__(self, model: Type[TModel], column_name: str) -> None: ...
    @abstractmethod
    def __call__(self, value: Any, operator_: operator = operator.eq) -> IFilter: ...


class IFilterSeq(ABC):
    @abstractmethod
    def __init__(self, /, mode_: mode, *filters: IFilter | IFilterSeq): ...
    @abstractmethod
    def compile(self) -> ColumnElement[bool]: ...


class Filter(IFilter[TModel]):
    def __init__(self, model_class: Type[TModel], column_name: str) -> None:
        self.column: Column = getattr(model_class, column_name, None)
        self.value = None
        self.operator_ = operator.eq

        assert (
            self.column is not None
        ), f"Model {model_class.__name__} has no column named {column_name}."

    def __call__(self, value: Any, operator_: operator = operator.eq) -> IFilter:
        self.value = value
        self.operator_ = operator_
        return self


class FilterSeq(IFilterSeq):
    def __init__(self, /, mode_: mode, *filters: IFilter | IFilterSeq):
        self.mode_ = mode_
        self.filters = filters

    def compile(self) -> ColumnElement[bool]:
        result = []
        for filter in self.filters:
            if isinstance(filter, IFilter):
                result.append(
                    _OPERATOR_TO_ORM[filter.operator_](
                        filter.column,
                        filter.value,
                    )
                )
            else:
                result.append(filter.compile())

        return _MODE_TO_ORM[self.mode_](*result)

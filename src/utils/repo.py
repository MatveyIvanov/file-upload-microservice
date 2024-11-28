from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Literal, Type, TypeAlias, TypeVar

from pydantic import BaseModel
from sqlalchemy import (
    BinaryExpression,
    Column,
    ColumnElement,
    Result,
    Select,
    delete,
    select,
    update,
    and_,
)
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import Base, Database
from utils.decorators import handle_orm_error, session as inject_session
from utils.shortcuts import get_object_or_404

TModel = TypeVar("TModel", bound=Base)
TSchema = TypeVar("TSchema", bound=BaseModel)

Operator = Literal["eq", "lt", "le", "gt", "ge", "in", "is"]
Filters: TypeAlias = Dict[str, Any]
FieldToOperator: TypeAlias = Dict[str, Operator]


__OPERATOR_TO_ORM: Dict[
    Operator,
    Callable[[Column, Any], BinaryExpression | ColumnElement],
] = {
    "eq": Column.__eq__,
    "lt": Column.__lt__,
    "le": Column.__le__,
    "gt": Column.__gt__,
    "ge": Column.__ge__,
    "in": Column.in_,
    "is": Column.is_,
}


def _build_filters(
    model: TModel,
    filters: Filters,
    operator_overrides: FieldToOperator | None,
) -> List[BinaryExpression | ColumnElement]:
    result, operator_overrides = [], operator_overrides or {}
    for field, value in filters.items():
        column = getattr(model, field)
        operator = __OPERATOR_TO_ORM[operator_overrides.get(field, "eq")]
        result.append(operator(column, value))
    return result


class IRepo(ABC, Generic[TModel]):
    @abstractmethod
    def all_as_select(self) -> Select[TModel]: ...
    @abstractmethod
    async def all(self, *, session: AsyncSession = None) -> Result[TModel]: ...
    @abstractmethod
    async def get_by_id(
        self,
        id_: int,  # TODO: generic or union type for id_
        *,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> TModel: ...
    @abstractmethod
    async def get_by_ids(
        self,
        ids: List[int],
        *,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> Select[TModel]: ...
    @abstractmethod
    async def get_by_field(
        self,
        field: str,
        value: Any,
        *,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> TModel: ...
    @abstractmethod
    async def get_by_filters(
        self,
        *,
        filters: Filters,
        operator_overrides: FieldToOperator | None = None,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> Result[TModel]: ...
    @abstractmethod
    async def exists_by_field(
        self,
        field: str,
        value: Any,
        *,
        session: AsyncSession = None,
    ) -> bool: ...
    @abstractmethod
    async def create(
        self,
        entry: TSchema,
        *,
        session: AsyncSession = None,
    ) -> TModel: ...
    @abstractmethod
    async def update(
        self,
        instance: TModel,
        values: Dict,
        *,
        session: AsyncSession = None,
    ) -> None: ...
    @abstractmethod
    async def multi_update(
        self,
        ids: List[int],
        *,
        values: Dict[str, Any],
        session: AsyncSession = None,
    ) -> None: ...
    @abstractmethod
    async def delete(
        self,
        instance: TModel,
        *,
        session: AsyncSession = None,
    ) -> None: ...
    @abstractmethod
    async def delete_by_field(
        self,
        field: str,
        value: Any,
        *,
        session: AsyncSession = None,
    ) -> None: ...


class Repo(IRepo[TModel]):
    def __init__(self, db: Database, model_class: Type[TModel], pk_field: str) -> None:
        self.session_factory = db.session
        self.model_class = model_class
        self.pk_field = pk_field

        assert hasattr(self.model_class, self.pk_field), "Wrong pk_field"

    @property
    def pk(self) -> Column:
        return getattr(self.model_class, self.pk_field)

    def all_as_select(self) -> Select[TModel]:
        return select(self.model_class)

    @handle_orm_error
    @inject_session
    async def all(self, *, session: AsyncSession = None) -> Result[TModel]:
        return await session.execute(self.all_as_select())

    @handle_orm_error
    @inject_session
    async def get_by_id(
        self,
        id_: int,
        *,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> TModel:
        qs = self.all_as_select().filter(self.pk == id_)
        if for_update:
            qs = qs.with_for_update()
        result = await session.execute(qs)
        first = result.first()
        return get_object_or_404(first[0] if first else None)

    @handle_orm_error
    @inject_session
    async def get_by_ids(
        self,
        ids: List[int],
        *,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> Select[TModel]:
        qs = self.all_as_select().filter(self.pk.in_(ids))
        if for_update:
            qs = qs.with_for_update()
        result = await session.execute(qs)
        first = result.first()
        return get_object_or_404(first[0] if first else None)

    @handle_orm_error
    @inject_session
    async def get_by_field(
        self,
        field: str,
        value: Any,
        *,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> TModel:
        qs = self.all_as_select().filter(getattr(self.model_class, field) == value)
        if for_update:
            qs = qs.with_for_update()
        result = await session.execute(qs)
        first = result.first()
        return get_object_or_404(first[0] if first else None)

    @handle_orm_error
    @inject_session
    async def get_by_filters(
        self,
        *,
        filters: Filters,
        operator_overrides: FieldToOperator | None = None,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> Result[TModel]:
        qs = self.all_as_select().filter(
            and_(
                *_build_filters(
                    self.model_class,
                    filters,
                    operator_overrides,
                )
            )
        )
        if for_update:
            qs = qs.with_for_update()
        print("COMPILED: ", qs.compile())
        return await session.execute(qs)

    @handle_orm_error
    @inject_session
    async def exists_by_field(
        self, field: str, value: Any, *, session: AsyncSession = None
    ) -> bool:
        qs = (
            self.all_as_select()
            .filter(getattr(self.model_class, field) == value)
            .limit(1)
        )
        result = await session.execute(qs)
        return result.first() is not None

    @handle_orm_error
    @inject_session
    async def create(
        self,
        entry: TSchema,
        *,
        session: AsyncSession = None,
    ) -> TModel:
        instance = self.model_class(**entry.model_dump())
        session.add(instance)
        await session.flush([instance])
        await session.refresh(instance)
        return instance

    @handle_orm_error
    @inject_session
    async def update(
        self,
        instance: TModel,
        values: Dict,
        *,
        session: AsyncSession = None,
    ) -> None:
        await session.execute(
            update(self.model_class)
            .filter(self.pk == getattr(instance, self.pk_field))
            .values(**values)
        )

    @handle_orm_error
    @inject_session
    async def multi_update(
        self,
        ids: List[int],
        *,
        values: Dict[str, Any],
        session: AsyncSession = None,
    ) -> None:
        await session.execute(
            update(self.model_class).filter(self.pk.in_(ids)).values(**values)
        )

    @handle_orm_error
    @inject_session
    async def delete(
        self,
        instance: TModel,
        *,
        session: AsyncSession = None,
    ) -> None:
        await session.execute(
            delete(self.model_class).filter(self.pk == getattr(instance, self.pk_field))
        )

    @handle_orm_error
    @inject_session
    async def delete_by_field(
        self,
        field: str,
        value: Any,
        *,
        session: AsyncSession = None,
    ) -> None:
        await session.execute(
            delete(self.model_class).filter(getattr(self.model_class, field) == value)
        )

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Column, Result, Select, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import Database
from utils.decorators import handle_orm_error
from utils.decorators import session as inject_session
from utils.shortcuts import get_object_or_404
from utils.sqlalchemy import IFilterSeq

TModel = TypeVar("TModel")
TSchema = TypeVar("TSchema", bound=BaseModel)


class IRepo(ABC, Generic[TModel]):
    @abstractmethod
    def __init__(self, db: Database, model_class: Type[TModel], pk_field: str) -> None:
        """
        :param db: database client instance
        :type db: Database
        :param model_class: orm model class
        :type model_class: Type[TModel]
        :param pk_field: primary key field name
        :type pk_field: str
        """
        ...

    @abstractmethod
    def all_as_select(self) -> Select[TModel]:
        """
        Construct select object for all rows

        :return: select object
        :rtype: Select[TModel]
        """
        ...

    @abstractmethod
    async def all(self, *, session: AsyncSession = None) -> Result[TModel]:
        """
        Get all rows

        :param session: orm session, defaults to None
        :type session: AsyncSession, optional
        :return: rows
        :rtype: Result[TModel]
        """
        ...

    @abstractmethod
    async def get_by_id(
        self,
        id_: int | str | UUID,
        *,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> TModel:
        """
        Get row by id

        :param id_: identifier of an object
        :type id_: int | str | UUID
        :param for_update: lock for update, defaults to False
        :type for_update: bool, optional
        :param session: orm session, defaults to None
        :type session: AsyncSession, optional
        :return: row
        :rtype: TModel
        """
        ...

    @abstractmethod
    async def get_by_ids(
        self,
        ids: List[int | str | UUID],
        *,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> Select[TModel]:
        """
        Get rows by identifiers

        :param ids: identifiers
        :type ids: List[int  |  str  |  UUID]
        :param for_update: lock for update, defaults to False
        :type for_update: bool, optional
        :param session: orm session, defaults to None
        :type session: AsyncSession, optional
        :return: rows
        :rtype: Select[TModel]
        """
        ...

    @abstractmethod
    async def get_by_field(
        self,
        field: str,
        value: Any,
        *,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> TModel:
        """
        Get row by field and its value

        :param field: field name
        :type field: str
        :param value: value of a field
        :type value: Any
        :param for_update: lock for update, defaults to False
        :type for_update: bool, optional
        :param session: orm session, defaults to None
        :type session: AsyncSession, optional
        :return: row
        :rtype: TModel
        """
        ...

    @abstractmethod
    async def get_by_filters(
        self,
        *,
        filters: IFilterSeq,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> Result[TModel]:
        """
        Get rows by filters

        :param filters: filter sequence
        :type filters: IFilterSeq
        :param for_update: lock for update, defaults to False
        :type for_update: bool, optional
        :param session: orm session, defaults to None
        :type session: AsyncSession, optional
        :return: rows
        :rtype: Result[TModel]
        """
        ...

    @abstractmethod
    async def exists_by_field(
        self,
        field: str,
        value: Any,
        *,
        session: AsyncSession = None,
    ) -> bool:
        """
        Check if row exist by field and its value

        :param field: field name
        :type field: str
        :param value: value
        :type value: Any
        :param session: orm session, defaults to None
        :type session: AsyncSession, optional
        :return: row existence
        :rtype: bool
        """
        ...

    @abstractmethod
    async def create(
        self,
        entry: TSchema,
        *,
        session: AsyncSession = None,
    ) -> TModel:
        """
        Insert row

        :param entry: entry with row data
        :type entry: TSchema
        :param session: orm session, defaults to None
        :type session: AsyncSession, optional
        :return: row
        :rtype: TModel
        """
        ...

    @abstractmethod
    async def update(
        self,
        instance: TModel,
        values: Dict,
        *,
        session: AsyncSession = None,
    ) -> None:
        """
        Update row

        :param instance: row to update
        :type instance: TModel
        :param values: values to update
        :type values: Dict
        :param session: orm session, defaults to None
        :type session: AsyncSession, optional
        """
        ...

    @abstractmethod
    async def multi_update(
        self,
        ids: List[int] | List[str] | List[UUID],
        *,
        values: Dict[str, Any],
        session: AsyncSession = None,
    ) -> None:
        """
        Update multiple rows by identifiers

        :param ids: identifiers
        :type ids: List[int  |  str  |  UUID]
        :param values: values to update
        :type values: Dict[str, Any]
        :param session: orm session, defaults to None
        :type session: AsyncSession, optional
        """
        ...

    @abstractmethod
    async def delete(
        self,
        instance: TModel,
        *,
        session: AsyncSession = None,
    ) -> None:
        """
        Delete row

        :param instance: row to delete
        :type instance: TModel
        :param session: orm session, defaults to None
        :type session: AsyncSession, optional
        """
        ...

    @abstractmethod
    async def delete_by_field(
        self,
        field: str,
        value: Any,
        *,
        session: AsyncSession = None,
    ) -> None:
        """
        Delete row by field and its value

        :param field: field name
        :type field: str
        :param value: value
        :type value: Any
        :param session: orm session, defaults to None
        :type session: AsyncSession, optional
        """
        ...


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
        filters: IFilterSeq,
        for_update: bool = False,
        session: AsyncSession = None,
    ) -> Result[TModel]:
        qs = self.all_as_select().filter(filters.compile())
        if for_update:
            qs = qs.with_for_update()
        return await session.execute(qs)

    @handle_orm_error
    @inject_session
    async def exists_by_field(
        self,
        field: str,
        value: Any,
        *,
        session: AsyncSession = None,
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
        ids: List[int] | List[str] | List[UUID],
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

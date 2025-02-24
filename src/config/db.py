import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("orm")


class Base(DeclarativeBase):
    pass


class Database:
    """
    Database class for client management
    """

    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, future=True, echo=True)
        self._session_factory = async_scoped_session(
            async_sessionmaker(
                class_=AsyncSession,
                autocommit=False,
                autoflush=True,
                bind=self._engine,
            ),
            scopefunc=asyncio.current_task,
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Context manager that produces async session.
        Handles commits, rollbacks and session closing.
        """
        session: AsyncSession = self._session_factory()
        try:
            logging.debug("YIELDING...")
            yield session
        except Exception as e:
            logging.debug("ROLLBACKING... ")
            await session.rollback()
            logging.debug("ERROR... ", str(e))
            logger.error(
                f"Session rollback because of exception - {str(e)}", exc_info=e
            )
            raise
        else:
            logging.debug("EXPUNGING...")
            # we want all objects to be
            # usable outside of the session
            session.expunge_all()
            logging.debug("COMMITTING... ")
            try:
                await session.commit()
            except SQLAlchemyError as e:
                logging.debug("ERROR COMMITTING...", str(e))
                await session.rollback()
                logger.error(
                    f"Session rollback because of exception on commit - {str(e)}",
                    exc_info=e,
                )
        finally:
            logging.debug("CLOSING... ")
            await session.close()

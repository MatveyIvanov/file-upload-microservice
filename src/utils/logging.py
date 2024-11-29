"""Implementation from https://habr.com/ru/articles/575454/"""

import datetime
import json
import logging
import os
import traceback
from pathlib import Path
from typing import Dict, Union

from pydantic import BaseModel, Field, ConfigDict

from config import settings

EMPTY_VALUE = ""
BUILTIN_RECORD_ATTRS_TO_IGNORE = set(
    (
        "name",
        "msg",
        "args",
        "levelno",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "threadName",
        "processName",
        "process",
    )
)


class BaseJsonLogSchema(BaseModel):
    """
    Base json log schema
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    thread: Union[int, str]
    level: int
    level_name: str
    message: str
    source: str
    timestamp: str = Field(..., alias="@timestamp")
    app_name: str
    app_version: str
    app_env: str
    duration: int
    exceptions: Union[list[str], str, None] = None
    trace_id: str | None = None
    span_id: str | None = None
    parent_id: str | None = None


class RequestJsonLogSchema(BaseModel):
    """
    Request/Response part of the log schema
    """

    request_uri: str
    request_referer: str
    request_protocol: str
    request_method: str
    request_path: str
    request_host: str
    request_size: int
    request_content_type: str
    request_headers: Dict
    request_body: Dict
    request_direction: str
    remote_ip: str
    remote_port: str | int
    response_status_code: int
    response_size: int
    response_headers: Dict
    response_body: Dict
    duration: int


class JSONLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord, *args, **kwargs) -> str:
        """
        Format log record to json.
        Log is filtered against sensitive fields.

        :param record: log record
        :type record: logging.LogRecord
        :return: json string
        :rtype: str
        """
        log_object = self._format_log_object(record)
        log_object = self._filter_sensitive_fields(log_object)
        return json.dumps(log_object, ensure_ascii=False)

    @staticmethod
    def _format_log_object(record: logging.LogRecord) -> Dict:
        """
        Log record to JSON schema convertation

        :param record: log record
        :type record: logging.LogRecord
        :return: dictionary with target schema
        :rtype: Dict
        """
        now = (
            datetime.datetime.fromtimestamp(record.created)
            .astimezone()
            .replace(microsecond=0)
            .isoformat()
        )
        message = record.getMessage()
        duration = record.duration if hasattr(record, "duration") else record.msecs
        json_log_fields = BaseJsonLogSchema(
            thread=record.process,
            timestamp=now,
            level=record.levelno,
            level_name=logging.getLevelName(record.levelno),
            message=message,
            source=record.name,
            duration=duration,
            app_name="APP",
            app_version="APP_VERSION",
            app_env="ENVIRONMENT",
            **{
                field: value
                for field, value in record.__dict__.items()
                if field not in BaseJsonLogSchema.model_fields.keys()
                and field not in BUILTIN_RECORD_ATTRS_TO_IGNORE
            },
        )

        if hasattr(record, "props"):
            json_log_fields.props = record.props

        if record.exc_info:
            json_log_fields.exceptions = traceback.format_exception(*record.exc_info)

        elif record.exc_text:
            json_log_fields.exceptions = record.exc_text

        json_log_object = json_log_fields.model_dump(
            exclude_unset=True,
            by_alias=True,
        )
        if hasattr(record, "request_json_fields"):
            json_log_object.update(record.request_json_fields)

        return json_log_object

    @staticmethod
    def _filter_sensitive_fields(data: Dict) -> Dict:
        """
        Filter sensitive data from log dictionary

        :param data: log dictionary
        :type data: Dict
        :return: filtered log dictionary
        :rtype: Dict
        """

        def _filter_dict(data: Dict):
            new_data = {}
            for k, v in data.items():
                if k.lower() not in settings.LOGGING_SENSITIVE_FIELDS:
                    if isinstance(v, dict):
                        new_data[k] = _filter_dict(v)
                    else:
                        new_data[k] = v
                else:
                    new_data[k] = "..."

            return new_data

        return _filter_dict(data)


def get_config(log_path: str) -> Dict:
    default_hanlder_settings = {
        "class": "logging.handlers.RotatingFileHandler",
        "encoding": "utf-8",
        "maxBytes": settings.LOGGING_MAX_BYTES,
        "backupCount": settings.LOGGING_BACKUP_COUNT,
        "formatter": "json",
    }
    handlers = {
        "uvicorn": {
            "level": "ERROR",
            "filename": os.path.join(log_path, "uvicorn.log"),
            "formatter": "json",
            **default_hanlder_settings,
        },
        "console": {
            "formatter": "verbose",
            "class": "logging.StreamHandler",
        },
    }
    loggers = {
        "uvicorn": {
            "handlers": ["uvicorn"],
            "level": "DEBUG" if settings.DEBUG else "ERROR",
            "propagate": False,
        },
        # Не даем стандартному логгеру fastapi работать
        # по пустякам и замедлять работу сервиса
        "uvicorn.access": {
            "handlers": ["uvicorn"],
            "level": "DEBUG" if settings.DEBUG else "ERROR",
            "propagate": False,
        },
        "": {
            "handlers": ["console"],
            "level": "DEBUG" if settings.DEBUG else "ERROR",
            "propagate": False,
        },
    }
    for logger_name in settings.LOGGING_LOGGERS:
        try:
            Path(log_path, logger_name).mkdir(parents=True, exist_ok=True)
        except (FileExistsError, FileNotFoundError):
            pass

        handlers[f"{logger_name}-info"] = {
            "level": "INFO",
            "filename": os.path.join(log_path, f"{logger_name}/info.log"),
            **default_hanlder_settings,
        }
        handlers[f"{logger_name}-errors"] = {
            "level": "ERROR",
            "filename": os.path.join(log_path, f"{logger_name}/errors.log"),
            **default_hanlder_settings,
        }
        loggers[logger_name] = {
            "handlers": [f"{logger_name}-info", f"{logger_name}-errors"],
            "level": "INFO",
            "propagate": False,
        }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "utils.logging.JSONLogFormatter",
            },
            "verbose": {
                "format": "[{asctime}] [{module}] [{funcName}] [{levelname}] {message}",
                "style": "{",
            },
        },
        "handlers": handlers,
        "loggers": loggers,
    }

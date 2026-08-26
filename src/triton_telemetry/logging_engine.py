"""Motor de logging estructurado y no bloqueante de Triton."""

import gzip
import json
import logging
import logging.config
import logging.handlers
import os
import queue
import shutil
from datetime import datetime, timezone


def gzip_namer(name):
    """Agrega la extensión .gz al archivo que será rotado."""
    return name + ".gz"


def gzip_rotator(source, dest):
    """Comprime el archivo rotado y elimina el archivo original."""
    with open(source, "rb") as source_file:
        with gzip.open(dest, "wb", compresslevel=9) as dest_file:
            shutil.copyfileobj(source_file, dest_file)

    os.remove(source)


class AsyncJSONFormatter(logging.Formatter):
    """Convierte los registros de logging en JSON estructurado."""

    def _serialize_exception(self, exc):
        """Serializa recursivamente una excepción y sus causas."""

        data = {
            "class": exc.__class__.__name__,
            "message": str(exc),
            "notes": getattr(exc, "__notes__", []),
        }

        # ExceptionGroup puede contener varias excepciones.
        if isinstance(exc, BaseExceptionGroup):
            data["nested_exceptions"] = [
                self._serialize_exception(child)
                for child in exc.exceptions
            ]

        # Conservamos la causa original de un raise ... from error.
        if exc.__cause__ is not None:
            data["cause"] = self._serialize_exception(exc.__cause__)

        return data

    def format(self, record):
        """Construye el registro JSON final."""

        timestamp = datetime.fromtimestamp(
            record.created,
            tz=timezone.utc,
        ).isoformat().replace("+00:00", "Z")

        payload = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "process": record.process,
            "thread_name": record.threadName,
            "task_name": getattr(record, "taskName", None),
            "filename": record.filename,
            "line": record.lineno,
        }

        # Si existe una excepción, guardamos todo su árbol.
        if record.exc_info:
            exc_value = record.exc_info[1]

            if exc_value is not None:
                payload["exception_tree"] = (
                    self._serialize_exception(exc_value)
                )

                payload["stack_trace"] = self.formatException(
                    record.exc_info
                )

        # Incorporamos metadatos agregados mediante logger(..., extra={...}).
        reserved_fields = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "taskName",
        }

        for key, value in record.__dict__.items():
            if key not in reserved_fields and not key.startswith("_"):
                payload[key] = value

        return json.dumps(
            payload,
            ensure_ascii=False,
        )


def setup_triton_logging(
    log_filename="triton_services.log",
):
    """Configura el pipeline de logging de Triton."""

    logging_schema = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "json_structured": {
                "()": AsyncJSONFormatter,
            },
            "console_clean": {
                "format": (
                    "%(asctime)s "
                    "[%(levelname)s] "
                    "(%(taskName)s) "
                    "%(message)s"
                ),
                "datefmt": "%H:%M:%S",
            },
        },

        "handlers": {
            "stdout_console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "console_clean",
                "stream": "ext://sys.stdout",
            },
            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "json_structured",
                "filename": log_filename,
                "maxBytes": 2 * 1024 * 1024,
                "backupCount": 3,
                "encoding": "utf-8",
            },
        },

        "loggers": {
            "triton_monitor": {
                "level": "DEBUG",
                "handlers": [
                    "stdout_console",
                    "rotating_file",
                ],
                "propagate": False,
            },
        },
    }

    # Construimos inicialmente los handlers mediante dictConfig.
    logging.config.dictConfig(logging_schema)

    logger = logging.getLogger("triton_monitor")

    # Buscamos el RotatingFileHandler configurado.
    file_handler = next(
        (
            handler
            for handler in logger.handlers
            if isinstance(
                handler,
                logging.handlers.RotatingFileHandler,
            )
        ),
        None,
    )

    if file_handler is not None:
        file_handler.namer = gzip_namer
        file_handler.rotator = gzip_rotator

    # Cola segura para transportar los LogRecord.
    log_queue = queue.Queue()

    queue_handler = logging.handlers.QueueHandler(log_queue)

    # Guardamos los handlers reales antes de reemplazarlos.
    real_handlers = logger.handlers.copy()

    # El listener será quien ejecute físicamente los handlers.
    listener = logging.handlers.QueueListener(
        log_queue,
        *real_handlers,
        respect_handler_level=True,
    )

    # Desde este momento el logger solamente coloca eventos en la cola.
    logger.handlers = [queue_handler]

    # Iniciamos el hilo consumidor.
    listener.start()

    # Guardamos una referencia para poder detenerlo posteriormente.
    logger.listener = listener

    return logger

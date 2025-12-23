import contextvars
import logging
import sys

trace_id_var = contextvars.ContextVar("trace_id", default="N/A")


class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = trace_id_var.get()
        return True


def setup_logger(name: str) -> logging.Logger:
    formatter = logging.Formatter(
        fmt="%(levelname)s:     [%(asctime)s] [TraceID: %(trace_id)s] %(name)s - %(message)s",
        datefmt="%H:%M:%S %d.%m.%Y"
    )

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addFilter(TraceIdFilter())
    logger.propagate = False

    loggers_to_patch = ["uvicorn", "uvicorn.access", "uvicorn.error"]
    for log_name in loggers_to_patch:
        uvicorn_logger = logging.getLogger(log_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.addHandler(handler)
        uvicorn_logger.addFilter(TraceIdFilter())
        uvicorn_logger.propagate = False

    return logger

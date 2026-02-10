"""
Structured JSON logging for CloudWatch compatibility.

This module provides JSON-formatted logging that includes correlation IDs,
timestamps, and structured fields for easy parsing in CloudWatch Logs.
"""

import logging
import json
import os
from datetime import datetime
from typing import Optional


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs as JSON.

    Includes standard fields:
    - timestamp: UTC timestamp in ISO format
    - level: Log level (DEBUG, INFO, WARNING, ERROR)
    - service: Service name (cortap-rpt)
    - module: Python module name
    - function: Function name where log was called
    - message: Log message
    - correlation_id: Request correlation ID (if available)
    - exception: Exception stack trace (if available)
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "cortap-rpt",
            "module": record.module,
            "function": record.funcName,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None)
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add any extra fields passed via extra parameter
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info",
                "correlation_id"
            ]:
                log_data[key] = value

        return json.dumps(log_data)


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger with JSON formatting.

    Args:
        name: Logger name (typically __name__)
        level: Optional log level override (defaults to env var LOG_LEVEL or INFO)

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request", extra={"correlation_id": "abc-123"})
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        # Set log level from parameter, env var, or default to INFO
        if level:
            log_level = level.upper()
        else:
            log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

    return logger


# Create a default logger for the app
default_logger = get_logger("cortap-rpt")

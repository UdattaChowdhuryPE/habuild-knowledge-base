import logging
import sys
import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structlog with JSON output and context propagation."""
    shared_processors = [
        structlog.contextvars.merge_contextvars,  # pulls request_id, user_id, etc from context
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    structlog.configure(
        processors=shared_processors
        + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
    )


def configure_tracing(app) -> None:
    """Configure OpenTelemetry tracing. ConsoleSpanExporter removed — it floods stdout at 500+ lines/sec in production."""
    provider = TracerProvider()
    trace.set_tracer_provider(provider)


def get_tracer(name: str):
    """Get a tracer instance for a module."""
    return trace.get_tracer(name)

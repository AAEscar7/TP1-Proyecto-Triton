"""Paquete Tritón Telemetry - Observabilidad Multicloud."""

from .exceptions import (
    CorruptedPayloadError,
    NetworkPeeringError,
    ProviderTimeoutError,
    TritonBaseError,
)
from .core import scan_all_providers, query_provider_telemetry
from .sanitizer import parse_cluster_id, parse_timeout

__all__ = [
    "TritonBaseError",
    "ProviderTimeoutError",
    "CorruptedPayloadError",
    "NetworkPeeringError",
    "scan_all_providers",
    "query_provider_telemetry",
    "parse_cluster_id",
    "parse_timeout",
]

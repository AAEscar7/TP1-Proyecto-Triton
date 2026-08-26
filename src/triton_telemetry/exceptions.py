"""Excepciones de Triton"""


class TritonBaseError(Exception):
    """Excepción base para los errores propios de Triton."""


class ProviderTimeoutError(TritonBaseError):
    """El proveedor no respondió dentro del tiempo permitido."""


class CorruptedPayloadError(TritonBaseError):
    """La respuesta del proveedor no tiene el formato esperado."""


class NetworkPeeringError(TritonBaseError):
    """Se produjo un problema de conectividad con el proveedor."""

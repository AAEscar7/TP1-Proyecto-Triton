"""Lógica asíncrona de telemetría del Proyecto Tritón."""

import asyncio
import httpx

from .exceptions import (
    CorruptedPayloadError,
    NetworkPeeringError,
    ProviderTimeoutError,
)


PROVIDER_URLS = {
    "AWS": "https://jsonplaceholder.typicode.com/posts/1",
    "Azure": "https://jsonplaceholder.typicode.com/posts/2",
    "GCP": "https://jsonplaceholder.typicode.com/posts/3",
}


CHAOS_URLS = {
    "AWS": "https://httpbin.org/delay/3",
    "Azure": "https://httpbin.org/status/504",
    "GCP": "https://httpbin.org/xml",
}


async def query_provider_telemetry(
    provider: str,
    timeout: float,
    chaos: bool = False,
):
    """
    Consulta la telemetría de un proveedor de forma asíncrona.

    En modo normal utiliza los endpoints nominales de JSONPlaceholder.
    En modo chaos utiliza endpoints de httpbin que provocan fallos
    controlados para probar la resiliencia del sistema.
    """

    # ---------------------------------------------------------
    # 1. Selección del endpoint
    # ---------------------------------------------------------

    if chaos and provider in CHAOS_URLS:
        url = CHAOS_URLS[provider]
    else:
        url = PROVIDER_URLS[provider]

    # ---------------------------------------------------------
    # 2. Consulta HTTP asíncrona
    # ---------------------------------------------------------

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                timeout=timeout,
            )

    except httpx.TimeoutException as error:
        triton_error = ProviderTimeoutError(
            f"{provider} no respondió dentro del timeout"
        )

        triton_error.add_note(f"Proveedor: {provider}")
        triton_error.add_note(
            f"Timeout configurado: {timeout} segundos"
        )
        triton_error.add_note(f"Endpoint: {url}")

        raise triton_error from error

    except httpx.RequestError as error:
        triton_error = NetworkPeeringError(
            f"{provider} no pudo establecer comunicación de red"
        )

        triton_error.add_note(f"Proveedor: {provider}")
        triton_error.add_note(
            f"Tipo de error HTTPX: {type(error).__name__}"
        )
        triton_error.add_note(f"Endpoint: {url}")

        raise triton_error from error

    # ---------------------------------------------------------
    # 3. Validación del código HTTP
    # ---------------------------------------------------------

    try:
        response.raise_for_status()

    except httpx.HTTPStatusError as error:
        triton_error = CorruptedPayloadError(
            f"{provider} respondió con HTTP "
            f"{error.response.status_code}"
        )

        triton_error.add_note(f"Proveedor: {provider}")
        triton_error.add_note(
            f"Código HTTP: {error.response.status_code}"
        )
        triton_error.add_note(f"Endpoint: {url}")

        raise triton_error from error

    # ---------------------------------------------------------
    # 4. Validación del payload JSON
    # ---------------------------------------------------------

    try:
        return response.json()

    except ValueError as error:
        triton_error = CorruptedPayloadError(
            f"{provider} devolvió un payload incompatible"
        )

        triton_error.add_note(f"Proveedor: {provider}")
        triton_error.add_note(f"Endpoint: {url}")
        triton_error.add_note(
            "Content-Type: "
            f"{response.headers.get('content-type', 'desconocido')}"
        )

        raise triton_error from error


async def scan_all_providers(
    providers: list[str],
    timeout: float,
    chaos: bool = False,
):
    """
    Consulta todos los proveedores concurrentemente.

    Las excepciones producidas por las tareas son agrupadas
    automáticamente por asyncio.TaskGroup en un ExceptionGroup.
    """

    tasks = {}

    # ---------------------------------------------------------
    # 5. Crear las tareas concurrentes
    # ---------------------------------------------------------

    async with asyncio.TaskGroup() as task_group:

        for provider in providers:
            tasks[provider] = task_group.create_task(
                query_provider_telemetry(
                    provider,
                    timeout,
                    chaos=chaos,
                ),
                name=f"telemetry-{provider}",
            )

    # ---------------------------------------------------------
    # 6. Recuperar resultados
    # ---------------------------------------------------------

    results = {}

    for provider, task in tasks.items():
        results[provider] = task.result()

    return results

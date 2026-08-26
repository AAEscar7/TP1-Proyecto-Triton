"""Punto de entrada CLI del Proyecto Tritón."""

import argparse
import asyncio

from triton_telemetry import (
    CorruptedPayloadError,
    NetworkPeeringError,
    ProviderTimeoutError,
    scan_all_providers,
)
from triton_telemetry.logging_engine import setup_triton_logging
from triton_telemetry.sanitizer import (
    parse_cluster_id,
    parse_timeout,
)


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logger = setup_triton_logging()


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

def build_cli_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos de la aplicación."""

    parser = argparse.ArgumentParser(
        prog="TritonMonitor",
        description=(
            "Sistema de Telemetría Multicloud y "
            "Observabilidad Asíncrona - Proyecto Tritón"
        ),
    )

    # Proveedores a monitorear
    parser.add_argument(
        "proveedores",
        nargs="+",
        choices=["AWS", "Azure", "GCP"],
        help="Proveedores cloud a monitorear.",
    )

    # Identificador del cluster
    parser.add_argument(
        "-c",
        "--cluster-id",
        type=parse_cluster_id,
        required=True,
        help=(
            "Identificador del cluster. "
            "Ejemplo: cluster-us-east-01"
        ),
    )

    # Timeout
    parser.add_argument(
        "-t",
        "--timeout",
        type=parse_timeout,
        default=2.5,
        help="Timeout HTTP entre 0.1 y 10.0 segundos.",
    )

    # Chaos
    parser.add_argument(
        "--chaos",
        action="store_true",
        help="Activa la simulación de fallos de red.",
    )

    # Modo operativo
    parser.add_argument(
        "-m",
        "--mode",
        choices=["nominal", "debug", "emergency"],
        default="nominal",
        help="Modo operativo del sistema.",
    )

    return parser


# ---------------------------------------------------------
# Manejo de errores
# ---------------------------------------------------------

def report_provider_timeout(group):
    """Reporta los ProviderTimeoutError contenidos en el grupo."""

    logger.error(
        "Se detectaron %d timeout(s) de proveedores.",
        len(group.exceptions),
    )

    for error in group.exceptions:
        logger.error("Proveedor: %s", error)

        for note in getattr(error, "__notes__", []):
            logger.error("  [FORENSE] %s", note)


def report_network_error(group):
    """Reporta los NetworkPeeringError contenidos en el grupo."""

    logger.error(
        "Se detectaron %d fallo(s) de red.",
        len(group.exceptions),
    )

    for error in group.exceptions:
        logger.error("Proveedor: %s", error)

        for note in getattr(error, "__notes__", []):
            logger.error("  [FORENSE] %s", note)


def report_corrupted_payload(group):
    """Reporta los CorruptedPayloadError contenidos en el grupo."""

    logger.error(
        "Se detectaron %d payload(s) incompatibles.",
        len(group.exceptions),
    )

    for error in group.exceptions:
        logger.error("Proveedor: %s", error)

        for note in getattr(error, "__notes__", []):
            logger.error("  [FORENSE] %s", note)


# ---------------------------------------------------------
# Ejecución principal
# ---------------------------------------------------------

async def async_main():
    """Ejecuta el ciclo principal de monitoreo."""

    parser = build_cli_parser()
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("INICIANDO PROYECTO TRITÓN")
    logger.info("Cluster: %s", args.cluster_id)
    logger.info("Modo: %s", args.mode)
    logger.info(
        "Proveedores: %s",
        ", ".join(args.proveedores),
    )
    logger.info("Timeout: %s segundos", args.timeout)

    if args.chaos:
        logger.warning("MODO CHAOS ACTIVADO")

    logger.info("=" * 60)

    try:
        results = await scan_all_providers(
            args.proveedores,
            args.timeout,
            chaos=args.chaos,
        )

        logger.info("MONITOREO COMPLETADO CORRECTAMENTE")

        for provider, result in results.items():
            logger.info(
                "%s -> %s",
                provider,
                result,
            )

    except* ProviderTimeoutError as group:
        report_provider_timeout(group)

    except* NetworkPeeringError as group:
        report_network_error(group)

    except* CorruptedPayloadError as group:
        report_corrupted_payload(group)

    finally:
        logger.info("=" * 60)
        logger.info("FIN DEL CICLO DE MONITOREO")
        logger.info("=" * 60)


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(async_main())

"""Punto de entrada CLI del Proyecto Tritón."""

import argparse
import asyncio
import sys

from triton_telemetry import (
    CorruptedPayloadError,
    NetworkPeeringError,
    ProviderTimeoutError,
    scan_all_providers,
)
from triton_telemetry.logging_engine import setup_triton_logging
from triton_telemetry.sanitizer import parse_cluster_id, parse_timeout


logger = setup_triton_logging()


def build_cli_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos de la aplicación CLI."""
    parser = argparse.ArgumentParser(
        prog="TritonMonitor",
        description="Sistema de Telemetría Multicloud y Observabilidad Asíncrona",
    )

    parser.add_argument(
        "proveedores",
        nargs="+",
        choices=["AWS", "Azure", "GCP"],
        help="Proveedores cloud a monitorear.",
    )

    parser.add_argument(
        "-c",
        "--cluster-id",
        type=parse_cluster_id,
        required=True,
        help="Identificador del clúster (Ejemplo: cluster-us-east-1).",
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=parse_timeout,
        default=2.5,
        help="Timeout HTTP (0.1 a 10.0 segundos).",
    )

    parser.add_argument(
        "--chaos",
        action="store_true",
        help="Activa la simulación de fallos de red en vivo.",
    )

    parser.add_argument(
        "-m",
        "--mode",
        choices=["nominal", "debug", "emergency"],
        default="nominal",
        help="Modo operativo del monitor.",
    )

    return parser


def report_provider_timeout(group: ExceptionGroup) -> None:
    """Reporta quirúrgicamente excepciones del tipo ProviderTimeoutError."""
    logger.error("Se detectaron %d timeout(s) de proveedor.",
                 len(group.exceptions))
    for error in group.exceptions:
        logger.error("Error detectado: %s", error)
        for note in getattr(error, "__notes__", []):
            logger.error("  [FORENSE] %s", note)


def report_network_error(group: ExceptionGroup) -> None:
    """Reporta quirúrgicamente excepciones del tipo NetworkPeeringError."""
    logger.error(
        "Se detectaron %d fallo(s) de conectividad/peering.", len(group.exceptions))
    for error in group.exceptions:
        logger.error("Error detectado: %s", error)
        for note in getattr(error, "__notes__", []):
            logger.error("  [FORENSE] %s", note)


def report_corrupted_payload(group: ExceptionGroup) -> None:
    """Reporta quirúrgicamente excepciones del tipo CorruptedPayloadError."""
    logger.error("Se detectaron %d payload(s) corruptos o estatus erróneos.", len(
        group.exceptions))
    for error in group.exceptions:
        logger.error("Error detectado: %s", error)
        for note in getattr(error, "__notes__", []):
            logger.error("  [FORENSE] %s", note)


async def async_main() -> None:
    """Ejecuta la orquestación principal de telemetría."""
    parser = build_cli_parser()
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("INICIANDO MONITOR DE TELEMETRÍA TRITÓN")
    logger.info("Clúster Target: %s", args.cluster_id)
    logger.info("Modo de Operación: %s", args.mode)
    logger.info("Proveedores Seleccionados: %s", ", ".join(args.proveedores))
    logger.info("Timeout Configurado: %s s", args.timeout)

    if args.chaos:
        logger.warning(
            "MODO CHAOS ACTIVADO: Simulando inyección de fallas en vivo")

    logger.info("=" * 60)

    try:
        results = await scan_all_providers(
            args.proveedores,
            args.timeout,
            chaos=args.chaos,
        )

        logger.info("EVALUACIÓN DE TELEMETRÍA COMPLETADA CON ÉXITO")
        for provider, result in results.items():
            logger.info("Métricas [%s]: %s", provider, result)

    except* ProviderTimeoutError as group:
        report_provider_timeout(group)

    except* NetworkPeeringError as group:
        report_network_error(group)

    except* CorruptedPayloadError as group:
        report_corrupted_payload(group)

    finally:
        logger.info("=" * 60)
        logger.info(
            "FINALIZANDO CICLO DE MONITOREO Y APAGANDO PIPELINE NO BLOQUEANTE")
        logger.info("=" * 60)
        # Detención limpia del QueueListener en el hilo secundario
        if hasattr(logger, "listener"):
            logger.listener.stop()


def main():
    """Punto de entrada síncrono del programa."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()

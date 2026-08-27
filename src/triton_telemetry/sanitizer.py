"""Módulo Sanitizer para validación de argumentos CLI."""

import argparse
import re


def parse_timeout(value: str) -> float:
    """Valida que el timeout sea un flotante entre 0.1 y 10.0 segundos."""
    try:
        timeout = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "El timeout debe ser un valor numérico validado."
        ) from error

    if not 0.1 <= timeout <= 10.0:
        raise argparse.ArgumentTypeError(
            "El timeout debe estar comprendido estrictamente entre 0.1 y 10.0 segundos."
        )

    return timeout


def parse_cluster_id(value: str) -> str:
    """Valida el patrón estricto del ID de clúster: cluster-[region]-[0-9]+"""
    pattern = r"^cluster-[a-z0-9-]+-[0-9]+$"

    if not re.fullmatch(pattern, value):
        raise argparse.ArgumentTypeError(
            "El ID del clúster debe respetar el patrón estricto: cluster-[region]-[0-9]+"
        )

    return value

"""Modulo Sanitizer"""

import argparse
import re


def parse_timeout(value):
    """Funcion de validacion del timeout"""
    try:
        timeout = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "el timeout debe ser un número"
        ) from error

    if not 0.1 <= timeout <= 10.0:
        raise argparse.ArgumentTypeError(
            "el timeout debe estar entre 0.1 y 10.0 segundos"
        )

    return timeout


def parse_cluster_id(value):
    """Funcion de validacion del nombre del cluster"""
    pattern = r"^cluster-[a-z]+(?:-[a-z]+)*-[0-9]+$"

    if not re.fullmatch(pattern, value):
        raise argparse.ArgumentTypeError(
            "el ID del cluster debe respetar el formato "
            "cluster-<region>-<numero>"
        )

    return value

from __future__ import annotations

import importlib
from pathlib import Path
from typing import List

from flask_restx import Namespace

_ROUTER_DIR = Path(__file__).resolve().parent


def _discover_namespaces() -> List[Namespace]:
    out: list[Namespace] = []
    for path in sorted(_ROUTER_DIR.glob('*.py')):
        stem = path.stem
        if stem.startswith('_'):
            continue
        mod = importlib.import_module(f'{__package__}.{stem}')
        for attr in sorted(dir(mod)):
            if not attr.endswith('_ns'):
                continue
            obj = getattr(mod, attr)
            if isinstance(obj, Namespace):
                out.append(obj)
    return out


ROUTER_NAMESPACES = _discover_namespaces()

__all__ = ['ROUTER_NAMESPACES']

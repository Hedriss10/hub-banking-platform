from typing import Any, List


def rows_from_json(payload: Any) -> List[Any]:
    if isinstance(payload, list):
        return payload
    if payload is None:
        return []
    return [payload]

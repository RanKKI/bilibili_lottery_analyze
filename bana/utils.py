import json

from typing import Any


def convert_json(data: Any, depth: int = 0) -> dict:
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            if depth == 0:
                raise ValueError("Not a valid json")
            return data
    if isinstance(data, list):
        for i in range(len(data)):
            data[i] = convert_json(data[i], depth + 1)
    if isinstance(data, dict):
        for key in data:
            data[key] = convert_json(data[key], depth + 1)
    return data

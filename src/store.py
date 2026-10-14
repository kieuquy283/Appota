from __future__ import annotations

import json
from pathlib import Path


SEED_PATH = Path(__file__).resolve().parents[1] / "data" / "seed.json"


def load_seed(path: Path = SEED_PATH) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def get_user(user_id: str, seed: dict) -> dict:
    for user in seed["users"]:
        if user["user_id"] == user_id and user["active"]:
            return user
    raise ValueError(f"Unknown or inactive user: {user_id}")

"""Load and validate a desk layout from JSON."""

from __future__ import annotations

import json
from pathlib import Path

from .models import DeskItem, Pose, Zone


def _pose(values: list[float]) -> Pose:
    if len(values) != 3:
        raise ValueError("poses must contain exactly [x, y, z]")
    return Pose(*map(float, values))


def load_layout(path: str | Path) -> tuple[dict, dict[str, Zone], dict[str, DeskItem]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {"workspace", "zones", "items", "home", "park"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"layout is missing: {', '.join(sorted(missing))}")

    zones = {
        name: Zone(
            name=name,
            center=_pose(value["center"]),
            width=float(value["width"]),
            depth=float(value["depth"]),
            kind=value.get("kind", "target"),
        )
        for name, value in data["zones"].items()
    }
    items = {
        name: DeskItem(
            name=name,
            pose=_pose(value["pose"]),
            mass_kg=float(value["mass_kg"]),
            category=value.get("category", "general"),
        )
        for name, value in data["items"].items()
    }
    data["home"] = _pose(data["home"])
    data["park"] = _pose(data["park"])
    return data, zones, items

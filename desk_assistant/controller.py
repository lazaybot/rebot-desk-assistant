"""Controller boundary. Only the non-hardware dry-run controller is included."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .models import TaskPlan


class DryRunController:
    """Record a validated plan without sending commands to physical hardware."""

    def execute(self, plan: TaskPlan, log_path: str | Path | None = None) -> list[dict]:
        events = []
        for index, step in enumerate(plan.steps, start=1):
            events.append({"index": index, **asdict(step), "status": "simulated"})
        if log_path is not None:
            payload = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "mode": "dry-run",
                "task": plan.task,
                "item": plan.item,
                "destination": plan.destination,
                "events": events,
            }
            destination = Path(log_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return events

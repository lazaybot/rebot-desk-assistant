"""Deterministic safety checks applied before any controller sees a plan."""

from __future__ import annotations

from dataclasses import dataclass

from .models import DeskItem, MotionStep, Pose, TaskPlan, Zone


class SafetyError(ValueError):
    """Raised when a requested desktop task violates a configured limit."""


@dataclass(frozen=True)
class SafetyPolicy:
    x_range: tuple[float, float]
    y_range: tuple[float, float]
    z_range: tuple[float, float]
    max_speed_mps: float
    max_payload_kg: float
    no_go_zones: tuple[Zone, ...] = ()

    @classmethod
    def from_layout(cls, data: dict, zones: dict[str, Zone]) -> "SafetyPolicy":
        workspace = data["workspace"]
        limits = data.get("limits", {})
        return cls(
            x_range=tuple(map(float, workspace["x"])),
            y_range=tuple(map(float, workspace["y"])),
            z_range=tuple(map(float, workspace["z"])),
            max_speed_mps=float(limits.get("max_speed_mps", 0.10)),
            max_payload_kg=float(limits.get("max_payload_kg", 0.25)),
            no_go_zones=tuple(z for z in zones.values() if z.kind == "no_go"),
        )

    def validate_pose(self, pose: Pose, *, allow_no_go_overflight: bool = False) -> None:
        for axis, value, bounds in (
            ("x", pose.x, self.x_range),
            ("y", pose.y, self.y_range),
            ("z", pose.z, self.z_range),
        ):
            if not bounds[0] <= value <= bounds[1]:
                raise SafetyError(f"{axis}={value:.3f} is outside {bounds}")
        for zone in self.no_go_zones:
            if zone.contains_xy(pose) and not allow_no_go_overflight:
                raise SafetyError(f"pose intersects no-go zone '{zone.name}'")

    def validate_item(self, item: DeskItem) -> None:
        if item.mass_kg <= 0:
            raise SafetyError("item mass must be positive")
        if item.mass_kg > self.max_payload_kg:
            raise SafetyError(
                f"'{item.name}' is {item.mass_kg:.3f} kg; configured desktop limit is "
                f"{self.max_payload_kg:.3f} kg"
            )

    def validate_plan(self, plan: TaskPlan) -> None:
        if not plan.steps:
            raise SafetyError("plan contains no steps")
        previous_pose = None
        for index, step in enumerate(plan.steps, start=1):
            if not 0 < step.speed_mps <= self.max_speed_mps:
                raise SafetyError(
                    f"step {index} speed {step.speed_mps:.3f} exceeds limit "
                    f"{self.max_speed_mps:.3f}"
                )
            if step.pose is not None:
                self.validate_pose(step.pose)
                if previous_pose is not None:
                    self._validate_segment(previous_pose, step.pose, index)
                previous_pose = step.pose
        if plan.steps[-1].action != "park":
            raise SafetyError("every task must end in a park step")

    def _validate_segment(self, start: Pose, end: Pose, step_index: int) -> None:
        """Reject a straight Cartesian segment that enters a protected XY zone."""
        samples = 50
        for sample in range(1, samples):
            ratio = sample / samples
            pose = Pose(
                x=start.x + (end.x - start.x) * ratio,
                y=start.y + (end.y - start.y) * ratio,
                z=start.z + (end.z - start.z) * ratio,
            )
            for zone in self.no_go_zones:
                if zone.contains_xy(pose):
                    raise SafetyError(
                        f"motion into step {step_index} crosses no-go zone '{zone.name}'"
                    )

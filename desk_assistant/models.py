"""Shared immutable data models used by the planner and safety layer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pose:
    x: float
    y: float
    z: float
    roll: float = 0.0
    pitch: float = 3.14159
    yaw: float = 0.0


@dataclass(frozen=True)
class Zone:
    name: str
    center: Pose
    width: float
    depth: float
    kind: str = "target"

    def contains_xy(self, pose: Pose) -> bool:
        return (
            abs(pose.x - self.center.x) <= self.width / 2
            and abs(pose.y - self.center.y) <= self.depth / 2
        )


@dataclass(frozen=True)
class DeskItem:
    name: str
    pose: Pose
    mass_kg: float
    category: str = "general"


@dataclass(frozen=True)
class MotionStep:
    action: str
    pose: Pose | None = None
    speed_mps: float = 0.08
    gripper: str | None = None
    note: str = ""


@dataclass(frozen=True)
class TaskPlan:
    task: str
    item: str
    destination: str
    steps: tuple[MotionStep, ...]

    @property
    def estimated_distance_m(self) -> float:
        poses = [step.pose for step in self.steps if step.pose is not None]
        distance = 0.0
        for start, end in zip(poses, poses[1:]):
            distance += (
                (end.x - start.x) ** 2
                + (end.y - start.y) ** 2
                + (end.z - start.z) ** 2
            ) ** 0.5
        return distance

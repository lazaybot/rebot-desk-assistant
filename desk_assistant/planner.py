"""Plan conservative desk tasks without depending on a robot SDK."""

from __future__ import annotations

from dataclasses import replace

from .models import DeskItem, MotionStep, Pose, TaskPlan, Zone
from .safety import SafetyError, SafetyPolicy


class DeskPlanner:
    def __init__(
        self,
        policy: SafetyPolicy,
        zones: dict[str, Zone],
        home: Pose,
        park: Pose,
        clearance_m: float = 0.12,
    ) -> None:
        self.policy = policy
        self.zones = zones
        self.home = home
        self.park_pose = park
        self.clearance_m = clearance_m

    def _approach(self, pose: Pose) -> Pose:
        z = min(pose.z + self.clearance_m, self.policy.z_range[1])
        return replace(pose, z=z)

    def plan_pick_place(self, item: DeskItem, destination: str, task: str) -> TaskPlan:
        if destination not in self.zones:
            raise SafetyError(f"unknown destination zone '{destination}'")
        zone = self.zones[destination]
        if zone.kind == "no_go":
            raise SafetyError(f"'{destination}' is a no-go zone")
        self.policy.validate_item(item)

        target = zone.center
        steps = (
            MotionStep("home", self.home, note="Known start pose"),
            MotionStep("open_gripper", self.home, gripper="open"),
            MotionStep("approach_pick", self._approach(item.pose)),
            MotionStep("descend_pick", item.pose, speed_mps=0.04),
            MotionStep("grasp", item.pose, speed_mps=0.03, gripper="close"),
            MotionStep("lift", self._approach(item.pose), speed_mps=0.05),
            MotionStep("approach_place", self._approach(target), speed_mps=0.06),
            MotionStep("descend_place", target, speed_mps=0.04),
            MotionStep("release", target, speed_mps=0.03, gripper="open"),
            MotionStep("retreat", self._approach(target), speed_mps=0.05),
            MotionStep("park", self.park_pose, speed_mps=0.06),
        )
        plan = TaskPlan(task, item.name, destination, steps)
        self.policy.validate_plan(plan)
        return plan

    def plan_present_tool(self, item: DeskItem) -> TaskPlan:
        return self.plan_pick_place(item, "handoff", "present-tool")

    def plan_sort(self, item: DeskItem) -> TaskPlan:
        destination = f"parts_{item.category}"
        return self.plan_pick_place(item, destination, "sort")

    def plan_inspect(self, item: DeskItem) -> TaskPlan:
        return self.plan_pick_place(item, "inspection", "inspect")

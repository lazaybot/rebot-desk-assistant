import json
import tempfile
import unittest
from pathlib import Path

from desk_assistant.controller import DryRunController
from desk_assistant.layout import load_layout
from desk_assistant.models import DeskItem, MotionStep, Pose, TaskPlan
from desk_assistant.planner import DeskPlanner
from desk_assistant.safety import SafetyError, SafetyPolicy


ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "desk_assistant" / "config" / "desk_layout.json"


class DeskAssistantTests(unittest.TestCase):
    def setUp(self):
        data, self.zones, self.items = load_layout(LAYOUT)
        self.policy = SafetyPolicy.from_layout(data, self.zones)
        self.planner = DeskPlanner(self.policy, self.zones, data["home"], data["park"])

    def test_present_tool_ends_parked(self):
        plan = self.planner.plan_present_tool(self.items["screwdriver"])
        self.assertEqual(plan.destination, "handoff")
        self.assertEqual(plan.steps[-1].action, "park")
        self.assertGreater(plan.estimated_distance_m, 0)

    def test_sort_uses_category_bin(self):
        plan = self.planner.plan_sort(self.items["red_connector"])
        self.assertEqual(plan.destination, "parts_red")

    def test_rejects_excess_payload(self):
        heavy = DeskItem("heavy", Pose(-0.2, 0.3, 0.04), 0.6)
        with self.assertRaisesRegex(SafetyError, "desktop limit"):
            self.planner.plan_present_tool(heavy)

    def test_rejects_no_go_pose(self):
        with self.assertRaisesRegex(SafetyError, "keyboard"):
            self.policy.validate_pose(Pose(0.2, 0.52, 0.04))

    def test_rejects_unsafe_speed(self):
        plan = TaskPlan(
            "bad",
            "test",
            "handoff",
            (MotionStep("park", Pose(0, 0.25, 0.3), speed_mps=0.5),),
        )
        with self.assertRaisesRegex(SafetyError, "exceeds limit"):
            self.policy.validate_plan(plan)

    def test_rejects_segment_crossing_no_go_zone(self):
        plan = TaskPlan(
            "crossing",
            "test",
            "handoff",
            (
                MotionStep("move", Pose(-0.10, 0.52, 0.30)),
                MotionStep("park", Pose(0.40, 0.52, 0.30)),
            ),
        )
        with self.assertRaisesRegex(SafetyError, "crosses no-go zone 'keyboard'"):
            self.policy.validate_plan(plan)

    def test_dry_run_writes_auditable_log(self):
        plan = self.planner.plan_inspect(self.items["circuit_board"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            events = DryRunController().execute(plan, path)
            saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(events), len(plan.steps))
        self.assertEqual(saved["mode"], "dry-run")
        self.assertTrue(all(event["status"] == "simulated" for event in events))


if __name__ == "__main__":
    unittest.main()

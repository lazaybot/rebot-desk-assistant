"""Command-line interface for planning and dry-running desk tasks."""

from __future__ import annotations

import argparse
import json
from importlib.resources import files

from .controller import DryRunController
from .layout import load_layout
from .planner import DeskPlanner
from .safety import SafetyError, SafetyPolicy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan safe reBot desk tasks")
    parser.add_argument(
        "--layout",
        default=str(files("desk_assistant").joinpath("config/desk_layout.json")),
        help="path to a desk layout JSON file",
    )
    parser.add_argument("--log", help="optional JSON execution-log path")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("present-tool", "sort", "inspect"):
        child = subparsers.add_parser(command)
        child.add_argument("item", help="item name from the layout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data, zones, items = load_layout(args.layout)
        if args.item not in items:
            raise SafetyError(f"unknown item '{args.item}'")
        planner = DeskPlanner(
            SafetyPolicy.from_layout(data, zones), zones, data["home"], data["park"]
        )
        item = items[args.item]
        plan = {
            "present-tool": planner.plan_present_tool,
            "sort": planner.plan_sort,
            "inspect": planner.plan_inspect,
        }[args.command](item)
        events = DryRunController().execute(plan, args.log)
    except (OSError, ValueError, KeyError, SafetyError) as error:
        print(f"ERROR: {error}")
        return 2

    print(f"DRY RUN: {plan.task} '{plan.item}' -> {plan.destination}")
    print(f"Estimated Cartesian travel: {plan.estimated_distance_m:.3f} m")
    for event in events:
        pose = event["pose"]
        position = "" if pose is None else f" ({pose['x']:.3f}, {pose['y']:.3f}, {pose['z']:.3f})"
        print(f"{event['index']:02d}. {event['action']}{position}")
    if args.log:
        print(f"Log: {args.log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# reBot Desk Assistant

This extension turns the reBot B601 hardware repository into a reproducible,
safety-first desktop workflow prototype. It plans three useful jobs:

- present a named hand tool at a handoff area;
- sort small parts into category bins;
- place a part at a camera inspection position.

The included controller is intentionally **dry-run only**. It validates and logs
Cartesian task plans but does not energize motors. A physical arm needs a
model-specific SDK adapter, measured coordinates, collision-aware trajectory
generation, emergency-stop hardware, and supervised commissioning.

## Quick start

Python 3.9 or newer is enough; the planner has no third-party runtime
dependencies.

```bash
python -m pip install --upgrade pip
python -m pip install -e .
rebot-desk present-tool screwdriver
python -m desk_assistant.cli present-tool screwdriver
python -m desk_assistant.cli --log outputs/sort-red.json sort red_connector
python -m desk_assistant.cli inspect circuit_board
python -m unittest discover -s tests -v
```

Coordinates and object names live in
`desk_assistant/config/desk_layout.json`. They are an example layout, not a
calibration for a real desk.

## Design

1. The layout defines the allowed workspace, no-go regions, named targets,
   object positions, and conservative speed/payload limits.
2. The planner generates approach, descend, grasp, lift, place, retreat, and
   park steps.
3. The safety policy rejects out-of-bounds poses, waypoints or straight motion
   segments crossing protected desk areas, excessive payloads, excessive
   speeds, and plans that do not finish parked.
4. The dry-run controller emits an auditable JSON log without talking to a
   motor controller.

## Recommended physical setup

- Soft TPU fingers from the upstream hardware files for small parts.
- A wrist depth camera using one of the upstream camera mounts.
- Fixed, high-contrast trays for handoff, inspection, and sorting zones.
- A rigid base clamp, physical emergency stop, and guarded operating area.

Do not use the arm to hand sharp, hot, powered, fragile, or heavy tools to a
person. The 250 g example limit is intentionally much lower than the arm's
advertised maximum payload; advertised capacity is not a safe desktop limit.

## Connecting real hardware

A hardware adapter should consume only a validated `TaskPlan`. Before enabling
it, add all of the following:

- inverse kinematics and collision checking for the exact B601 model;
- joint, torque, acceleration, and watchdog limits;
- calibrated transforms for the arm base, desk, camera, gripper, and trays;
- gripper force or current limiting;
- a physical emergency stop that does not depend on this Python process;
- hardware-in-the-loop tests with an empty workspace and reduced speed.

Until then, the correct execution mode is the included dry run.

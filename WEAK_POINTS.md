# Engineering review and improvement scope

## Weak points in the upstream project for this use case

The upstream repository is a strong hardware source and ecosystem index, but it
does not provide one integrated, reproducible desktop-assistant workflow.

- Control examples are spread across several external SDK, ROS, simulation,
  and community repositories.
- Payload and reach specifications do not define a safe human-adjacent desk
  envelope.
- Camera mounts exist, but a mount is not an end-to-end calibrated perception
  pipeline.
- Community safety features exist, but the root repository does not expose one
  task-level safety policy shared by every control stack.
- There is no simple task format for tool presentation, component sorting, or
  inspection-zone placement.
- There is no included hardware-in-the-loop evidence for this desk extension.

## What this extension changes

- Adds named, editable desk zones and items.
- Separates task planning from robot-specific motor control.
- Validates every plan before execution and requires a final park step.
- Protects a configured keyboard area as a no-go zone.
- Uses conservative payload and speed limits independent of marketing specs.
- Records deterministic dry-run logs for review and tests failure cases.

## Remaining limitations

This is a tested software prototype, not a completed physical appliance. It
does not yet include perception, inverse kinematics, collision geometry,
real-time control, motor feedback, or a verified B601 hardware adapter. Those
are the next engineering phase and should not be represented as complete.

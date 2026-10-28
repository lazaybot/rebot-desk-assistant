# reBot Desk Assistant

A safety-first desktop task planner for the [Seeed reBot B601 robotic arm](https://github.com/Seeed-Projects/reBot-DevArm).

This independent software extension plans three practical desk workflows:

- present a named hand tool at a designated handoff zone;
- sort small components into category bins;
- position a part for camera inspection.

It includes configurable desk geometry, protected no-go zones, conservative speed and payload limits, full motion-segment checks, mandatory safe parking, auditable dry-run logs, and automated tests.

## Status

**Tested software prototype — dry-run only.** It does not energize motors and has not been validated on a physical B601 arm. Real hardware operation still requires a model-specific SDK adapter, inverse kinematics, collision checking, calibration, watchdogs, and a physical emergency stop.

## Quick start

Python 3.9 or newer:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
rebot-desk present-tool screwdriver
rebot-desk sort red_connector
rebot-desk inspect circuit_board
python -m unittest discover -s tests -v
```

Use `--log outputs/run.json` to save an auditable dry-run log.

## Documentation

- [Setup, design, and safety](DESK_ASSISTANT.md)
- [Engineering review and remaining limitations](WEAK_POINTS.md)
- [Example desk layout](desk_assistant/config/desk_layout.json)

## Attribution and licensing

This project is an independent software extension inspired by the open-source [Seeed-Projects/reBot-DevArm](https://github.com/Seeed-Projects/reBot-DevArm) project. It is not endorsed by Seeed Studio and does not redistribute or modify the upstream mechanical design files.

The Python software in this repository is licensed under Apache-2.0. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

# Automated Scratch-Off Ticket System

This project is a Python-based robotic control system for automating the scratching of lottery tickets using either a CNC or a UR3 collaborative robot arm. The system includes hardware control, calibration utilities, and a local web-based GUI for selecting and running scratch programs. It also controls a single rail stepper driven camera system to track the robot arm's efforts.

## Features

- Supports CNC or UR3 robotic scratching modes (I think, CNC may have broken in this branch)
- CSV-defined ticket layouts and scratch zones
- Real-time GUI for manual control, program execution, and calibration
- Height compensation using Z-map
- Program modes: random, by group, and interruptible
- Serial-controlled Single Rail Stepper driven camera tracking system for inspection and alignment
- Modular design for extensibility


## Ticket Format (CSV)

Each ticket CSV contains entries like:

```
x, y, width, height, label, group, visible, priority, id
```

Used to define scratchable regions in physical coordinates (in mm).

## Basic Usage

1. Connect your CNC or UR3 robot and Arduino-based camera system
2. Run `python runner.py` to launch the system
3. Open the browser-based GUI at `http://localhost:8000`
4. Select a ticket and program
5. Calibrate if needed (top-left, bottom-left, height map)
6. Start the program

## Programs

- `random`: Scratch all visible boxes in random order
- `by_group`: Scratch by predefined groupings
- `by_group_interruptable`: Allows pausing and order changes mid-run

## Calibration Tools

- **Height Calibration:** Create or load a Z-map for consistent bit depth
- **Top/Bottom Corner Capture:** Align physical ticket placement
- **Camera Adjustment:** Move camera to inspect and confirm box positions

## Configuration Notes

Some settings like serial port (`COM4`, `COM9`) and IP address (`192.168.x.x`) are currently hardcoded in `settings.py` or other modules. These should be updated per machine or moved to a `.env` file or settings interface for production use.


## License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).

---


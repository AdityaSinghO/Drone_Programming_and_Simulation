# Drone Simulation Project

A Python-based drone simulation suite using `pysimverse`, featuring autonomous navigation scripts, keyboard-controlled flight with a live video feed, and hand gesture control powered by MediaPipe.

---

## Project Structure

```
.
├── 1_1_garage_navigation.py       # Basic single-leg autonomous flight
├── 1_2_garage_navigation.py       # Multi-leg autonomous navigation
├── 1_3_garage_navigation.py       # Advanced multi-leg navigation
├── 2_video_streaming_image_capturing.py  # Keyboard control + live feed + screenshots
├── 3_hand_controlled_drone.py     # Zone-based hand gesture control
├── 3_improved_hand_controls.py    # Full 6-DOF proportional hand gesture control
└── models/
    └── hand_landmarker.task       # MediaPipe hand landmark model
```

---

## Prerequisites

### Python Dependencies

```bash
pip install pysimverse opencv-python mediapipe keyboard
```

### MediaPipe Hand Landmark Model

Download `hand_landmarker.task` from the [MediaPipe Models page](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker) and place it at the path referenced in the hand control scripts:

```
models/hand_landmarker.task
```

> **Note:** The model path in `3_hand_controlled_drone.py` and `3_improved_hand_controls.py` is currently hardcoded. Update it to match your local setup before running.

---

## Scripts

### 1. Autonomous Navigation

Three scripts demonstrating pre-programmed flight paths — no input required once launched.

**`1_1_garage_navigation.py`** — Basic flight: rotate, set speed, move forward, land.

**`1_2_garage_navigation.py`** — Three separate takeoff-navigate-land sequences, each targeting a different heading and distance.

**`1_3_garage_navigation.py`** — Two-leg navigation with altitude control, covering longer distances.

```bash
python 1_1_garage_navigation.py
python 1_2_garage_navigation.py
python 1_3_garage_navigation.py
```

---

### 2. Keyboard Control + Video Feed

**`2_video_streaming_image_capturing.py`**

Fly the drone manually using your keyboard while viewing a live video feed. Press `Z` to save a timestamped screenshot.

**Controls:**

| Key | Action |
|-----|--------|
| `W` / `S` | Forward / Backward |
| `A` / `D` | Strafe Left / Right |
| `↑` / `↓` | Ascend / Descend |
| `←` / `→` | Rotate (Yaw) |
| `Z` | Save screenshot |
| `Q` | Land and quit |

Screenshots are saved to `drone_screenshots/` with the format `snapshot_YYYYMMDD_HHMMSS.png`.

```bash
python 2_video_streaming_image_capturing.py
```

---

### 3. Hand Gesture Control

#### Basic — Zone-Based (`3_hand_controlled_drone.py`)

Divides the webcam frame into three vertical zones. The drone yaws based on which zone your hand occupies.

| Zone | Action |
|------|--------|
| Left (< 33%) | Yaw left |
| Center (33–66%) | Hover |
| Right (> 66%) | Yaw right |

```bash
python 3_hand_controlled_drone.py
```

#### Improved — Full 6-DOF Proportional Control (`3_improved_hand_controls.py`)

A more sophisticated control scheme using hand position, span, and rotation relative to a calibrated anchor pose.

| Gesture | Drone Action |
|---------|-------------|
| Move hand left/right | Strafe left/right |
| Move hand up/down | Ascend/descend |
| Move hand toward/away from camera | Move forward/backward |
| Rotate hand (wrist twist) | Yaw left/right |
| Hold a fist for ~20 frames | Land and quit |
| Remove hand from frame | Reset anchor; drone hovers |

The anchor is set automatically when a hand is first detected. All movement is proportional — the further from the anchor position, the faster the drone responds.

```bash
python 3_improved_hand_controls.py
```

---

## Configuration

Key tuning constants are defined at the top of each script:

| Constant | Description |
|----------|-------------|
| `SPEED` | Max RC speed for lateral/vertical movement (default: 50) |
| `YAW_SPEED` | Max RC speed for rotation (default: 20–30) |
| `DEADZONE_XY` | Normalized deadzone radius around anchor (default: 0.06) |
| `MAX_RANGE_XY` | Normalized max displacement radius (default: 0.25) |
| `FIST_THRESHOLD` | Avg fingertip distance threshold to detect a fist (default: 0.12) |
| `FIST_HOLD_FRAMES` | Frames fist must be held to trigger landing (default: 20) |

---

## Notes

- The webcam index in the hand control scripts is set to `1`. Change `cv2.VideoCapture(1)` to `cv2.VideoCapture(0)` if your primary webcam isn't detected.
- The `keyboard` library used in the keyboard control script may require elevated permissions on some systems (e.g., `sudo` on Linux).
- All scripts connect to the simulator via `pysimverse`. Ensure the simulation environment is running before executing any script.

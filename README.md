# Gesture Remote

Pinch at your webcam to trigger a natural-language action on your Android phone, via
[Artemis](https://github.com/google/artemis).

Standalone project — unrelated to any other hand-tracking code.

## Setup

### 1. Install Artemis (one-time, run yourself)

```bash
git clone https://github.com/google/artemis.git
cd artemis
.\start.bat        # Windows; installs uv, adb, scrcpy, ffmpeg and configures Artemis
```

Then connect your phone:
1. Enable Developer Options > USB Debugging on the phone.
2. Plug in via USB and authorize the prompt on the device.
3. Verify: `adb devices` should list it.

Test Artemis works standalone:
```bash
uv run artemis run "Open Settings, find Battery and tell me current level" --profile flash
```

### 2. Point this project at your Artemis install

Edit [config.py](config.py) and set `ARTEMIS_DIR` to the full path of the artemis folder
you cloned above (the one containing `start.bat`).

### 3. Install this project's dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
python gesture_remote.py
```

Show a gesture to the webcam. After a short cooldown (`config.COOLDOWN_SECONDS`) it
dispatches the matching instruction from `config.GESTURE_INSTRUCTIONS` to Artemis, which
drives it on your phone. Press `q` in the video window to quit.

| Gesture | Default instruction |
|---|---|
| Pinch (thumb tip to index fingertip) | Open the Camera app and take a photo |
| V sign (index + middle up) | Take a screenshot |
| Thumbs up | Turn up the media volume |
| Open palm (all fingers up) | Go to the home screen |
| Fist | Lock the screen |

## Extending

Add more gestures by writing a detector function in [gesture_remote.py](gesture_remote.py),
adding it to `GESTURE_DETECTORS`, and adding an entry to `GESTURE_INSTRUCTIONS` in
[config.py](config.py) — no changes needed in [artemis_bridge.py](artemis_bridge.py).
Remove an entry from `GESTURE_INSTRUCTIONS` to disable that gesture without touching the
detection code.

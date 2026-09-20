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

### 4. (Optional) Customize gestures

```bash
python configure.py
```

Interactively pick a profile, edit which instruction each gesture sends, and tune hold
time / cooldown / pinch tolerance — no code editing required. Saved to `settings.json`
(gitignored, per-machine) and merged over the defaults in [config.py](config.py).

### 5. Run

```bash
python gesture_remote.py
```

Hold a gesture steady in front of the webcam. A progress bar fills over
`HOLD_SECONDS` (0.8s by default) before it fires — this is a deliberate confirmation
step so a passing hand shape doesn't accidentally lock your phone or send a text. Once
it fires, a "Sent: ..." toast confirms what was dispatched, and the same gesture can't
re-fire until `COOLDOWN_SECONDS` has passed. Press `q` in the video window to quit.

**Default profile** (5 gestures, quick actions):

| Gesture | Default instruction |
|---|---|
| Pinch (thumb tip to index fingertip) | Open the Camera app and take a photo |
| V sign (index + middle up) | Take a screenshot |
| Thumbs up | Turn up the media volume |
| Open palm (all fingers up) | Go to the home screen |
| Fist | Lock the screen |

**Accessibility profile** (`ACTIVE_PROFILE = "accessibility"` in config.py or via
`configure.py`): fewer gestures, a longer hold time, and a looser pinch tolerance —
tuned for tremor or limited hand mobility, favoring high-value one-handed actions over
gesture variety.

| Gesture | Default instruction |
|---|---|
| Open palm | Call `CONTACT_NAME` |
| Fist | Text `CONTACT_NAME` "I'm okay" |
| Thumbs up | Open Reminders and read today's reminders |

Set `CONTACT_NAME` in [config.py](config.py) or via `configure.py`.

## Extending

Add more gestures by writing a detector function in [gesture_remote.py](gesture_remote.py)
and adding it to `GESTURE_DETECTORS`. Everything else — which gestures are active, their
instructions, timing — lives in `config.PROFILES` and can be changed per-profile via
`configure.py` without touching detection code.

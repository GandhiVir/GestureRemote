"""Configuration for the gesture-to-phone remote.

Don't hand-edit GESTURE_INSTRUCTIONS/thresholds/CONTACT_NAME below if you just want to
customize behavior — run `python configure.py` instead; it writes overrides to
settings.json (gitignored) that are merged in at the bottom of this file.
"""

import json
import os

# Absolute path to your local clone of https://github.com/google/artemis
# (the folder containing start.bat / start.sh).
ARTEMIS_DIR = r"C:\path\to\artemis"

# Artemis execution profile: "flash" (fast, reactive) or "pro" (planning-based).
ARTEMIS_PROFILE = "flash"

# Name used in accessibility-profile instructions (e.g. "Call {CONTACT_NAME}").
CONTACT_NAME = "Mom"

# Which gesture profile is active: "default" or "accessibility".
ACTIVE_PROFILE = "default"

# Each profile bundles: how long a gesture must be held before it fires
# (hold_seconds), how long to wait before the same gesture can fire again
# (cooldown_seconds), how forgiving pinch detection is (pinch_threshold —
# larger tolerates a looser pinch), and which gestures map to which
# Artemis instructions.
PROFILES = {
    "default": {
        "hold_seconds": 0.8,
        "cooldown_seconds": 5.0,
        "pinch_threshold": 0.45,
        # Checked in order of specificity (pinch/v-sign first) so a gesture with
        # curled fingers isn't mistaken for a fist, matching HandTracking's ordering.
        "gesture_instructions": {
            "pinch": "Open the Camera app and take a photo",
            "v_sign": "Take a screenshot",
            "thumb_up": "Turn up the media volume",
            "open_palm": "Go to the home screen",
            "fist": "Lock the screen",
        },
    },
    # Fewer gestures, longer hold time, and looser thresholds for users with
    # limited hand mobility or tremor — favors avoiding accidental triggers
    # and high-value one-handed actions over gesture variety.
    "accessibility": {
        "hold_seconds": 1.5,
        "cooldown_seconds": 8.0,
        "pinch_threshold": 0.6,
        "gesture_instructions": {
            "open_palm": "Call {CONTACT_NAME}",
            "fist": "Send a text message to {CONTACT_NAME} saying I'm okay",
            "thumb_up": "Open the Reminders app and read today's reminders",
        },
    },
}


def resolve_instruction(instruction, contact_name):
    return instruction.format(CONTACT_NAME=contact_name) if "{CONTACT_NAME}" in instruction else instruction

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")


def _load_overrides():
    if not os.path.exists(SETTINGS_FILE):
        return
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        overrides = json.load(f)

    global ACTIVE_PROFILE, CONTACT_NAME
    ACTIVE_PROFILE = overrides.get("active_profile", ACTIVE_PROFILE)
    CONTACT_NAME = overrides.get("contact_name", CONTACT_NAME)

    for profile_name, profile_overrides in overrides.get("profiles", {}).items():
        profile = PROFILES.setdefault(profile_name, {})
        gesture_overrides = profile_overrides.pop("gesture_instructions", None)
        profile.update(profile_overrides)
        if gesture_overrides:
            profile.setdefault("gesture_instructions", {}).update(gesture_overrides)


_load_overrides()

ACTIVE = PROFILES[ACTIVE_PROFILE]
HOLD_SECONDS = ACTIVE["hold_seconds"]
COOLDOWN_SECONDS = ACTIVE["cooldown_seconds"]
PINCH_THRESHOLD = ACTIVE["pinch_threshold"]
GESTURE_INSTRUCTIONS = {
    gesture: resolve_instruction(instruction, CONTACT_NAME)
    for gesture, instruction in ACTIVE["gesture_instructions"].items()
}

"""Configuration for the gesture-to-phone remote."""

# Absolute path to your local clone of https://github.com/google/artemis
# (the folder containing start.bat / start.sh).
ARTEMIS_DIR = r"C:\path\to\artemis"

# Artemis execution profile: "flash" (fast, reactive) or "pro" (planning-based).
ARTEMIS_PROFILE = "flash"

# Seconds to wait after firing an instruction before the same gesture can fire again.
COOLDOWN_SECONDS = 5.0

# Normalized pinch distance (thumb tip to index tip, as a fraction of hand size)
# below which the hand is considered "pinched".
PINCH_THRESHOLD = 0.35

# Gesture -> natural-language instruction sent to Artemis.
GESTURE_INSTRUCTIONS = {
    "pinch": "Open the Camera app and take a photo",
}

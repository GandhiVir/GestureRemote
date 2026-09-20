"""Interactive CLI to customize gesture mappings without editing config.py.

Walks through picking a profile, editing its gesture instructions, hold/cooldown
timing, pinch tolerance, and the accessibility profile's contact name, then writes
the result to settings.json (gitignored, loaded automatically by config.py).
"""

import json

import config


def prompt(label, default):
    value = input(f"{label} [{default}]: ").strip()
    return value if value else default


def prompt_float(label, default):
    while True:
        raw = input(f"{label} [{default}]: ").strip()
        if not raw:
            return default
        try:
            return float(raw)
        except ValueError:
            print("Please enter a number.")


def main():
    print("Gesture Remote configuration\n")

    profile_names = list(config.PROFILES.keys())
    print("Available profiles:", ", ".join(profile_names))
    profile_name = prompt("Active profile", config.ACTIVE_PROFILE)
    if profile_name not in config.PROFILES:
        print(f"Unknown profile {profile_name!r}, keeping {config.ACTIVE_PROFILE!r}.")
        profile_name = config.ACTIVE_PROFILE

    profile = dict(config.PROFILES[profile_name])
    contact_name = config.CONTACT_NAME
    if profile_name == "accessibility":
        contact_name = prompt("Contact name used in accessibility instructions", contact_name)

    print(f"\nEditing profile {profile_name!r}. Press Enter to keep the current value.\n")

    profile["hold_seconds"] = prompt_float("Seconds to hold a gesture before it fires", profile["hold_seconds"])
    profile["cooldown_seconds"] = prompt_float(
        "Seconds before the same gesture can fire again", profile["cooldown_seconds"]
    )
    profile["pinch_threshold"] = prompt_float(
        "Pinch tolerance (higher = looser pinch accepted)", profile["pinch_threshold"]
    )

    print("\nGesture instructions (leave a line blank to remove that gesture):")
    gesture_instructions = {}
    for gesture, current in profile["gesture_instructions"].items():
        resolved_current = config.resolve_instruction(current, contact_name)
        value = prompt(f"  {gesture}", resolved_current)
        if value:
            gesture_instructions[gesture] = value
    profile["gesture_instructions"] = gesture_instructions

    settings = {
        "active_profile": profile_name,
        "contact_name": contact_name,
        "profiles": {profile_name: profile},
    }

    with open(config.SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

    print(f"\nSaved to {config.SETTINGS_FILE}")


if __name__ == "__main__":
    main()

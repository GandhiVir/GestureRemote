"""Webcam gesture detector that triggers Artemis phone-automation instructions.

Show a gesture to the webcam and it fires the matching instruction from
config.GESTURE_INSTRUCTIONS against your Android device via Artemis.
Press 'q' to quit.
"""

import time

import cv2
import mediapipe as mp

import artemis_bridge
import config

WRIST = 0
THUMB_TIP, THUMB_IP, THUMB_MCP = 4, 3, 2
INDEX_TIP, INDEX_PIP, INDEX_MCP = 8, 6, 5
MIDDLE_TIP, MIDDLE_PIP, MIDDLE_MCP = 12, 10, 9
RING_TIP, RING_PIP = 16, 14
PINKY_TIP, PINKY_PIP = 20, 18


def is_finger_up(hand, tip_idx, pip_idx):
    return hand[tip_idx].y < hand[pip_idx].y


def is_thumb_extended_up(hand):
    # Thumb landmarks run tip -> ip -> mcp; an upright thumb has each joint
    # higher (smaller y) than the one below it.
    return hand[THUMB_TIP].y < hand[THUMB_IP].y < hand[THUMB_MCP].y


def finger_states(hand):
    return (
        is_finger_up(hand, INDEX_TIP, INDEX_PIP),
        is_finger_up(hand, MIDDLE_TIP, MIDDLE_PIP),
        is_finger_up(hand, RING_TIP, RING_PIP),
        is_finger_up(hand, PINKY_TIP, PINKY_PIP),
    )


def is_pinch(hand):
    thumb_tip = hand[THUMB_TIP]
    index_tip = hand[INDEX_TIP]
    wrist = hand[WRIST]
    index_mcp = hand[INDEX_MCP]

    hand_scale = dist(wrist, index_mcp)
    pinch_distance = dist(thumb_tip, index_tip)
    return hand_scale > 0 and pinch_distance < hand_scale * config.PINCH_THRESHOLD


def is_v_sign(hand):
    index_up, middle_up, ring_up, pinky_up = finger_states(hand)
    return index_up and middle_up and not ring_up and not pinky_up


def is_thumb_up(hand):
    index_up, middle_up, ring_up, pinky_up = finger_states(hand)
    other_fingers_curled = not (index_up or middle_up or ring_up or pinky_up)
    return other_fingers_curled and is_thumb_extended_up(hand)


def is_open_palm(hand):
    index_up, middle_up, ring_up, pinky_up = finger_states(hand)
    return index_up and middle_up and ring_up and pinky_up


def is_fist(hand):
    index_up, middle_up, ring_up, pinky_up = finger_states(hand)
    all_curled = not (index_up or middle_up or ring_up or pinky_up)
    return all_curled and not is_thumb_extended_up(hand)


def dist(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5


# Checked in this order so a more specific gesture (e.g. pinch, with fingers
# mostly curled) isn't mistaken for a more general one (e.g. fist).
GESTURE_DETECTORS = [
    ("pinch", is_pinch),
    ("v_sign", is_v_sign),
    ("thumb_up", is_thumb_up),
    ("open_palm", is_open_palm),
    ("fist", is_fist),
]


def detect_gesture(hand):
    for name, detector in GESTURE_DETECTORS:
        if name in config.GESTURE_INSTRUCTIONS and detector(hand):
            return name
    return None


TOAST_SECONDS = 2.5


def main():
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    last_fired = 0.0
    held_gesture = None
    held_since = 0.0
    fired_this_hold = False
    toast_text = ""
    toast_until = 0.0

    with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5) as hands:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            gesture = None
            if results.multi_hand_landmarks:
                landmarks = results.multi_hand_landmarks[0]
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = detect_gesture(landmarks.landmark)

            now = time.time()

            if gesture != held_gesture:
                held_gesture = gesture
                held_since = now
                fired_this_hold = False

            held_duration = now - held_since if held_gesture else 0.0

            if (
                held_gesture
                and not fired_this_hold
                and held_duration >= config.HOLD_SECONDS
                and (now - last_fired) > config.COOLDOWN_SECONDS
            ):
                instruction = config.GESTURE_INSTRUCTIONS[held_gesture]
                artemis_bridge.dispatch(instruction)
                last_fired = now
                fired_this_hold = True
                toast_text = f"Sent: {instruction}"
                toast_until = now + TOAST_SECONDS

            draw_overlay(frame, held_gesture, held_duration, toast_text if now < toast_until else "")
            cv2.imshow("Gesture Remote", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


def draw_overlay(frame, gesture, held_duration, toast_text):
    h, w = frame.shape[:2]

    if gesture:
        progress = min(held_duration / config.HOLD_SECONDS, 1.0)
        label = gesture.upper() if progress >= 1.0 else f"{gesture.upper()} ({progress * 100:.0f}%)"
        cv2.putText(frame, label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        bar_x, bar_y, bar_w, bar_h = 10, 55, 200, 12
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (80, 80, 80), 1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_w * progress), bar_y + bar_h), (0, 255, 0), -1)
    else:
        cv2.putText(frame, "...", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    if toast_text:
        cv2.putText(frame, toast_text, (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)


if __name__ == "__main__":
    main()

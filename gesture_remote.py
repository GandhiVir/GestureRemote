"""Webcam gesture detector that triggers Artemis phone-automation instructions.

Show a pinch gesture (thumb tip touching index fingertip) to the webcam and it
fires the instruction configured in config.GESTURE_INSTRUCTIONS["pinch"]
against your Android device via Artemis. Press 'q' to quit.
"""

import time

import cv2
import mediapipe as mp

import artemis_bridge
import config

THUMB_TIP = 4
INDEX_TIP = 8
WRIST = 0
MIDDLE_MCP = 9


def hand_scale(landmarks):
    """Wrist-to-middle-knuckle distance, used to normalize pinch distance for hand size/depth."""
    wrist = landmarks[WRIST]
    middle_mcp = landmarks[MIDDLE_MCP]
    return ((wrist.x - middle_mcp.x) ** 2 + (wrist.y - middle_mcp.y) ** 2) ** 0.5


def is_pinch(landmarks):
    thumb = landmarks[THUMB_TIP]
    index = landmarks[INDEX_TIP]
    dist = ((thumb.x - index.x) ** 2 + (thumb.y - index.y) ** 2) ** 0.5
    scale = hand_scale(landmarks)
    if scale == 0:
        return False
    return (dist / scale) < config.PINCH_THRESHOLD


def main():
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    last_fired = 0.0
    was_pinching = False

    with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5) as hands:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            pinching = False
            if results.multi_hand_landmarks:
                landmarks = results.multi_hand_landmarks[0]
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
                pinching = is_pinch(landmarks.landmark)

            now = time.time()
            if pinching and not was_pinching and (now - last_fired) > config.COOLDOWN_SECONDS:
                instruction = config.GESTURE_INSTRUCTIONS["pinch"]
                artemis_bridge.dispatch(instruction)
                last_fired = now
            was_pinching = pinching

            status = "PINCH" if pinching else "..."
            cv2.putText(frame, status, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Gesture Remote", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

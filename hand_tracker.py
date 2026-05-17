import threading
import time

import cv2
import mediapipe as mp

from config import (
    CAM_H,
    CAM_W,
    DOWN,
    ENABLE_HAND_SKELETON,
    FINGER_THRESHOLD,
    HAND_CONNECTIONS,
    INDEX_FINGER_TIP,
    LEFT,
    RIGHT,
    UP,
)
from gestures import GestureRecognizer


class HandTracker:
    def __init__(self, model_path: str):
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision as mp_vision

        self._mp = mp
        self._mp_vision = mp_vision
        self._mp_python = mp_python

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Webcam tidak ditemukan. Gunakan keyboard WASD sebagai fallback.")
            self.available = False
        else:
            self.available = True

        if self.available:
            try:
                base_opts = mp_python.BaseOptions(model_asset_path=model_path)
                options = mp_vision.HandLandmarkerOptions(
                    base_options=base_opts,
                    running_mode=mp_vision.RunningMode.VIDEO,
                    num_hands=1,
                    min_hand_detection_confidence=0.5,
                    min_hand_presence_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
                self._detector = mp_vision.HandLandmarker.create_from_options(options)
                print("MediaPipe HandLandmarker berhasil diinisialisasi.")
            except Exception as e:
                print(f"Gagal membuat HandLandmarker: {e}")
                self.available = False

        self._lock = threading.Lock()
        self._direction = None
        self._gesture = None
        self._gesture_label = "NO HAND"
        self._cam_frame = None
        self._prev_finger_pos = None
        self._recognizer = GestureRecognizer()
        self._last_gesture = None
        self._last_gesture_ts = 0.0
        self._running = True

        if self.available:
            self._thread = threading.Thread(target=self._tracking_loop, daemon=True)
            self._thread.start()

    def _draw_hand_skeleton(self, frame, landmarks_px):
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, landmarks_px[a], landmarks_px[b], (0, 160, 80), 2)

        for i, (lx, ly) in enumerate(landmarks_px):
            if i == INDEX_FINGER_TIP:
                cv2.circle(frame, (lx, ly), 12, (0, 200, 60), -1)
                cv2.circle(frame, (lx, ly), 8, (255, 220, 0), -1)
            else:
                cv2.circle(frame, (lx, ly), 4, (0, 220, 120), -1)

    def _tracking_loop(self):
        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int(time.monotonic() * 1000)

            try:
                result = self._detector.detect_for_video(mp_image, timestamp_ms)
            except Exception:
                time.sleep(0.01)
                continue

            detected_direction = None
            detected_gesture = None
            gesture_label = "NO HAND"

            if result.hand_landmarks:
                hand = result.hand_landmarks[0]
                gesture_label = self._recognizer.classify(hand) or "TRACKING"
                landmarks_px = [(int(lm.x * w), int(lm.y * h)) for lm in hand]
                if ENABLE_HAND_SKELETON:
                    self._draw_hand_skeleton(frame, landmarks_px)

                curr_x, curr_y = landmarks_px[INDEX_FINGER_TIP]
                cv2.putText(frame, f"({curr_x},{curr_y})",
                            (curr_x + 14, curr_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 255, 200), 1)

                if gesture_label != "TRACKING":
                    now = time.monotonic()
                    if (gesture_label != self._last_gesture or
                            now - self._last_gesture_ts > 1.2):
                        detected_gesture = gesture_label
                        self._last_gesture = gesture_label
                        self._last_gesture_ts = now
                    cv2.putText(frame, gesture_label,
                                (8, 28), cv2.FONT_HERSHEY_SIMPLEX,
                                0.55, (80, 220, 255), 2)

                if self._prev_finger_pos is not None:
                    prev_x, prev_y = self._prev_finger_pos
                    dx = curr_x - prev_x
                    dy = curr_y - prev_y

                    if max(abs(dx), abs(dy)) > FINGER_THRESHOLD:
                        if abs(dx) >= abs(dy):
                            detected_direction = RIGHT if dx > 0 else LEFT
                        else:
                            detected_direction = DOWN if dy > 0 else UP

                self._prev_finger_pos = (curr_x, curr_y)
            else:
                self._prev_finger_pos = None
                self._last_gesture = None
                cv2.putText(frame, "Arahkan jari ke kamera",
                            (8, 28), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (80, 80, 220), 1)

            cv2.putText(frame, f"Min geser: {FINGER_THRESHOLD}px",
                        (5, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                        (120, 120, 120), 1)

            with self._lock:
                self._direction = detected_direction
                if detected_gesture is not None:
                    self._gesture = detected_gesture
                self._gesture_label = gesture_label
                self._cam_frame = cv2.resize(frame, (CAM_W, CAM_H))

    def get_direction(self):
        with self._lock:
            d = self._direction
            self._direction = None
        return d

    def get_gesture(self):
        with self._lock:
            g = self._gesture
            self._gesture = None
        return g

    def get_status_label(self):
        with self._lock:
            return self._gesture_label

    def get_cam_frame(self):
        with self._lock:
            return self._cam_frame.copy() if self._cam_frame is not None else None

    def stop(self):
        self._running = False
        if self.available:
            self.cap.release()
            try:
                self._detector.close()
            except Exception:
                pass

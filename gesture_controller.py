"""Gesture controller for BIOCORE AI.

Detecta gestos de mano con OpenCV + MediaPipe y los mapea a acciones del dashboard.
"""

import io
from typing import Optional
import importlib

try:
    cv2 = importlib.import_module('cv2')
except Exception:
    cv2 = None

try:
    Image = importlib.import_module('PIL.Image')
except Exception:
    Image = None


def _resolve_mediapipe_solutions():
    candidates = [
        'mediapipe.solutions',
        'mediapipe.python.solutions',
        'mediapipe.python.solutions.hands',
    ]
    for candidate in candidates:
        try:
            module = importlib.import_module(candidate)
            if candidate.endswith('.hands') or hasattr(module, 'hands'):
                return module
        except Exception:
            continue
    return None


try:
    mp = importlib.import_module('mediapipe')
except Exception as e:
    mp = None
    mp_import_error = str(e)
    solutions = None
    mp_solutions_available = False
else:
    mp_import_error = None
    solutions = _resolve_mediapipe_solutions()
    if solutions is None and hasattr(mp, 'solutions'):
        solutions = mp.solutions
    mp_solutions_available = solutions is not None and (
        hasattr(solutions, 'hands') or hasattr(solutions, 'Hands')
    )

import numpy as np

GESTURE_ACTIONS = {
    'open_palm': 'pause_resume',
    'index': 'next_view',
    'two_fingers': 'change_module',
    'ok_sign': 'generate_report',
    'pinch': 'zoom_ecg',
}


class GestureController:
    def __init__(self):
        self.available = False
        self.hands = None
        self.mp_hands = None
        
        # Check all dependencies
        if cv2 is None or Image is None:
            reason = []
            if cv2 is None:
                reason.append("opencv-python")
            if Image is None:
                reason.append("Pillow")
            print(f"Gesture control unavailable. Missing: {', '.join(reason)}. "
                  f"Install with: pip install opencv-python pillow")
            return
        
        # Check MediaPipe
        if mp is None or not mp_solutions_available:
            error_detail = f" Details: {mp_import_error}" if mp_import_error else ""
            print(f"Gesture control unavailable. MediaPipe not properly installed or unsupported version.{error_detail} "
                  f"Try: pip install --upgrade mediapipe")
            return
        
        try:
            # Initialize MediaPipe Hands with proper error handling
            self.mp_hands = solutions if hasattr(solutions, 'Hands') else solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=1,
                min_detection_confidence=0.65,
                min_tracking_confidence=0.5,
            )
            self.available = True
            print("MediaPipe Hands initialized successfully")
        except Exception as e:
            self.available = False
            self.hands = None
            self.mp_hands = None
            print(f"MediaPipe initialization failed: {e}. "
                  f"Try: pip install --upgrade --force-reinstall mediapipe")

    def detect_gesture(self, image_data) -> Optional[str]:
        if not self.available:
            return None
        try:
            if isinstance(image_data, (bytes, bytearray)):
                image = Image.open(io.BytesIO(image_data)).convert('RGB')
            elif isinstance(image_data, np.ndarray):
                if image_data.ndim == 3 and image_data.shape[2] == 3:
                    image = Image.fromarray(cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB))
                else:
                    image = Image.fromarray(image_data)
                image = image.convert('RGB')
            else:
                image = Image.open(image_data).convert('RGB')
        except Exception as e:
            print(f"GestureController image conversion failed: {e}")
            return None

        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not results or not results.multi_hand_landmarks:
            return None
        landmarks = results.multi_hand_landmarks[0].landmark
        handedness = results.multi_handedness[0].classification[0].label if results.multi_handedness else 'Right'
        return self._classify(landmarks, handedness)

    def _classify(self, landmarks, hand_label: str) -> Optional[str]:
        finger_state = {
            'thumb': self._thumb_extended(landmarks, hand_label),
            'index': self._finger_extended(landmarks, 8, 6),
            'middle': self._finger_extended(landmarks, 12, 10),
            'ring': self._finger_extended(landmarks, 16, 14),
            'pinky': self._finger_extended(landmarks, 20, 18),
        }
        extended = [k for k, v in finger_state.items() if v]
        if len(extended) == 5:
            return 'open_palm'
        if finger_state['index'] and not any(finger_state[x] for x in ['middle', 'ring', 'pinky']):
            return 'index'
        if finger_state['index'] and finger_state['middle'] and not any(finger_state[x] for x in ['ring', 'pinky']):
            return 'two_fingers'
        if self._is_ok_sign(landmarks):
            return 'ok_sign'
        if self._is_pinch(landmarks):
            return 'pinch'
        return None

    def _finger_extended(self, landmarks, tip_idx: int, pip_idx: int) -> bool:
        return landmarks[tip_idx].y < landmarks[pip_idx].y

    def _thumb_extended(self, landmarks, hand_label: str) -> bool:
        tip = landmarks[4]
        ip = landmarks[3]
        if hand_label == 'Right':
            return tip.x > ip.x
        return tip.x < ip.x

    def _distance(self, first, second) -> float:
        return np.linalg.norm(np.array((first.x, first.y)) - np.array((second.x, second.y)))

    def _is_ok_sign(self, landmarks) -> bool:
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        dist = self._distance(thumb_tip, index_tip)
        return dist < 0.06 and not self._finger_extended(landmarks, 12, 10) and not self._finger_extended(landmarks, 16, 14)

    def _is_pinch(self, landmarks) -> bool:
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        dist = self._distance(thumb_tip, index_tip)
        return dist < 0.05

    def gesture_to_action(self, label: Optional[str]) -> Optional[str]:
        if label is None:
            return None
        return GESTURE_ACTIONS.get(label)

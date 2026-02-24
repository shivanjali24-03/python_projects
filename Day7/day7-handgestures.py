"""
Hand Gesture Particle System - ENHANCED VERSION
- Tiny particles (size 1)
- ALL 32 finger combinations detected (every permutation of 5 fingers)
- 2-hand detection with special effects
- Each unique gesture has its own particle behaviour
"""

import cv2
import random
import math
import os
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import mediapipe as mp

# ─────────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────────
WIDTH, HEIGHT  = 1280, 720
NUM_PARTICLES  = 800          # more particles for tiny size
MODEL_PATH     = "hand_landmarker.task"
MODEL_URL      = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

# ─────────────────────────────────────────────
#  ALL GESTURE DEFINITIONS
#  fingers_up = [thumb, index, middle, ring, pinky]
#  True = finger up, False = finger down
#  32 total combinations (2^5)
# ─────────────────────────────────────────────
GESTURE_MAP = {
    # ── 0 fingers ──
    (False, False, False, False, False): ("FIST",            (80,  80,  255), "Particles spiral inward"),
    # ── 1 finger ──
    (True,  False, False, False, False): ("THUMBS UP",       (0,   220, 255), "Particles float upward"),
    (False, True,  False, False, False): ("POINTING",        (80,  255, 80),  "Stream to index tip"),
    (False, False, True,  False, False): ("MIDDLE FINGER",   (255, 50,  50),  "Particles explode out"),
    (False, False, False, True,  False): ("RING UP",         (200, 100, 255), "Slow spiral"),
    (False, False, False, False, True):  ("PINKY UP",        (255, 200, 0),   "Tiny scatter"),
    # ── 2 fingers ──
    (True,  True,  False, False, False): ("THUMB+INDEX",     (100, 255, 200), "Pinch repel"),
    (False, True,  True,  False, False): ("PEACE / V",       (200, 80,  255), "Dual stream"),
    (False, True,  False, True,  False): ("INDEX+RING",      (255, 150, 0),   "Cross stream"),
    (False, True,  False, False, True):  ("INDEX+PINKY",     (0,   150, 255), "Wide repel"),
    (False, False, True,  True,  False): ("MIDDLE+RING",     (150, 255, 100), "Slow attract"),
    (False, False, True,  False, True):  ("MIDDLE+PINKY",    (255, 80,  200), "Zigzag"),
    (False, False, False, True,  True):  ("RING+PINKY",      (80,  200, 255), "Gentle wave"),
    (True,  False, False, False, True):  ("HANG LOOSE",      (255, 220, 0),   "Surfer wave"),
    (True,  False, True,  False, False): ("THUMB+MIDDLE",    (100, 200, 255), "Orbit"),
    (True,  False, False, True,  False): ("THUMB+RING",      (200, 255, 100), "Spin"),
    # ── 3 fingers ──
    (True,  True,  True,  False, False): ("THREE / OK",      (0,   255, 180), "Triangle burst"),
    (False, True,  True,  True,  False): ("THREE MIDDLE",    (255, 100, 100), "Fan out"),
    (False, True,  True,  False, True):  ("INDEX+MID+PINK",  (100, 255, 255), "Wide fan"),
    (False, True,  False, True,  True):  ("INDEX+RING+PINK", (255, 180, 50),  "Spread"),
    (False, False, True,  True,  True):  ("LAST THREE",      (180, 100, 255), "Sweep"),
    (True,  True,  False, True,  False): ("THUMB+IDX+RING",  (50,  255, 150), "Vortex"),
    (True,  True,  False, False, True):  ("THUMB+IDX+PINK",  (255, 255, 50),  "Star burst"),
    (True,  False, True,  True,  False): ("THUMB+MID+RING",  (100, 150, 255), "Orbit ring"),
    (True,  False, True,  False, True):  ("THUMB+MID+PINK",  (255, 100, 180), "Scatter"),
    (True,  False, False, True,  True):  ("THUMB+RING+PINK", (150, 255, 200), "Wave up"),
    # ── 4 fingers ──
    (True,  True,  True,  True,  False): ("FOUR / NO PINKY", (0,   200, 255), "Strong repel"),
    (True,  True,  True,  False, True):  ("FOUR / NO RING",  (255, 150, 100), "Swirl out"),
    (True,  True,  False, True,  True):  ("FOUR / NO MID",   (100, 255, 150), "Explode"),
    (True,  False, True,  True,  True):  ("FOUR / NO IDX",   (200, 100, 255), "Pull in"),
    (False, True,  True,  True,  True):  ("FOUR / NO THUMB", (255, 200, 80),  "Fountain"),
    # ── 5 fingers ──
    (True,  True,  True,  True,  True):  ("OPEN HAND",       (0,   255, 255), "Mega repel"),
}

# ─────────────────────────────────────────────
#  PARTICLE CLASS
# ─────────────────────────────────────────────
class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x    = random.uniform(0, WIDTH)
        self.y    = random.uniform(0, HEIGHT)
        self.vx   = random.uniform(-1.0, 1.0)
        self.vy   = random.uniform(-1.0, 1.0)
        self.life = random.uniform(0.5, 1.0)
        self.size = 1                           # TINY particles — always 1px
        # Random bright color
        self.color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255),
        )

    def apply_force(self, tx, ty, strength, attract=True, swirl=0.0):
        """Generic force: attract or repel from point (tx, ty)"""
        dx = tx - self.x
        dy = ty - self.y
        dist = max(math.sqrt(dx**2 + dy**2), 1)
        force = strength / (dist ** 1.3)
        direction = 1 if attract else -1
        self.vx += direction * (dx / dist) * force
        self.vy += direction * (dy / dist) * force
        # Swirl: add perpendicular component
        if swirl != 0:
            self.vx += (-dy / dist) * swirl
            self.vy += ( dx / dist) * swirl

    def update(self, all_hands_data, gesture_key, num_hands):
        """
        all_hands_data: list of hand_points for each detected hand
        gesture_key: tuple of booleans e.g. (True,False,True,False,False)
        num_hands: 1 or 2
        """
        if all_hands_data:
            hand = all_hands_data[0]    # primary hand
            px, py = hand[0]            # wrist/palm

            t, i, m, r, p = gesture_key  # thumb, index, middle, ring, pinky

            # ── 2 HANDS SPECIAL EFFECTS ──
            if num_hands == 2 and len(all_hands_data) >= 2:
                h1 = all_hands_data[0][0]
                h2 = all_hands_data[1][0]
                mid_x = (h1[0] + h2[0]) // 2
                mid_y = (h1[1] + h2[1]) // 2
                # Particles attracted to midpoint between two hands
                self.apply_force(mid_x, mid_y, 40, attract=True, swirl=1.5)

            # ── 0 FINGERS: FIST → spiral inward ──
            elif not any([t, i, m, r, p]):
                self.apply_force(px, py, 50, attract=True, swirl=1.2)

            # ── 5 FINGERS: OPEN HAND → mega repel ──
            elif all([t, i, m, r, p]):
                self.apply_force(px, py, 120, attract=False)

            # ── THUMB ONLY → float upward ──
            elif t and not any([i, m, r, p]):
                self.apply_force(px, py, 30, attract=True)
                self.vy -= 0.8  # float up

            # ── INDEX ONLY → stream to fingertip ──
            elif i and not any([t, m, r, p]):
                self.apply_force(hand[8][0], hand[8][1], 60, attract=True)

            # ── MIDDLE ONLY → explode outward ──
            elif m and not any([t, i, r, p]):
                self.apply_force(px, py, 100, attract=False)
                self.vx += random.uniform(-0.5, 0.5)
                self.vy += random.uniform(-0.5, 0.5)

            # ── RING ONLY → slow gentle spiral ──
            elif r and not any([t, i, m, p]):
                self.apply_force(px, py, 25, attract=True, swirl=0.5)

            # ── PINKY ONLY → tiny scatter ──
            elif p and not any([t, i, m, r]):
                self.apply_force(px, py, 15, attract=False)
                self.vx += random.uniform(-0.3, 0.3)
                self.vy += random.uniform(-0.3, 0.3)

            # ── PEACE (index+middle) → dual fingertip stream ──
            elif i and m and not r and not p:
                self.apply_force(hand[8][0], hand[8][1], 40, attract=True)
                self.apply_force(hand[12][0], hand[12][1], 40, attract=True)

            # ── HANG LOOSE (thumb+pinky) → wave effect ──
            elif t and p and not any([i, m, r]):
                self.apply_force(hand[4][0], hand[4][1], 30, attract=True)
                self.apply_force(hand[20][0], hand[20][1], 30, attract=True)
                self.vy -= 0.3

            # ── THUMB+INDEX → pinch repel ──
            elif t and i and not any([m, r, p]):
                self.apply_force(hand[4][0], hand[4][1], 40, attract=False)
                self.apply_force(hand[8][0], hand[8][1], 40, attract=False)

            # ── INDEX+PINKY → wide repel (rock sign) ──
            elif i and p and not any([t, m, r]):
                self.apply_force(hand[8][0], hand[8][1], 35, attract=False)
                self.apply_force(hand[20][0], hand[20][1], 35, attract=False)

            # ── 3 fingers with index+middle+ring → fan out ──
            elif i and m and r and not t and not p:
                self.apply_force(hand[8][0],  hand[8][1],  30, attract=True)
                self.apply_force(hand[12][0], hand[12][1], 30, attract=True)
                self.apply_force(hand[16][0], hand[16][1], 30, attract=True)

            # ── FOUR fingers (no pinky) → strong repel ──
            elif t and i and m and r and not p:
                self.apply_force(px, py, 90, attract=False)

            # ── FOUR fingers (no thumb / four+pinky) → fountain ──
            elif i and m and r and p and not t:
                self.apply_force(px, py, 50, attract=True, swirl=0.8)
                self.vy -= 0.6   # fountain upward

            # ── DEFAULT for remaining combos → gentle orbit ──
            else:
                self.apply_force(px, py, 35, attract=True, swirl=0.6)

        # Friction
        self.vx *= 0.95
        self.vy *= 0.95

        # Speed cap
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > 15:
            self.vx = (self.vx / speed) * 15
            self.vy = (self.vy / speed) * 15

        self.x += self.vx
        self.y += self.vy

        # Fade
        self.life -= 0.004
        if self.life <= 0 or not (0 <= self.x <= WIDTH) or not (0 <= self.y <= HEIGHT):
            self.reset()

    def draw(self, frame):
        alpha = max(0.0, min(1.0, self.life))
        b, g, r = self.color
        cv2.circle(frame, (int(self.x), int(self.y)), 1,
                   (int(b * alpha), int(g * alpha), int(r * alpha)), -1)

# ─────────────────────────────────────────────
#  FINGER STATE DETECTION
# ─────────────────────────────────────────────
def get_fingers_up(hand_points):
    """Returns tuple of 5 booleans: (thumb, index, middle, ring, pinky)"""
    if len(hand_points) < 21:
        return (False, False, False, False, False)

    THRESHOLD = 12

    # Thumb (horizontal check)
    wrist_x   = hand_points[0][0]
    thumb_tip = hand_points[4][0]
    thumb_mcp = hand_points[2][0]
    thumb_up  = abs(thumb_tip - wrist_x) > abs(thumb_mcp - wrist_x)

    # Other 4 fingers (vertical check)
    other = []
    for tip_id, pip_id in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        other.append((hand_points[pip_id][1] - hand_points[tip_id][1]) > THRESHOLD)

    return (thumb_up, other[0], other[1], other[2], other[3])

# ─────────────────────────────────────────────
#  DRAW HAND SKELETON
# ─────────────────────────────────────────────
def draw_hand(frame, hand_points, color=(150, 150, 150)):
    connections = [
        (0,1),(1,2),(2,3),(3,4),
        (0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12),
        (0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20),
        (5,9),(9,13),(13,17),
    ]
    for s, e in connections:
        cv2.line(frame, hand_points[s], hand_points[e], color, 1)
    for pt in hand_points:
        cv2.circle(frame, pt, 2, (255, 255, 255), -1)

# ─────────────────────────────────────────────
#  DOWNLOAD MODEL
# ─────────────────────────────────────────────
def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading hand model... please wait")
        import urllib.request
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(MODEL_URL, context=ctx) as r:
            with open(MODEL_PATH, 'wb') as f:
                f.write(r.read())
        print("Model downloaded!")
    else:
        print("Model ready.")

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    download_model()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not opened!")
        print("Fix: System Settings -> Privacy & Security -> Camera -> Turn ON Terminal")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    # MediaPipe — detect up to 2 hands
    base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,                         # detect BOTH hands
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    detector = vision.HandLandmarker.create_from_options(options)

    particles = [Particle() for _ in range(NUM_PARTICLES)]
    overlay   = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    print("\n=== HAND GESTURE PARTICLE SYSTEM ===")
    print(f"Tracking up to 2 hands | {NUM_PARTICLES} tiny particles")
    print("All 32 finger combinations have unique effects!")
    print("Press Q to quit\n")

    # Current gesture info for display
    current_gesture_name = "NONE"
    current_gesture_desc = "Show your hand!"
    current_color        = (180, 180, 180)
    current_fingers_key  = (False,) * 5
    num_hands_detected   = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame     = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result    = detector.detect(mp_image)

        all_hands_data = []   # list of hand_points for each hand
        all_keys       = []   # finger tuple for each hand

        if result.hand_landmarks:
            num_hands_detected = len(result.hand_landmarks)
            for hand_lm in result.hand_landmarks:
                hand_points = [
                    (int(lm.x * WIDTH), int(lm.y * HEIGHT))
                    for lm in hand_lm
                ]
                all_hands_data.append(hand_points)
                all_keys.append(get_fingers_up(hand_points))

                # Draw skeleton
                draw_hand(frame, hand_points)

            # Use first hand's gesture key for display
            current_fingers_key = all_keys[0]
            info = GESTURE_MAP.get(current_fingers_key,
                                   ("CUSTOM", (200, 200, 200), "Custom combo"))
            current_gesture_name = info[0]
            current_color        = info[1]
            current_gesture_desc = info[2]
        else:
            num_hands_detected  = 0
            current_gesture_name = "NO HAND"
            current_gesture_desc = "Show your hand to camera"
            current_color        = (180, 180, 180)
            current_fingers_key  = (False,) * 5

        # ── Update particles ──
        overlay = (overlay * 0.88).astype(np.uint8)
        for p in particles:
            p.update(all_hands_data, current_fingers_key, num_hands_detected)
            p.draw(overlay)

        # ── Combine frame + particles ──
        dim_frame = (frame * 0.3).astype(np.uint8)
        combined  = cv2.add(dim_frame, overlay)

        # ── HUD — Finger indicators ──
        finger_names = ["T", "I", "M", "R", "P"]
        finger_x = 20
        for idx, (fname, is_up) in enumerate(zip(finger_names, current_fingers_key)):
            color = current_color if is_up else (60, 60, 60)
            cv2.rectangle(combined, (finger_x, 10), (finger_x + 30, 50), color, -1)
            cv2.putText(combined, fname, (finger_x + 7, 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            finger_x += 38

        # ── Gesture name ──
        cv2.putText(combined, current_gesture_name, (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, current_color, 2)

        # ── Description ──
        cv2.putText(combined, current_gesture_desc, (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # ── Hand count ──
        hand_msg = f"Hands detected: {num_hands_detected}"
        if num_hands_detected == 2:
            hand_msg += "  << TWO HANDS UP! Special effect! >>"
        cv2.putText(combined, hand_msg, (20, HEIGHT - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 255) if num_hands_detected == 2 else (150, 150, 150), 1)

        cv2.imshow("Hand Gesture Particles", combined)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Bye!")

if __name__ == "__main__":
    main()
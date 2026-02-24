import cv2
import numpy as np
import random
import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# -------------------------
# Config
# -------------------------
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# -------------------------
# Helper Classes
# -------------------------
class Player:
    def __init__(self, x, y, radius=20):
        self.x = x
        self.y = y
        self.radius = radius

    def update_from_hand(self, x, y):
        self.x = x
        self.y = y

    def draw(self, frame):
        cv2.circle(frame, (int(self.x), int(self.y)), self.radius, (255, 0, 0), -1)


class FallingObject:
    def __init__(self):
        self.radius = 15
        self.respawn()

    def respawn(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-300, -50)
        self.speed = random.randint(2, 4)  # not greater than 4

    def update(self):
        self.y += self.speed

    def draw(self, frame):
        cv2.circle(frame, (int(self.x), int(self.y)), self.radius, (0, 255, 255), -1)


class HandTracker:
    """Uses MediaPipe Tasks Hand Landmarker to get index finger tip (landmark 8) and full landmarks."""
    def __init__(self, model_path):
        BaseOptions = python.BaseOptions
        HandLandmarker = vision.HandLandmarker
        HandLandmarkerOptions = vision.HandLandmarkerOptions
        VisionRunningMode = vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=1
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.frame_id = 0

    def get_hand(self, frame_bgr):
        # Convert to RGB
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = self.landmarker.detect_for_video(mp_image, self.frame_id)
        self.frame_id += 1

        if result.hand_landmarks:
            hand = result.hand_landmarks[0]
            h, w, _ = frame_bgr.shape
            tip = hand[8]  # index finger tip
            cx = int(tip.x * w)
            cy = int(tip.y * h)
            return (cx, cy), hand

        return None, None


class GestureDetector:
    """
    Classifies simple gestures from 21 hand landmarks:
    FIST, OPEN, TWO_FINGERS, UNKNOWN
    Landmark indices (MediaPipe):
      0 = wrist
      4 = thumb tip
      8 = index tip
      12 = middle tip
      16 = ring tip
      20 = pinky tip
      5, 9, 13, 17 = finger base joints (MCP)
    """
    def classify(self, hand_landmarks):
        # tip.y < base.y means finger is extended (higher on screen)
        def is_extended(tip_i, base_i):
            return hand_landmarks[tip_i].y < hand_landmarks[base_i].y

        thumb_ext = is_extended(4, 2)   # approximate base for thumb
        index_ext = is_extended(8, 5)
        middle_ext = is_extended(12, 9)
        ring_ext = is_extended(16, 13)
        pinky_ext = is_extended(20, 17)

        extended_count = sum([thumb_ext, index_ext, middle_ext, ring_ext, pinky_ext])

        # FIST: none or only one extended
        if extended_count <= 1:
            return "FIST"

        # TWO FINGERS: index + middle extended, ring & pinky folded
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            return "TWO_FINGERS"

        # OPEN: most fingers extended
        if extended_count >= 4:
            return "OPEN"

        return "UNKNOWN"


class Game:
    def __init__(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, radius=20)
        self.objects = [FallingObject() for _ in range(random.choice([2, 3]))]
        self.score = 0
        self.lives = 3
        self.game_over = False

    def check_collision(self, obj):
        dx = self.player.x - obj.x
        dy = self.player.y - obj.y
        dist = math.sqrt(dx*dx + dy*dy)
        return dist < self.player.radius + obj.radius

    def update(self):
        if self.game_over:
            return

        for obj in self.objects:
            obj.update()

            if self.check_collision(obj):
                self.score += 1
                obj.respawn()

            elif obj.y > SCREEN_HEIGHT:
                self.lives -= 1
                obj.respawn()

        if self.lives <= 0:
            self.game_over = True

    def draw(self, frame, gesture_label):
        # Draw objects
        for obj in self.objects:
            obj.draw(frame)

        # Draw player
        self.player.draw(frame)

        # UI
        cv2.putText(frame, f"Score: {self.score}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Lives: {self.lives}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"Gesture: {gesture_label}", (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        if self.game_over:
            cv2.putText(frame, "GAME OVER", (180, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)


# -------------------------
# Main
# -------------------------
def main():
    # Camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)

    # Hand tracker (model must be in same folder)
    model_path = "hand_landmarker.task"
    hand_tracker = HandTracker(model_path)
    gesture_detector = GestureDetector()

    game = Game()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
        frame = cv2.flip(frame, 1)  # mirror view

        # Get hand position + landmarks
        pos, hand_landmarks = hand_tracker.get_hand(frame)

        current_gesture = "UNKNOWN"

        if pos is not None and hand_landmarks is not None:
            x, y = pos
            game.player.update_from_hand(x, y)
            # small green dot to show fingertip
            cv2.circle(frame, (x, y), 6, (0, 255, 0), -1)

            current_gesture = gesture_detector.classify(hand_landmarks)

        # Gesture effects
        if current_gesture == "FIST":
            # Pause: do not update game
            pass
        elif current_gesture == "TWO_FINGERS":
            # Slow motion: reduce speeds
            for obj in game.objects:
                obj.speed = max(1, obj.speed - 1)
            game.update()
        else:
            # OPEN or UNKNOWN: normal speeds (clamp back to 2..4)
            for obj in game.objects:
                obj.speed = min(max(obj.speed, 2), 4)
            game.update()

        # Draw everything
        game.draw(frame, current_gesture)

        cv2.imshow("Gesture Catch Game (OOP + Gestures)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
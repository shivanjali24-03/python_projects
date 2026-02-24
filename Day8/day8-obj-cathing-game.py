import cv2
import numpy as np
import random
import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Screen size
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# Player (hand-controlled)
player = {
    "x": SCREEN_WIDTH // 2,
    "y": SCREEN_HEIGHT // 2,
    "radius": 20
}

# Game state
score = 0
lives = 3
game_over = False

# Spawn one falling object
def spawn_object():
    return {
        "x": random.randint(0, SCREEN_WIDTH),
        "y": random.randint(-300, -50),
        "speed": random.randint(2, 4),  # not greater than 4
        "radius": 15
    }

# Collision check
def check_collision(player, obj):
    dx = player["x"] - obj["x"]
    dy = player["y"] - obj["y"]
    distance = math.sqrt(dx*dx + dy*dy)
    return distance < player["radius"] + obj["radius"]

# Decide how many objects: 2 or 3
spawn_count = random.choice([2, 3])
objects = [spawn_object() for _ in range(spawn_count)]

# -------------------------------
# MediaPipe Tasks: Hand Landmarker
# -------------------------------

model_path = "hand_landmarker.task"

BaseOptions = python.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

landmarker = HandLandmarker.create_from_options(options)

# Camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)

frame_id = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
    frame = cv2.flip(frame, 1)  # mirror for natural feel

    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Detect hands
    result = landmarker.detect_for_video(mp_image, frame_id)
    frame_id += 1

    # If hand detected, use index finger tip (landmark 8)
    if result.hand_landmarks:
        hand_landmarks = result.hand_landmarks[0]  # first hand

        h, w, _ = frame.shape
        index_tip = hand_landmarks[8]  # index finger tip

        cx = int(index_tip.x * w)
        cy = int(index_tip.y * h)

        player["x"] = cx
        player["y"] = cy

        # Draw a small circle where finger is (debug)
        cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)

    if not game_over:
        # Update objects
        for obj in objects:
            obj["y"] += obj["speed"]

            # Check collision (caught)
            if check_collision(player, obj):
                score += 1
                new_obj = spawn_object()
                obj.update(new_obj)

            # Check missed
            elif obj["y"] > SCREEN_HEIGHT:
                lives -= 1
                new_obj = spawn_object()
                obj.update(new_obj)

        if lives <= 0:
            game_over = True

    # Draw falling objects
    for obj in objects:
        cv2.circle(frame, (int(obj["x"]), int(obj["y"])), obj["radius"], (0, 255, 255), -1)

    # Draw player (hand point)
    cv2.circle(frame, (int(player["x"]), int(player["y"])), player["radius"], (255, 0, 0), -1)

    # Draw score & lives
    cv2.putText(frame, f"Score: {score}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Lives: {lives}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if game_over:
        cv2.putText(frame, "GAME OVER", (200, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    cv2.imshow("Gesture Game - Hand Control (MediaPipe Tasks)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
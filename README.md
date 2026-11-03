<div align="center">

# 🐍 Python Projects: Day by Day

**A daily Python practice log, from basic logic to real-time hand-tracking games.**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0097A7?style=for-the-badge&logo=google&logoColor=white)

</div>

## ⭐ Highlights

### ✋ Hand-gesture catching game (`Day8/`)
Play a game **with your hand in front of the webcam**. MediaPipe tracks your hand in real time, your hand controls the player, and you catch falling objects to score points. You get 3 lives.

### ✨ Hand-gesture particle system (`Day7/`)
It detects **all 32 finger combinations** across both hands and draws particle effects that react to your gestures.

## 📅 Progress log

| Day | Topic | What I built |
|---|---|---|
| 1 | Basics | Arithmetic, number swapping, positive/negative check |
| 2 | Strings | Reverse, palindrome, vowel count, character frequency, first non-repeating character |
| 3 | Lists | Remove duplicates, second-largest element, move zeros to the end |
| 4 | Logic | Grade calculator, number classifier, menu-based billing system |
| 5 | Data | Contact book |
| 6 | Mini app | Daily expense tracker |
| 7 | Computer vision | Hand-gesture particle system (OpenCV + MediaPipe) |
| 8 | Computer vision | Hand-controlled catching game (OpenCV + MediaPipe) |

## Run it

```bash
# Basic scripts
python Day4/day4-billing-system.py

# Webcam projects (Day 7 and 8)
pip install opencv-python mediapipe numpy
cd Day8
python day8-obj-cathing-game.py
```

The webcam projects need a camera, and the `hand_landmarker.task` model file in the same folder (it's already included).

---

Built by [@shivanjali24-03](https://github.com/shivanjali24-03)

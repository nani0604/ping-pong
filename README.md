# ping-pong

# 🎮 Ultimate Pong - AI vs Player

A modern twist on the classic Pong game using Python and Pygame. This version features:

- 🔥 AI opponent with adjustable difficulty  
- 🎯 Power-ups like speed boost, paddle resizing, and multiball  
- 🔊 Sound effects for immersive gameplay  
- 🏆 High score tracking  
- 💡 Clean object-oriented code

---

## 🛠️ Features

- Left paddle controlled by **AI**  
- Right paddle controlled by **Player** (Arrow keys)
- Power-ups appear randomly with effects:
  - 🟩 Expand paddle
  - 🟥 Shrink paddle
  - 🟨 Speed boost
  - 🔵 Multiball
- High score saved locally in `highscore.json`
- Game over after a player reaches 10 points

---

## 🎮 Controls

| Key         | Action                     |
|-------------|----------------------------|
| `↑` / `↓`   | Move right paddle up/down  |
| `SPACE`     | Start game                 |
| `P`         | Pause / Resume             |
| `R`         | Restart game               |
| `ESC`       | Quit                       |

---

## 📦 Requirements

- Python 3.x
- [pygame](https://www.pygame.org/)

Install pygame using pip:

```bash
pip install pygame
▶️ How to Run
bash
Copy
Edit
python ultimate_pong.py


project/
├── sounds/
│   ├── hit.wav
│   ├── score.wav
│   ├── powerup.wav
│   └── wall.wav
├── highscore.json   (auto-created after playing)
└── ultimate_pong.py
![image](https://github.com/user-attachments/assets/fe5bed34-2077-43c5-82ef-399ee486fd45)

![image](https://github.com/user-attachments/assets/cadf3e08-d6ce-4086-a2ae-b1967812712a)



🚀 Future Improvements (Ideas)
Multiple AI difficulty levels switchable in-game

Custom player names and themes

Multiplayer over network

Mobile-friendly version using Kivy

# Creepy-Tomatoe

GPT assisted coding journey

## Simple Pygame Demo

`game.py` contains a simple Pygame demo. Use the arrow keys to move the blue circle.
Avoid the red squares and collect the yellow coins. Both enemies and coins can
enter from any edge of the screen and travel horizontally or vertically. The
player starts in the center and earns a point for each coin collected. If a red
square collides with the player an end screen appears allowing you to restart
with `R` or quit with `Q`. Your score is recorded locally and the top five
results are displayed on the game over screen.

```
python3 game.py
```

Install dependencies with:

```bash
pip install -r requirements.txt
```

Pygame is required to run the demo.

Scores are saved in `scores.txt` in the project directory.

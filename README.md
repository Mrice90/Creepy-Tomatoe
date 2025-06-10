# Creepy-Tomatoe

GPT assisted coding journey

## Simple Pygame Demo

`game.py` contains a simple Pygame demo. Use `W`, `A`, `S` and `D` to move the ninja.
Shoot projectiles with the arrow keys (as long as ammo is available). Avoid the oni enemies and collect the coins.
Both enemies and coins can enter from any edge of the screen and travel horizontally or vertically. The
player starts in the center and earns a point for each coin collected. Projectiles
also award points when they destroy enemies or coins. Ammo pickups occasionally spawn and increase
your projectile count when collected. If an enemy
collides with the player an end screen appears allowing you to restart
with `R` or quit with `Q`.

### Assets

Binary image and audio files aren't stored in this repository. When the game
first runs it generates simple CC0 placeholder graphics and sound effects inside
the `assets/` directory. You can drop in higher quality CC0 replacements.
Place any `*.wav` files beginning with `hit`, `coin` or `swish` in
`assets/sounds/` and the game will randomly choose between them. The
background track `komiku-it.wav` will loop automatically.

Suggested sources:

- <https://www.kenney.nl/assets> for sprites
- <https://opengameart.org> for additional images
- <https://freesound.org> for sound effects

```
python3 game.py
```

Pygame is required to run the demo.

### Credits

- **Zombie RPG sprites** by Curt (March 20, 2013) from [OpenGameArt](https://opengameart.org)
- **Block Ninja 2D sprites** by Korba™ (May 28, 2014) from [OpenGameArt](https://opengameart.org)


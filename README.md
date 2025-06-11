# Creepy-Tomatoe

GPT assisted coding journey

## Overview

`game.py` implements a small arcade game in Pygame. Move the ninja with **W**, **A**, **S** and **D** and throw shuriken using the **arrow keys**. Zombies and coins spawn from the edges of the play area and cross the screen. Collecting a coin grants a point while eliminating a zombie awards a point and may spawn an ammo pickup. Coins hit by a shuriken are worth five points. Every ten points earned grants an extra life.

Each level lasts 60 seconds. When the timer expires the next level begins with faster enemies and adjusted spawn rates. If a zombie touches the player all lives are lost and an end screen appears that lets you restart with **R** or quit with **Q**.

Animated Blue Flame Flowers randomly decorate the map at the start of every level. The left side panel contains an **About** button which opens the developer's web page in a browser. The right panel houses the **Shop** where different grass backgrounds can be purchased for 10 points each. Press **Esc** during play to open the pause menu. From there you can adjust master, SFX and music volume sliders, switch the background music track and resume or exit the game.

## Assets

All images and sound effects used by the game are included in the `assets/` folder. You can replace them with your own CC0 files. The game automatically loads any `*.wav`, `*.ogg` or `*.mp3` placed in `assets/sounds/`.

- files starting with `hit` play when zombies or the player are struck
- files starting with `coin` play when coins are collected
- files starting with `swish` play when throwing shuriken
- several background tracks are available and can be selected from the pause menu

Run the game with:

```
python3 game.py
```

Pygame is required to run the game.

### Credits

 - **Zombie RPG sprites** by Curt (March 20, 2013) from [OpenGameArt](https://opengameart.org)
 - **Block Ninja 2D sprites** by Korba™ (May 28, 2014) from [OpenGameArt](https://opengameart.org)
 - **Forest background** by Ansimuz from [OpenGameArt](https://opengameart.org)
 - **Coin animation** by Kenney from [OpenGameArt](https://opengameart.org)
 - **5 Hit Sounds** by Kenney from [OpenGameArt](https://opengameart.org)
 - **Coin sound effects** by Kenney from [OpenGameArt](https://opengameart.org)
 - **Swish sound effects** by Kenney from [OpenGameArt](https://opengameart.org)
 - **"It's Time for Adventure Vol 2 - Battle Theme"** by Komiku from [OpenGameArt](https://opengameart.org)
 - **8 Bit Battler** by Juhani Junkala from [OpenGameArt](https://opengameart.org)
 - **New Battle** by FoxSynergy from [OpenGameArt](https://opengameart.org)

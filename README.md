# Terminal Dash

A deterministic terminal-based rhythm platformer inspired by Geometry Dash.

## Features

- **Deterministic Physics**: Every jump follows the exact same arc
- **Progressive Difficulty**: Speed increases gradually over time
- **Instant Restart**: Press SPACE after death to try again
- **Stable Performance**: Fixed tick rate with no flickering
- **Clean Architecture**: Modular design with separation of concerns

## Requirements

- Python 3.6+
- Standard library only (uses `curses`)
- Terminal with at least 80x24 characters recommended

## How to Play

1. Run the game:
   ```bash
   python3 main.py
   ```

2. Controls:
   - **SPACE (tap)**: Short jump - for low obstacles
   - **SPACE (hold)**: Variable jump height - hold longer for higher jumps
   - **Release SPACE**: Cut jump short mid-air
   - **Q**: Quit game

3. Objective:
   - Avoid obstacles by jumping over them
   - Survive as long as possible for a high score
   - The game speeds up over time

## Architecture

```
main.py      - Entry point and curses initialization
game.py      - Core game loop and state management
player.py    - Player physics and jump mechanics
level.py     - Level scrolling and obstacle generation
renderer.py  - Display logic
```

## Game Mechanics

### Physics-Based Jumping
The game features **variable jump heights** based on how long you hold the space bar:
- **Tap jump** (quick press): Short hop - clears spikes and low obstacles (2 units high)
- **Medium jump** (brief hold ~0.2s): Mid-height jump - clears medium obstacles (4-5 units high)
- **Full jump** (full hold ~0.3s): Maximum height - clears tall obstacles (6-7 units high)

**Master the timing**: Each obstacle is designed for specific jump heights. Learn when to tap vs when to hold!

### Platform Layer
The game uses a dual-layer ground system:
- **Platform layer** (─): Where you run - don't fall through gaps!
- **Ground layer** (=): Visual foundation below the platform

### Background Elements
- **Stars** (·): Decorative stars in the sky with parallax scrolling
- **Clouds** (~≈~): Floating clouds that scroll slower than the foreground

### Obstacle Types
Obstacles are aligned with jump height requirements:
- **Spikes** (▲): Ground hazards - requires short tap jump
- **Low Blocks** (██): 2 units tall - requires short tap jump
- **Mid Blocks** (████): 3-4 units tall - requires medium jump (brief hold)
- **High Blocks** (██████): 5-6 units tall - requires full jump (full hold)
- **Floating Obstacles** (◆): Mid-air hazards at various heights
- **Gaps** (  ): Missing platform sections - must jump or fall!

### Level Design
- **Strategic Jumping**: Obstacles are placed to test your ability to vary jump heights
- **Progressive Difficulty**: Speed increases, testing your timing precision
- **Jump Mastery**: Learn to tap for quick obstacles, hold for tall ones

### Speed Progression
- Base speed: 20 ticks/second
- Increases by 0.1x every 200 ticks
- Maximum: 3.0x speed multiplier

### Collision
- Instant death on contact with obstacles
- Collision checked at player's fixed x-position

## Extending the Game

The modular architecture makes it easy to add:
- **Elevated obstacles**: Modify `level.py` obstacle generation
- **Double jump**: Add state to `player.py`
- **Power-ups**: Extend `Player` and `Level` classes
- **Custom levels**: Replace pattern with level data in `level.py`
- **Replay system**: Log inputs and tick counter in `game.py`

## Performance Notes

- Fixed tick rate prevents timing variations
- Non-blocking input ensures responsive controls
- Clean separation prevents state leakage between runs
- Error handling prevents crashes from terminal resize

## License

Public domain - use freely

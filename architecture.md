# Architecture — Terminal Geometry Dash

## Overview

A terminal-based side-scrolling platformer (Geometry Dash clone) built with Python's `curses` library. The player auto-runs rightward and must jump over obstacles with variable-height jumps controlled by holding SPACE. The game is fully deterministic — same inputs always produce the same result.

**Stack**: Python 3.6+ · stdlib only (`curses`, `time`, `random`)

---

## Module Map

```
main.py          Entry point, curses bootstrap
   │
   └─ game.py    Core loop, state machine, orchestrator
        │
        ├─ player.py     Player entity, physics, jump mechanics
        ├─ level.py      World grid, scrolling, obstacle generation
        └─ renderer.py   Display-only output layer
```

All dependencies flow **downward**. No module imports from a sibling or upward. `Game` is the sole orchestrator.

---

## Module Responsibilities

### `main.py` — Entry Point
| Concern          | Detail                                    |
|:-----------------|:------------------------------------------|
| Terminal setup   | `curses.wrapper`, hide cursor, nodelay    |
| Lifecycle        | Construct `Game`, call `run()`, clean exit |
| Lines            | 24                                        |

### `game.py` — Game Class (Orchestrator)
| Concern            | Detail                                              |
|:-------------------|:----------------------------------------------------|
| Game loop           | Fixed-rate tick loop with `time.sleep` pacing       |
| Input routing       | Reads `getch()`, maps keys to player/game actions   |
| State transitions   | `running` ↔ `game_over`, reset cycle               |
| Scoring             | `distance_score = tick_counter // 10`               |
| Speed progression   | Tick interval shrinks every 200 ticks (cap 3×)      |
| Collision detection | Delegates grid queries to `Level`                   |
| Render orchestration| Calls `Renderer` methods in correct draw order      |
| Lines               | 161                                                 |

### `player.py` — Player Class
| Concern          | Detail                                              |
|:-----------------|:----------------------------------------------------|
| Position         | Fixed x=5, floating-point y                        |
| Jump model       | SPACE press starts timer; release computes velocity |
| Variable height  | Velocity = -2.5 + (hold_ratio × -5.0), hold capped at 0.4s |
| Asymmetric gravity | Up: 0.35, Down: 1.0 — fast fall, floaty rise     |
| Max height       | Hard cap at row 3 — can never fly above            |
| Jump cooldown    | 120ms after landing before next jump allowed        |
| Visual states    | ● ground, ◎ charging, ◉ airborne                  |
| Lines            | ~105                                                |

### `level.py` — Level Class
| Concern             | Detail                                            |
|:--------------------|:--------------------------------------------------|
| Grid storage        | 2D array `[height][width]` of single characters   |
| Scrolling           | Shift all rows left by 1 each tick                |
| Obstacle generation | 22-element cycling pattern with spacing + type    |
| Gap handling        | Counter-based multi-column gaps                   |
| Background          | Stars + clouds with parallax (slower scroll)      |
| Collision queries   | `has_obstacle_at(x,y)` and `get_char_at(x,y)`    |
| Lines               | 233                                               |

### `renderer.py` — Renderer Class
| Concern          | Detail                                              |
|:-----------------|:----------------------------------------------------|
| Screen I/O       | All `stdscr.addstr()` calls live here only         |
| Draw order       | clear → HUD → background → foreground → player    |
| Error handling   | Silent try/except on all writes (resize-safe)      |
| Pure output      | **Never mutates game state** — read-only of models |
| Lines            | 80                                                  |

---

## Class Diagram

```
┌──────────────────────────────────────────────────┐
│                     Game                         │
│──────────────────────────────────────────────────│
│ stdscr, running, game_over, space_held           │
│ tick_interval, tick_counter, speed_multiplier     │
│ distance_score, best_score                       │
│ height, width                                    │
│──────────────────────────────────────────────────│
│ run()              # main loop                   │
│ handle_input()     # input dispatch              │
│ update()           # tick logic                  │
│ check_collision()  # collision queries           │
│ render()           # draw orchestration          │
│ reset()            # full state reset            │
├──────────────────────────────────────────────────┤
│ owns:                                            │
│  ├─ Player   player                              │
│  ├─ Level    level                               │
│  └─ Renderer renderer                            │
└──────────────────────────────────────────────────┘

┌─────────────────────────┐  ┌─────────────────────────────┐
│        Player           │  │           Level             │
│─────────────────────────│  │─────────────────────────────│
│ x=5, y (float)          │  │ grid[h][w]  (char[][])      │
│ velocity_y, on_ground   │  │ level_pattern[22]           │
│ jump_press_time         │  │ pattern_index, gap_counter  │
│ land_time, jump_cooldown│  │ star_positions, cloud_pos   │
│ gravity_up/down         │  │                             │
│─────────────────────────│  │─────────────────────────────│
│ press_jump()            │  │ scroll()                    │
│ release_jump()          │  │ _add_column()               │
│ update()                │  │ has_obstacle_at(x,y) → bool │
│ get_char() → str        │  │ get_char_at(x,y) → str     │
│ get_jump_height_cat()   │  │ get_background_elements()   │
│ reset(screen_height)    │  │ reset()                     │
└─────────────────────────┘  └─────────────────────────────┘

┌──────────────────────────┐
│        Renderer          │
│──────────────────────────│
│ stdscr, height, width    │
│──────────────────────────│
│ clear()                  │
│ refresh()                │
│ draw_hud(score,best,…)   │
│ draw_level(level)        │
│ draw_player(player)      │
└──────────────────────────┘
```

---

## Key Data Structures

### Level Grid
A 2D list of single-character strings: `grid[y][x] → str`

| Row                     | Content           |
|:------------------------|:------------------|
| `0`                     | HUD (not in grid) |
| `1` … `height-4`       | Open sky / obstacles |
| `height-3` (platform)  | `─` or obstacle chars |
| `height-2` (ground)    | `=` or gap spaces |
| `height-1`             | Bottom edge (unused) |

### Obstacle Characters
| Char | Meaning          | Kills on contact |
|:-----|:-----------------|:-----------------|
| `▲`  | Spike            | Yes              |
| `█`  | Block (various)  | Yes              |
| `◆`  | Floating hazard  | Yes              |
| `─`  | Platform         | No               |
| `=`  | Ground           | No               |
| ` `  | Empty / gap      | Falls through    |

### Level Pattern Array (22 elements, cyclic)
Each entry: `(spacing, element_type, height_req, *params)`

```python
# Example entries:
(15, 'spike',        'short')       # 15-col gap then a spike
(10, 'mid_obstacle', 'medium')      # floating ◆ at mid height
(16, 'gap',          'any', 3)      # 3-column gap in platform
(14, 'high_obstacle', 'full')       # floating ◆ at max height
```

---

## Design Patterns

### 1. Fixed Tick-Rate Game Loop
The loop measures elapsed time per tick and sleeps the remainder to maintain a constant frame rate. Speed increases are implemented by **shrinking the tick interval**, not by moving objects further per tick — the world always scrolls 1 column/tick.

### 2. Composition over Inheritance
`Game` owns `Player`, `Level`, and `Renderer` as plain instance attributes. No class hierarchies. Communication is via direct method calls.

### 3. Model–View Separation
`Renderer` is a pure output layer. It reads state from `Player` and `Level` but never writes to them. All state mutation happens via `Game.update()`.

### 4. Deterministic Level Generation
The obstacle pattern is a fixed 22-element array that cycles. Combined with deterministic parallax offsets (seeded `random`), every playthrough generates the same level layout, making the game a learnable skill challenge.

### 5. Asymmetric Gravity
Rising uses low gravity (0.35) for a floaty ascent; falling uses high gravity (1.0) for a snappy descent. This creates a "Geometry Dash feel" where the player hangs at the peak briefly.

### 5b. Jump Cooldown
A 120ms cooldown after landing prevents accidental double-jumps and ensures clean separation between consecutive jumps.

### 6. Silent Error Handling
All `curses.addstr()` calls are wrapped in bare `try/except` blocks. This prevents crashes when the terminal is resized mid-game or when characters are written outside bounds.

---

## State Machine

```
         ┌─────────────────────────┐
         │                         │
         ▼                         │
  ┌─────────────┐          ┌──────────────┐
  │  PLAYING    │──death──▶│  GAME OVER   │
  │             │          │              │
  │ game_over=F │          │ game_over=T  │
  │ running=T   │          │ running=T    │
  └─────────────┘          └──────────────┘
         ▲                         │
         │         SPACE           │
         └─────────────────────────┘
                  reset()

  Press Q from any state → running=False → exit loop
```

---

## Extension Points

| Feature         | Where to modify                              |
|:----------------|:---------------------------------------------|
| New obstacle    | `Level._add_column()` + add char to `has_obstacle_at` |
| Double jump     | `Player.start_jump()` — add air-jump state   |
| Power-ups       | New items in `Level`, pickup logic in `Game`  |
| Custom levels   | Replace `level_pattern` array                |
| Sound           | Hook into `Game.update()` events             |
| Replay system   | Log `(tick, key)` pairs in `Game.handle_input()` |
| Color           | Use `curses.init_pair()` in `Renderer`       |

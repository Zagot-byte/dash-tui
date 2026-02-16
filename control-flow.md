# Control Flow — Terminal Geometry Dash

## 1. Entry Point (`main.py`)

```
__main__ → curses.wrapper(main)
  └─ main(stdscr)
       ├─ curses.curs_set(0)    # hide cursor
       ├─ stdscr.nodelay(1)     # non-blocking input
       ├─ stdscr.timeout(0)     # no input delay
       ├─ Game(stdscr)          # construct all subsystems
       └─ game.run()            # enter main loop
```

`curses.wrapper` initialises the terminal, calls `main(stdscr)`, and restores the terminal on exit. Ctrl-C is caught and swallowed for a clean exit.

---

## 2. Main Game Loop (`Game.run`)

```
while self.running:
  ┌─ tick_start = time.time()
  │
  ├─ handle_input()       # read keyboard, update player/game state flags
  ├─ update()             # physics, scrolling, collision, scoring, speed
  ├─ render()             # clear → draw HUD → draw level → draw player → refresh
  │
  └─ sleep(tick_interval - elapsed)   # maintain constant tick rate
```

The loop runs at ~30 ticks/sec (base), accelerating up to 90 ticks/sec (3× multiplier). All timing is wall-clock based.

---

## 3. Input Handling (`Game.handle_input`)

```
getch() → key
  │
  ├─ SPACE pressed
  │    ├─ game_over?  → reset()         # restart on death screen
  │    └─ first press → space_held=True, player.press_jump()
  │                     (starts hold timer in Player)
  │
  ├─ no key (-1)
  │    └─ space_held was True → space_held=False, player.release_jump()
  │                              (computes hold duration, launches jump)
  │
  └─ 'q'/'Q' → running = False   # exit loop
```

Key insight: `getch()` returns -1 every tick where nothing is pressed. SPACE press starts a real-time timer; release computes hold duration and launches with proportional velocity.

---

## 4. Update Tick (`Game.update`)

```
if game_over: return

player.update()              # apply gravity, velocity, ground clamp
level.scroll()               # shift grid left, generate new column

check_collision()?
  ├─ True  → game_over = True, update best_score
  └─ False → tick_counter++
             distance_score = tick_counter // 15
             every 200 ticks: speed_multiplier += 0.1 (cap 3.0)
                              tick_interval = base / speed_multiplier
```

### 4a. Collision Detection (`Game.check_collision`)

```
player_x = 5 (fixed)
player_y = int(player.y)

1. level.has_obstacle_at(x, y)?        # hit a █, ▲, or ◆
     → True = dead

2. player_y >= platform_row?           # player at ground level
     level.get_char_at(x, platform_row) == ' '?   # no platform = gap
       → True = dead
```

---

## 5. Player Physics (`Player.update`)

```
if NOT on_ground:
  │
  ├─ holding_space AND hold_ticks < max(12)?
  │    hold_ticks++
  │    velocity_y = rise_speed(-1.8) + (rise_accel(-0.15) × hold_ticks)
  │    (rises faster the longer you hold)
  │
  ├─ ELSE (released or max reached):
  │    holding_space = False
  │    velocity_y += gravity(1.2)   # heavy fall
  │
  ├─ y += velocity_y
  │
  ├─ y < max_height(3)?  → clamp: y=3, velocity=0 (hard ceiling)
  └─ y ≥ ground_y?       → land: y=ground_y, velocity=0, on_ground=True
                            record land_time for cooldown
```

### 5a. Jump Flow

```
press_jump():
  if on_ground AND cooldown elapsed (100ms since last landing):
    holding_space = True, hold_ticks = 0
    velocity_y = rise_speed(-1.8)   # start rising immediately
    on_ground = False

release_jump():
  holding_space = False   # gravity takes over
```

Jump height categories:
| Hold Ticks | Category | Clears                   |
|:-----------|:---------|:-------------------------|
| ≤ 4        | short    | spikes, low blocks       |
| 5–8        | medium   | mid blocks, mid floaters |
| 9–12       | full     | high blocks, high floaters |

---

## 6. Level Scrolling (`Level.scroll`)

```
for each row:
  grid[y] = grid[y][1:] + [' ']      # shift left by 1 column

parallax background:
  every 3rd tick: shift star x-positions left (wrap around)
  every 2nd tick: shift cloud x-positions left (wrap around)

_add_column()                         # append new rightmost column
```

### 6a. Column Generation (`Level._add_column`) — RANDOMIZED

```
if gap_counter > 0:
  write ' ' to ground + platform rows, gap_counter--
  return

if double_spike_remaining > 0:
  double_spike_remaining--
  if == 0: place ▲
  return

write '=' (ground) and '─' (platform) at rightmost column

columns_until_next--

if columns_until_next ≤ 0:
  pick random obstacle from weighted pool:
    spike(30%) | low_block(20%) | gap(15%) | mid_block(12%)
    double_spike(10%) | mid_obstacle(10%) | high_block(8%)
    high_obstacle(5%)
  place obstacle via _place_obstacle()
  columns_until_next = random(8..18)
```

Each run generates a **unique random level** — obstacles and spacing are non-deterministic. Background stars/clouds remain deterministic (seeded RNG).

---

## 7. Rendering (`Game.render` → `Renderer`)

```
renderer.clear()         # stdscr.clear()

renderer.draw_hud(score, best, speed, game_over)
  └─ row 0: "Score: X  Best: Y  Speed: Z.Zx"
     if game_over: centered "GAME OVER - Press SPACE…" at mid-screen

renderer.draw_level(level)
  ├─ draw stars (·) from bg_elements
  ├─ draw clouds (~≈~) from bg_elements
  └─ draw foreground (rows 1..height):
       for each cell: if not space/bg → addstr(y, x, char)

renderer.draw_player(player)
  └─ addstr(int(y), x=5, player.get_char())
       ● grounded  │  ◎ charging  │  ◉ airborne

renderer.refresh()       # stdscr.refresh()
```

All rendering is wrapped in try/except to silently handle terminal resize or out-of-bounds writes.

---

## 8. Reset Flow (`Game.reset`)

```
Game.reset():
  game_over = False
  tick_counter = 0, distance_score = 0
  speed_multiplier = 1.0, tick_interval = base
  space_held = False

  player.reset(height)    # y = ground_y, velocity = 0, charge = 0
  level.reset()           # rebuild empty grid, re-init bg, fill screen
```

Triggered by pressing SPACE while `game_over == True`. The entire game state is rebuilt from scratch — no leftover state.

---

## 9. Complete Tick Sequence Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      ONE GAME TICK                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  handle_input()                                              │
│    └─ read key → update space_held flag                      │
│       └─ call player.start_jump() or player.release_jump()   │
│                                                              │
│  update()                                                    │
│    ├─ player.update()     ← apply gravity + velocity         │
│    ├─ level.scroll()      ← shift grid + add new column      │
│    ├─ check_collision()   ← obstacle hit or gap fall?        │
│    └─ score & speed       ← increment counters               │
│                                                              │
│  render()                                                    │
│    ├─ clear screen                                           │
│    ├─ draw HUD                                               │
│    ├─ draw level (bg → fg)                                   │
│    ├─ draw player                                            │
│    └─ refresh                                                │
│                                                              │
│  sleep(remaining time)   ← maintain tick rate                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

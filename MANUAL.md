# Unicorn HAT Mini — Game Manual (EN)

Collection of mini-games on a 17×7 LED matrix, four buttons (A, B, X, Y).

## Global controls

| Action | Buttons |
|---|---|
| Menu: up | X (short) |
| Menu: down | Y (short) |
| Menu: enter | A (short) |
| Menu: back | B (short) |
| Exit current game | Long-press A + B + X + Y (> 1.1 s) |

A "long press" anywhere means hold > 1.1 s. A "combo" means press multiple buttons together (released within ~0.17 s).

---

## Labyrinth (Maze)

Navigate a player dot from the left entrance to the right exit through a generated maze. View scrolls with the player.

**Levels**: 1 – 15. Maze size grows as `(10·N + 1) × (10·N + 1)` cells, padded for scrolling. Higher level = bigger maze.

**Controls**
| Action | Button |
|---|---|
| Move left | A |
| Move right | B |
| Move up | X |
| Move down | Y |
| Auto-solve (gives up) | A + B + X long press |

**Goal**: reach the exit. Auto-solve animates a BFS path then ends the game.

---

## Reaktion (Reaction)

Seven levels of reaction-time challenges. Each level: clear 15 successful rounds; 3 lives; reaction time per round shown after each hit.

### Lvl-1 — Basic reaction
Single corner blinks red. Press the matching button.
- Valid window: 0.5 s after blink. Slower = lose life.
- No display timeout — game waits for press.

### Lvl-2 — Color filter
Single corner blinks **red or blue**.
- Press the button **only on red**. On blue: do nothing (1 s display timeout passes the round).
- Pressing on blue or wrong button = lose life.

### Lvl-3 — Combo press
Two corners blink red simultaneously (e.g. A + X).
- Press both buttons together. Valid window 0.7 s.
- Wrong combo or single press = lose life.

### Lvl-4 — Decoy (single)
3 of 4 corners blink in random colors {red, green, blue}; **exactly one is red**.
- Press the corner showing red. Display timeout 1.2 s.
- Wrong corner / timeout = lose life. Reaction limit 0.5 s.

### Lvl-5 — Decoy (multi)
All 4 corners blink. **1 or 2 are red**, the rest green/blue.
- Press the combination of red corners (e.g. red on A and X → press A + X).
- Display timeout 1.5 s, reaction limit 0.8 s.

### Lvl-6 — Simon (fixed sequences)
A sequence of N buttons blinks in red, then "R" (Ready), pause, "G" (Go). Repeat the sequence.
- Round 1 = length 1 → round 15 = length 15.
- Per-button input window 0.75 s.
- On failure (wrong button or timeout): lose 1 life, replay the **same length** with a different sequence (3 deterministic sequences per length).
- Sequences are predetermined (always the same on every play).

### Lvl-7 — Simon (random sequences)
Same flow as Lvl-6 but sequences are freshly randomized every play.

---

## Space (Space Shooter)

Side-scrolling shooter. Ship on the left, meteors fly in from the right. Shoot meteors before they hit you.

**Controls**
| Action | Button |
|---|---|
| Move ship up | X |
| Move ship down | Y |
| Shoot | A |

**Lives**: 3. After being hit, ship blinks (invincibility ~1 s).

### Lvl-1
- Spawn interval: 15 ticks (slow). Meteor speed: slow. Max 1 meteor per spawn.
- Win: 30 hits.
- Difficulty ramps at scores 8 / 15 / 25.

### Lvl-2
- Spawn interval: 10 ticks. Meteor speed: faster. Up to 3 meteors per spawn.
- Win: 50 hits.
- Difficulty ramps at scores 8 / 15 / 25 / 40.

---

## Pong

Classic paddle game vs AI. Player paddle on the left (green), AI paddle on the right (blue), cyan ball bounces between them.

**Controls**
| Action | Button |
|---|---|
| Paddle up | X |
| Paddle down | Y |

Ball spin: hitting the paddle off-center adds vertical velocity. Match the ball with the paddle center to neutralize.

### Lvl-1
- Ball horizontal speed: 0.5 cells/tick. AI step interval: every 4 ticks (slow).
- Win: 5 points.

### Lvl-2
- Ball horizontal speed: 0.7 cells/tick. AI step interval: every 2 ticks (fast).
- Win: 7 points.

**Lose**: AI reaches the win-score first (no `winning()` animation, just exit prompt).

---

## Flappy

One-button reflex game. Yellow bird at column 4 falls under gravity; tap **A** to flap upward. Green pipes scroll right-to-left with a vertical gap. Pass through to score; touching a pipe, ceiling or floor ends the run.

**Controls**
| Action | Button |
|---|---|
| Flap | A (short) |

After a death, the score is shown briefly then the exit prompt. Endurance — no win condition.

### Lvl-1
- Gap size: 3 rows. Pipe scroll: 0.4 cells/tick. Spawn every 20 ticks (~1 s).

### Lvl-2
- Gap size: 2 rows. Pipe scroll: 0.6 cells/tick. Spawn every 15 ticks.

---

## Duell (Mash Duel) — 2 players

Button-mashing tug-of-war for two players. **Red player** owns A and B. **Blue player** owns X and Y. Long-press is filtered (so the global ABXY exit chord doesn't count).

After a 3/2/1 countdown, the field appears. The match ends as soon as the win condition triggers; the winner's color flashes the screen and a banner ("R" / "B") appears before the exit prompt.

> **Note**: button releases are batched ~0.17 s by the input pipeline, capping the effective mash event rate. Each event still counts every individual button character within the combination, so simultaneous mashing on multiple buttons is rewarded.

### Lvl-1 — Single bar (AB vs XY)

One full-screen bar. Cells left of the boundary are red, cells right are blue, the boundary itself is yellow.

- Each detected combo: A and B characters → red presses; X and Y → blue presses.
- `pressure ∈ [-1, +1]`, starts at 0. Each red press: `+1/30`. Each blue press: `-1/30`.
- Boundary column = `8 + round(pressure * 8)`.
- Win: pressure reaches +1 (boundary at right edge → red wins) or −1 (boundary at left edge → blue wins).

### Lvl-2 — Four independent bars

Four horizontal bars stacked, one per button. Each bar fills left→right based on its own button's press count.

| Row | Bar | Color |
|---|---|---|
| 0 | A | red |
| 1 | X | blue |
| 2, 3 | separator (dim white) | |
| 4 | B | red |
| 5 | Y | blue |
| 6 | separator (dim white) | |

- Pairings: A vs X (top), B vs Y (bottom). Bars move **independently**.
- Each bar fills `min(16, count * 17 / 25)` cells. First bar to reach the right edge wins its pairing — and that decides the overall match.
- Strategy: split focus between your two buttons or commit to one to outpace the opposite bar in that pair.

### Lvl-3 — Endurance (decay)

Same as Lvl-2 plus passive decay: each tick, every count decays by `0.04`. About 0.8 counts/sec — a maxed bar (25) drains in ~31 s if you stop. Forces sustained mashing.

---

## Game of Life

Conway's Game of Life on a 17×7 toroidal grid (edges wrap). Three sub-modes: **Edit**, **Preset Picker**, **Simulation**.

### Edit mode (default on entry)

Move the cursor (blue), toggle cells (green when alive), then start the simulation.

| Action | Button |
|---|---|
| Cursor left | A (short) |
| Cursor right | B (short) |
| Cursor up | X (short) |
| Cursor down | Y (short) |
| Toggle cell at cursor | A + X (combo) |
| Start simulation | B + Y (combo) |
| **Clear grid** | A (long) |
| **Randomize grid** | B (long) |
| **Open preset picker** | X (long) |

A short banner ("C" / "?" / "P" / "R") appears on each action / mode change.

### Preset picker mode

Browse and place predefined patterns at the cursor. Preset preview is **yellow** overlaid on the grid; cells that overlap living cells appear **orange**. Cursor stays put — pre-position it in Edit before entering.

| Action | Button |
|---|---|
| Previous preset | X (short) |
| Next preset | Y (short) |
| Cycle drop mode (OR / XOR / REPLACE) | X + Y (combo) |
| Confirm placement at cursor | A (short) |
| Cancel back to Edit | B (short) |

**Drop modes**:
- **OR** — preset cells turn ON; existing cells unchanged.
- **XOR** — preset cells toggle (kills overlapping live cells, lights empty ones).
- **REPLACE** — clear grid, then place preset.

Available presets: Glider, R-pentomino, Lightweight spaceship, Blinker, Block, Pulsar fragment.

### Simulation mode

Cells follow Conway's rules. Speed and pause adjustable in real time.

| Action | Button |
|---|---|
| Pause / resume | A (short) |
| Slower (longer step) | X (short) |
| Faster (shorter step) | Y (short) |
| Back to Edit (running) | B (short) |
| **Step once** (when paused) | B (short) |
| Back to Edit (always) | B (long) |
| Randomize while running | Y (long) |

Living cells: green (running) / orange (paused).

---

## Notes

- "Combo" means buttons pressed and released within ~0.17 s of each other.
- "Long press" threshold: 1.1 s.
- Universal exit (any game): hold A + B + X + Y for > 1.1 s.

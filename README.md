# Python Collaborative Game (Student Repo)

This is the clean student version with no solutions. Implement the game by completing TODOs under `game/`.

## Game overview
- Genre: turn-based, text UI
- Goal: survive enemy encounters across simple levels
- Turn flow:
  1) Render header and status
  2) Player chooses action: attack/defend/wait/quit
  3) Enemy AI chooses a move
  4) Engine updates tick and checks win/lose

## Modules to implement
- `game/engine.py`: game loop control and state (running, tick, player health)
- `game/entities.py`: `Player` and `Enemy` dataclasses, basic stats
- `game/ai.py`: `choose_enemy_move(tick) -> str` with simple logic
- `game/levels.py`: `load_levels()` returning at least two levels
- `game/ui.py`: header, input prompt, and status rendering

## Group responsibilities
- group01 — Engine & loop
- group02 — Entities & combat rules
- group03 — AI behavior & difficulty
- group04 — Levels & content loading
- group05 — UI/UX prompts and output polish

## Tasks and course
- Tasks: see `tasks/`
- Course: see `course/`

## Run (after implementing)
```
python main.py
```

## Getting started
1) Create a branch: `git checkout -b group0X/feature`
2) Implement TODOs in your module
3) Push and open a PR to `main`

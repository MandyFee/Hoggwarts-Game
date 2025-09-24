# Task: Engine & State

- Add fields to `GameState`: `score: int`, `stamina: int`, `status: str` (e.g., "ok", "stunned").
- Implement JSON save/load: `save_state(path)`, `load_state(path)` on `GameEngine`.
- Ensure `tick` increments per full player+enemy turn.
- Add `reset()` to reinitialize the game.

Acceptance:
- `python main.py` still runs.
- Save then load restores identical state.

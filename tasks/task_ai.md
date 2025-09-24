# Task: Enemy AI

- Replace baseline AI with a function that considers player HP, enemy HP, and tick.
- Difficulty modes: `easy`, `normal`, `hard` (e.g., aggressive on hard).
- Keep API: `choose_enemy_move(tick: int, difficulty: str = "normal") -> str`.

Acceptance:
- Different difficulty changes move distribution.
- No crashes on boundary conditions.

# Task: Entities & Combat

- Add `inventory: list[str]` to `Player` and `Enemy` (optional for enemy).
- Implement `compute_damage(attacker, defender, action) -> int` in new `game/combat.py`.
- Support crits (10% chance x2 damage) and defense reducing damage by 1.
- Prevent negative HP.

Acceptance:
- Attacking reduces HP according to formula.
- Defend reduces damage properly.

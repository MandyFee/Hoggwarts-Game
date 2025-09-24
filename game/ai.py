"""Simple enemy AI helpers."""
from typing import Literal

EnemyMove = Literal["attack", "defend", "wait"]

def choose_enemy_move(tick: int) -> EnemyMove:
    """Return the enemy's move for the current tick.

    The pattern keeps the behaviour predictable but not static:
    - every 5th turn the enemy defends to mitigate damage
    - otherwise every 3rd turn the enemy waits to regroup
    - all other turns the enemy attacks
    """
    if tick % 5 == 4:
        return "defend"
    if tick % 3 == 2:
        return "wait"
    return "attack"

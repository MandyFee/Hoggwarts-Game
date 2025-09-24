"""Enemy AI helpers with simple adaptive behaviour."""
from __future__ import annotations

import random
from dataclasses import dataclass, replace
from typing import Literal

EnemyMove = Literal["curse", "shield", "stalk"]
Difficulty = Literal["easy", "normal", "hard"]


@dataclass(frozen=True)
class _AIContext:
    player_hp: int = 0
    enemy_hp: int = 0


_context = _AIContext()


def set_ai_context(player_hp: int, enemy_hp: int) -> None:
    """Expose the latest health totals so choose_enemy_move can adapt."""
    global _context
    _context = replace(_context, player_hp=max(0, player_hp), enemy_hp=max(0, enemy_hp))


_DIFFICULTY_WEIGHTS = {
    "easy": {"curse": 0.45, "shield": 0.30, "stalk": 0.25},
    "normal": {"curse": 0.55, "shield": 0.25, "stalk": 0.20},
    "hard": {"curse": 0.70, "shield": 0.20, "stalk": 0.10},
}


def choose_enemy_move(tick: int, difficulty: Difficulty = "normal") -> EnemyMove:
    """Return the opponent's move for the current round.

    The AI takes into account remaining health on both sides, the current tick,
    and the requested difficulty. Hard mode favours aggressive curse usage,
    whereas easy mode gives the player more openings.
    """
    ctx = _context
    weights = dict(_DIFFICULTY_WEIGHTS.get(difficulty, _DIFFICULTY_WEIGHTS["normal"]))

    total_hp = max(1, ctx.player_hp + ctx.enemy_hp)
    enemy_ratio = ctx.enemy_hp / total_hp
    player_ratio = ctx.player_hp / total_hp

    if ctx.enemy_hp <= 5 or enemy_ratio < 0.25:
        weights["shield"] += 0.15
        weights["curse"] -= 0.05
        weights["stalk"] -= 0.10
    elif player_ratio < 0.35:
        weights["curse"] += 0.10
        weights["stalk"] += 0.05
        weights["shield"] -= 0.15

    if tick % 5 == 0:
        weights["stalk"] += 0.10
        weights["curse"] -= 0.05
        weights["shield"] -= 0.05
    elif tick % 3 == 0:
        weights["curse"] += 0.05
        weights["shield"] += 0.05
        weights["stalk"] -= 0.10

    # Clamp and normalise weights to avoid negative probabilities.
    curse = max(0.0, weights["curse"])
    shield = max(0.0, weights["shield"])
    stalk = max(0.0, weights["stalk"])
    total = curse + shield + stalk or 1.0
    curse /= total
    shield /= total
    stalk /= total

    roll = random.random()
    if roll < curse:
        return "curse"
    if roll < curse + shield:
        return "shield"
    return "stalk"

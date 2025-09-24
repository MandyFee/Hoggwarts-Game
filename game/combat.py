"""Combat helpers and formulas for the duel system."""
from __future__ import annotations

import random
from typing import Protocol

OFFENSIVE_ACTIONS = {"attack", "cast", "curse"}
DEFENSIVE_ACTIONS = {"defend", "protego", "shield"}
NEUTRAL_ACTIONS = {"focus", "wait", "stalk"}
CRIT_CHANCE = 0.10


class Combatant(Protocol):
    attack: int
    defense: int


def compute_damage(attacker: Combatant, defender: Combatant, action: str) -> int:
    """Calculate the amount of damage dealt for a given action.

    Offensive actions roll the attack stat, defensive actions negate damage,
    and neutral actions are supportive. A simple crit system grants a 10%
    chance of doubling the damage, and defenders shave one point off incoming
    hits when they are actively guarding.
    """
    lowered = action.lower().strip()
    if lowered in DEFENSIVE_ACTIONS or lowered in NEUTRAL_ACTIONS:
        return 0

    if lowered not in OFFENSIVE_ACTIONS:
        return 0

    damage = max(0, attacker.attack)
    if random.random() < CRIT_CHANCE:
        damage *= 2

    # Baseline mitigation based on defender's training
    mitigated = max(0, damage - 1)
    # Defender's defense stat reflects dueling experience, shave more damage
    mitigated = max(0, mitigated - max(0, defender.defense - 1))
    return mitigated

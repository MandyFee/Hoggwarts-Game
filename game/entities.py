"""Entity definitions for Hogwarts duelists."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Player:
    """Student duelist statistics used during combat."""

    name: str
    hp: int
    attack: int = 6
    defense: int = 3
    inventory: List[str] = field(default_factory=lambda: ["Chocolate Frog", "Wand Polish", "Pepperup Potion"])
    max_hp: int = field(init=False)

    def __post_init__(self) -> None:
        self.max_hp = self.hp


@dataclass
class Enemy:
    """Opponent statistics for Hogwarts training bouts."""

    kind: str
    hp: int
    attack: int = 4
    defense: int = 2
    inventory: List[str] = field(default_factory=list)
    max_hp: int = field(init=False)

    def __post_init__(self) -> None:
        self.max_hp = self.hp

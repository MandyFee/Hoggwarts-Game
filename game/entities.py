"""Entity definitions for the Hogwarts training game."""
from dataclasses import dataclass, field


@dataclass
class Player:
    """Basic player combat stats."""

    name: str
    hp: int
    attack: int = 6
    defense: int = 3
    max_hp: int = field(init=False)

    def __post_init__(self) -> None:
        self.max_hp = self.hp


@dataclass
class Enemy:
    """Basic enemy combat stats."""

    kind: str
    hp: int
    attack: int = 4
    defense: int = 2
    max_hp: int = field(init=False)

    def __post_init__(self) -> None:
        self.max_hp = self.hp

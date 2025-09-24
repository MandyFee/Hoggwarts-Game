"""Level loading helpers."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from .entities import Enemy

DATA_PATH = Path(__file__).resolve().parent / "data" / "levels.json"


@dataclass(frozen=True)
class Level:
    """Immutable description of a duel encounter."""

    name: str
    enemy_kind: str
    enemy_hp: int
    enemy_attack: int
    enemy_defense: int
    reward: int = 0
    difficulty: str = "normal"

    def build_enemy(self) -> Enemy:
        """Instantiate the opponent for this encounter."""
        return Enemy(
            kind=self.enemy_kind,
            hp=self.enemy_hp,
            attack=self.enemy_attack,
            defense=self.enemy_defense,
        )

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "Level":
        _ensure_is_mapping(raw, "level definition")
        if "enemy" not in raw:
            _fail("Level entry is missing 'enemy' block.")
        enemy = raw["enemy"]
        _ensure_is_mapping(enemy, "enemy definition")

        try:
            name = str(raw.get("name", "Unknown Arena"))
            kind = str(enemy["kind"])
            hp = int(enemy["hp"])
            attack = int(enemy["attack"])
            defense = int(enemy["defense"])
        except KeyError as missing:
            _fail(f"Enemy definition is missing required field: {missing.args[0]}")
        except (TypeError, ValueError) as exc:
            _fail(f"Enemy stats must be numeric: {exc}")

        reward = int(raw.get("reward", 0))
        difficulty = str(raw.get("difficulty", "normal")).lower()
        if difficulty not in {"easy", "normal", "hard"}:
            _fail(f"Unsupported difficulty '{difficulty}' on level '{name}'.")

        if any(value <= 0 for value in (hp, attack, defense)):
            _fail(f"Enemy stats must be positive integers for '{name}'.")

        return cls(
            name=name,
            enemy_kind=kind,
            enemy_hp=hp,
            enemy_attack=attack,
            enemy_defense=defense,
            reward=max(0, reward),
            difficulty=difficulty,
        )


def _ensure_is_mapping(value: Any, description: str) -> None:
    if not isinstance(value, dict):
        _fail(f"Expected {description} to be an object, received {type(value).__name__}.")


def _fail(message: str) -> "NoReturn":
    print(f"[levels] {message}", file=sys.stderr)
    raise SystemExit(1)


def _coerce_levels(levels: Iterable[Dict[str, Any] | Level]) -> List[Level]:
    coerced: List[Level] = []
    for idx, item in enumerate(levels):
        if isinstance(item, Level):
            coerced.append(item)
            continue
        try:
            coerced.append(Level.from_dict(item))
        except SystemExit:
            raise
        except Exception as exc:  # pragma: no cover - safety net for unexpected data issues
            _fail(f"Unable to parse level at index {idx}: {exc}")
    return coerced


def _load_raw_levels(path: Path) -> Sequence[Dict[str, Any]]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _fail(f"Could not find level data file at {path}.")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        _fail(f"Malformed JSON in {path.name}: {exc}")

    if not isinstance(data, list):
        _fail("Top-level JSON structure must be a list of levels.")

    if not data:
        _fail("Level file must contain at least one level entry.")

    return data


def load_levels(path: Path | None = None) -> List[Level]:
    """Return a list of Hogwarts duel venues and foes."""
    source = path or DATA_PATH
    raw_levels = _load_raw_levels(source)
    return _coerce_levels(raw_levels)

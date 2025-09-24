"""Game engine and state management."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from .entities import Enemy, Player

PLAYER_ACTIONS = {"attack", "defend", "wait", "quit"}
ENEMY_ACTIONS = {"attack", "defend", "wait"}


@dataclass
class GameState:
    """Light-weight container tracking the running game."""

    running: bool = True
    tick: int = 0
    level_index: int = 0
    player_hp: int = 0
    enemy_hp: int = 0


class GameEngine:
    """Coordinate the flow of the turn-based combat."""

    def __init__(self, player: Player, levels: Sequence[Dict[str, Any]]) -> None:
        if not levels:
            raise ValueError("At least one level is required to start the game.")

        self.player = player
        self.levels: List[Dict[str, Any]] = list(levels)
        self.state = GameState(player_hp=player.hp)
        self.enemy: Optional[Enemy] = None
        self._player_guard = False
        self._enemy_guard = False
        self._load_level(0)

    @property
    def current_level(self) -> Dict[str, Any]:
        return self.levels[self.state.level_index]

    def is_running(self) -> bool:
        return self.state.running

    def stop(self) -> None:
        self.state.running = False

    def reset(self) -> None:
        """Reset the game back to the first level."""
        self.state = GameState(player_hp=self.player.max_hp)
        self.player.hp = self.player.max_hp
        self._player_guard = False
        self._enemy_guard = False
        self._load_level(0)

    def update(self, player_action: str, enemy_action: str) -> List[str]:
        """Resolve a full player/enemy turn and return log lines."""
        messages: List[str] = []
        if not self.state.running:
            return messages

        action = player_action.strip().lower()
        if action not in PLAYER_ACTIONS:
            action = "wait"

        if action == "quit":
            messages.append("You decide to retreat from the duel. Game over.")
            self.stop()
            return messages

        if self.enemy is None:
            raise RuntimeError("GameEngine.update called before an enemy was loaded.")

        # Player phase
        if action == "attack":
            damage = self.player.attack
            if self._enemy_guard:
                damage = max(0, damage - self.enemy.defense)
                self._enemy_guard = False
                if damage:
                    messages.append(
                        f"You attack and punch through the guard for {damage} damage."
                    )
                else:
                    messages.append(f"The {self.enemy.kind} blocks your attack!")
            else:
                messages.append(f"You attack and deal {damage} damage.")

            if damage:
                self.state.enemy_hp = max(0, self.state.enemy_hp - damage)
                self.enemy.hp = self.state.enemy_hp

        elif action == "defend":
            self._player_guard = True
            messages.append("You raise your guard, ready to deflect the next strike.")

        elif action == "wait":
            messages.append("You bide your time, watching the enemy closely.")

        enemy_defeated = False
        if self.state.enemy_hp <= 0:
            enemy_defeated = True
            messages.append(f"The {self.enemy.kind} is defeated!")
            self._advance_level(messages)

        # Enemy phase (skipped if the previous foe was just beaten)
        if not enemy_defeated and self.state.running:
            foe_action = enemy_action.strip().lower()
            if foe_action not in ENEMY_ACTIONS:
                foe_action = "wait"

            if foe_action == "attack":
                damage = self.enemy.attack
                if self._player_guard:
                    damage = max(0, damage - self.player.defense)
                    self._player_guard = False
                    if damage:
                        messages.append(
                            f"The {self.enemy.kind} attacks and slips past your guard for {damage} damage."
                        )
                    else:
                        messages.append(
                            f"You deflect the {self.enemy.kind}'s strike without taking damage."
                        )
                else:
                    messages.append(
                        f"The {self.enemy.kind} attacks and deals {damage} damage."
                    )

                if damage:
                    self.state.player_hp = max(0, self.state.player_hp - damage)
                    self.player.hp = self.state.player_hp

            elif foe_action == "defend":
                self._enemy_guard = True
                messages.append(f"The {self.enemy.kind} raises its guard.")

            elif foe_action == "wait":
                messages.append(f"The {self.enemy.kind} circles, waiting for an opening.")

        if self.state.player_hp <= 0 and self.state.running:
            messages.append("You collapse from your wounds. The duel is lost.")
            self.stop()

        self.state.tick += 1
        return messages

    def _load_level(self, index: int) -> None:
        self.state.level_index = index
        level = self.levels[index]
        enemy_data = level.get("enemy", {})
        self.enemy = Enemy(
            kind=enemy_data.get("kind", "Unknown Foe"),
            hp=enemy_data.get("hp", 10),
            attack=enemy_data.get("attack", 3),
            defense=enemy_data.get("defense", 1),
        )
        self.state.enemy_hp = self.enemy.hp
        self.enemy.hp = self.state.enemy_hp

    def _advance_level(self, messages: List[str]) -> None:
        next_index = self.state.level_index + 1
        if next_index >= len(self.levels):
            messages.append("All challenges cleared! You are victorious.")
            self.stop()
            return

        heal = min(5, self.player.max_hp - self.state.player_hp)
        if heal > 0:
            self.state.player_hp += heal
            self.player.hp = self.state.player_hp
            messages.append(f"You take a moment to recover {heal} HP before the next duel.")

        messages.append("A new challenger steps forward!")
        self._load_level(next_index)

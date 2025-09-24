"""Game engine and state management for Hogwarts-themed duels."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from .combat import compute_damage
from .entities import Enemy, Player
from .levels import Level

PLAYER_ACTIONS = {"cast", "protego", "focus", "exit", "item"}
ENEMY_ACTIONS = {"curse", "shield", "stalk"}
STARTING_STAMINA = 12

ITEM_EFFECTS: Dict[str, Dict[str, Any]] = {
    "chocolate frog": {
        "message": "You unwrap a Chocolate Frog and take a restorative bite.",
        "heal": 6,
        "status": "nourished",
    },
    "wand polish": {
        "message": "You buff your wand, letting the core hum with fresh power.",
        "stamina": 4,
        "status": "fortified",
    },
    "pepperup potion": {
        "message": "A gulp of Pepperup Potion sends sparks of energy through you.",
        "heal": 4,
        "stamina": 4,
        "status": "energised",
    },
}


@dataclass
class GameState:
    """Light-weight container tracking the running duel."""

    running: bool = True
    tick: int = 0
    level_index: int = 0
    player_hp: int = 0
    enemy_hp: int = 0
    stamina: int = STARTING_STAMINA
    score: int = 0
    status: str = "ok"


class GameEngine:
    """Coordinate the flow of each duel round."""

    def __init__(self, player: Player, levels: Sequence[Dict[str, Any] | Level]) -> None:
        if not levels:
            raise ValueError("At least one level is required to start the duel.")

        self.player = player
        self.levels: List[Level] = [lvl if isinstance(lvl, Level) else Level.from_dict(lvl) for lvl in levels]
        self._max_stamina = max(STARTING_STAMINA, player.attack * 2 + player.defense)
        self.state = GameState(player_hp=player.hp, stamina=self._max_stamina)
        self.enemy: Optional[Enemy] = None
        self._player_guard = False
        self._enemy_guard = False
        self._load_level(0)

    @property
    def current_level(self) -> Level:
        return self.levels[self.state.level_index]

    def is_running(self) -> bool:
        return self.state.running

    def stop(self) -> None:
        self.state.running = False
        self.state.status = "finished"

    def reset(self) -> None:
        """Reset the duel back to the opening round."""
        self.player.hp = self.player.max_hp
        self.state = GameState(
            running=True,
            tick=0,
            level_index=0,
            player_hp=self.player.hp,
            enemy_hp=0,
            stamina=self._max_stamina,
            score=0,
            status="ok",
        )
        self._player_guard = False
        self._enemy_guard = False
        self._load_level(0)

    def save_state(self, path: str | Path) -> None:
        """Persist the current duel state to JSON."""
        data: Dict[str, Any] = {
            "state": asdict(self.state),
            "player": {
                "name": self.player.name,
                "hp": self.state.player_hp,
                "attack": self.player.attack,
                "defense": self.player.defense,
                "inventory": list(self.player.inventory),
            },
            "enemy": None,
            "guards": {
                "player_guard": self._player_guard,
                "enemy_guard": self._enemy_guard,
            },
        }
        if self.enemy is not None:
            data["enemy"] = {
                "kind": self.enemy.kind,
                "hp": self.state.enemy_hp,
                "attack": self.enemy.attack,
                "defense": self.enemy.defense,
                "inventory": list(self.enemy.inventory),
            }

        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load_state(self, path: str | Path) -> None:
        """Restore a previously saved duel state."""
        payload = Path(path).read_text(encoding="utf-8")
        data = json.loads(payload)

        state_block = data.get("state")
        if not isinstance(state_block, dict):
            raise ValueError("Saved game is missing state information.")

        player_block = data.get("player", {})
        self.player.name = str(player_block.get("name", self.player.name))
        self.player.attack = int(player_block.get("attack", self.player.attack))
        self.player.defense = int(player_block.get("defense", self.player.defense))
        self.player.inventory = list(player_block.get("inventory", self.player.inventory))
        player_hp = int(player_block.get("hp", self.player.hp))
        self.player.hp = player_hp

        level_index = int(state_block.get("level_index", 0))
        if not 0 <= level_index < len(self.levels):
            raise ValueError("Saved game references an unknown level index.")

        tick = int(state_block.get("tick", 0))
        stamina = int(state_block.get("stamina", self._max_stamina))
        score = int(state_block.get("score", 0))
        status = str(state_block.get("status", "ok"))
        running = bool(state_block.get("running", True))

        self._load_level(level_index)

        enemy_block = data.get("enemy")
        if enemy_block:
            self.enemy = Enemy(
                kind=enemy_block.get("kind", self.enemy.kind if self.enemy else "Unknown Opponent"),
                hp=int(enemy_block.get("hp", self.enemy.hp if self.enemy else 10)),
                attack=int(enemy_block.get("attack", self.enemy.attack if self.enemy else 3)),
                defense=int(enemy_block.get("defense", self.enemy.defense if self.enemy else 1)),
                inventory=list(enemy_block.get("inventory", [])),
            )
            enemy_hp = self.enemy.hp
        else:
            enemy_hp = self.enemy.hp if self.enemy else 0

        self.state = GameState(
            running=running,
            tick=tick,
            level_index=level_index,
            player_hp=player_hp,
            enemy_hp=enemy_hp,
            stamina=max(0, min(stamina, self._max_stamina)),
            score=score,
            status=status,
        )

        guards = data.get("guards", {})
        self._player_guard = bool(guards.get("player_guard", False))
        self._enemy_guard = bool(guards.get("enemy_guard", False))

    def update(self, player_action: str, enemy_action: str, item_name: Optional[str] = None) -> List[str]:
        """Resolve a full round and return narration lines."""
        messages: List[str] = []
        if not self.state.running:
            return messages

        action = player_action.strip().lower()
        if action not in PLAYER_ACTIONS:
            action = "focus"

        if action == "exit":
            messages.append("You lower your wand and bow out of the duel.")
            self.stop()
            return messages

        if self.enemy is None:
            raise RuntimeError("GameEngine.update called before an opponent was loaded.")

        self.state.status = "ok"

        # Player phase
        if action == "cast":
            self.state.status = "attacking"
            raw_damage = compute_damage(self.player, self.enemy, action)
            if self.state.stamina <= 2:
                raw_damage = max(0, raw_damage - 1)
            damage = raw_damage
            if self._enemy_guard:
                block = 1 + self.enemy.defense
                damage = max(0, damage - block)
                self._enemy_guard = False
                if damage:
                    messages.append(
                        f"You cast a spell that slips past the shield for {damage} damage."
                    )
                else:
                    messages.append(
                        f"The {self.enemy.kind} repels your spell with a shimmering Protego!"
                    )
            else:
                if damage:
                    messages.append(f"Your spell strikes true for {damage} damage.")
                else:
                    messages.append(f"Your spell fizzles before it reaches the {self.enemy.kind}.")

            if damage:
                self.state.enemy_hp = max(0, self.state.enemy_hp - damage)
                self.enemy.hp = self.state.enemy_hp
            self.state.stamina = max(0, self.state.stamina - 2)

        elif action == "protego":
            self.state.status = "guarded"
            self._player_guard = True
            self.state.stamina = max(0, self.state.stamina - 1)
            messages.append("You conjure Protego, conjuring a gleaming shield in front of you.")

        elif action == "focus":
            self.state.status = "focused"
            self.state.stamina = min(self._max_stamina, self.state.stamina + 3)
            messages.append("You take a steadying breath, letting your magic coalesce.")

        elif action == "item":
            messages.extend(self._use_inventory_item(item_name))

        enemy_defeated = False
        if self.state.enemy_hp <= 0:
            enemy_defeated = True
            messages.append(f"The {self.enemy.kind} is disarmed and crumples to the floor!")
            self._handle_victory(messages)

        # Opponent phase (skipped if the previous foe was just defeated)
        if not enemy_defeated and self.state.running:
            foe_action = enemy_action.strip().lower()
            if foe_action not in ENEMY_ACTIONS:
                foe_action = "stalk"

            if foe_action == "curse":
                raw_damage = compute_damage(self.enemy, self.player, foe_action)
                if self._player_guard:
                    block = 1 + self.player.defense
                    damage = max(0, raw_damage - block)
                    self._player_guard = False
                    if damage:
                        messages.append(
                            f"The {self.enemy.kind} unleashes a curse that cracks your shield for {damage} damage."
                        )
                    else:
                        messages.append(
                            f"Protego flares brilliantly, nullifying the {self.enemy.kind}'s curse!"
                        )
                else:
                    damage = raw_damage
                    if damage:
                        messages.append(
                            f"The {self.enemy.kind} hurls a stinging hex for {damage} damage."
                        )
                    else:
                        messages.append(
                            f"You twist aside and the {self.enemy.kind}'s hex scatters harmlessly."
                        )

                if damage:
                    self.state.player_hp = max(0, self.state.player_hp - damage)
                    self.player.hp = self.state.player_hp
                    self.state.status = "stunned"

            elif foe_action == "shield":
                self._enemy_guard = True
                messages.append(f"The {self.enemy.kind} throws up a Protego shield.")

            elif foe_action == "stalk":
                messages.append(f"The {self.enemy.kind} circles warily, wand poised.")

        if self.state.player_hp <= 0 and self.state.running:
            messages.append("Your knees buckle as the duel slips away. Darkness closes in.")
            self.stop()

        if self.state.running:
            self.state.tick += 1
        return messages

    def _use_inventory_item(self, item_name: Optional[str]) -> List[str]:
        messages: List[str] = []
        if not item_name:
            messages.append("You fumble with your satchel and lose the moment.")
            return messages

        key = item_name.strip().lower()
        actual_name: Optional[str] = None
        removed_index = -1
        for idx, entry in enumerate(self.player.inventory):
            if entry.strip().lower() == key:
                actual_name = self.player.inventory.pop(idx)
                removed_index = idx
                break

        if actual_name is None:
            messages.append(f"You rummage for {item_name}, but your satchel comes up empty.")
            return messages

        effect = ITEM_EFFECTS.get(key)
        if effect is None:
            insert_at = removed_index if removed_index >= 0 else len(self.player.inventory)
            self.player.inventory.insert(insert_at, actual_name)
            messages.append(f"You brandish {actual_name}, but it refuses to react mid-duel.")
            return messages

        messages.append(effect.get("message", f"You use {actual_name}."))

        heal_amount = int(effect.get("heal", 0) or 0)
        if heal_amount:
            healed = min(heal_amount, self.player.max_hp - self.state.player_hp)
            if healed:
                self.state.player_hp += healed
                self.player.hp = self.state.player_hp
                messages.append(f"You recover {healed} HP as warmth rushes through you.")
            else:
                messages.append("You're already in perfect shape.")

        stamina_amount = int(effect.get("stamina", 0) or 0)
        if stamina_amount:
            gained = min(stamina_amount, self._max_stamina - self.state.stamina)
            if gained:
                self.state.stamina += gained
                messages.append(f"Your focus steadies, restoring {gained} stamina.")
            else:
                messages.append("Your focus is already razor sharp.")

        self.state.status = effect.get("status", self.state.status)
        self._player_guard = False
        return messages

    def _load_level(self, index: int) -> None:
        self.state.level_index = index
        level = self.levels[index]
        self.enemy = level.build_enemy()
        self.state.enemy_hp = self.enemy.hp

    def _handle_victory(self, messages: List[str]) -> None:
        level = self.current_level
        if level.reward:
            self.state.score += level.reward
            messages.append(f"You earn {level.reward} House Points for the victory!")
        self.state.status = "victorious"
        self._advance_level(messages)

    def _advance_level(self, messages: List[str]) -> None:
        next_index = self.state.level_index + 1
        if next_index >= len(self.levels):
            messages.append("Students around you erupt in cheers—you've won the House Cup!")
            self.stop()
            return

        heal = min(5, self.player.max_hp - self.state.player_hp)
        if heal > 0:
            self.state.player_hp += heal
            self.player.hp = self.state.player_hp
            messages.append(f"Madam Pomfrey rushes in and mends {heal} HP before the next round.")

        self.state.stamina = min(self._max_stamina, self.state.stamina + 4)
        messages.append("Another challenger steps from the shadows, wand at the ready!")
        self._load_level(next_index)

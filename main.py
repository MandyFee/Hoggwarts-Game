"""CLI entry point for the Hogwarts dueling game."""
from pathlib import Path
from typing import Optional

from game.ai import choose_enemy_move, set_ai_context
from game.engine import GameEngine
from game.entities import Player
from game.levels import Level, load_levels
from game.ui import (
    prompt_inventory_choice,
    prompt_load_path,
    prompt_player_action,
    prompt_save_path,
    render_header,
    render_status,
)

DEFAULT_SAVE_PATH = Path("saves/hogwarts_duel.json")


def main() -> None:
    print("Welcome to the Hogwarts Dueling Club!")
    print("Type cast, protego, focus, bag, save, load, h for help, or exit when prompted.")
    print()

    levels = load_levels()
    player = Player(name="Hogwarts Champion", hp=30)
    engine = GameEngine(player, levels)

    while engine.is_running():
        level: Level = engine.current_level
        render_header(level.name, engine.state.tick)

        enemy = engine.enemy
        enemy_kind = enemy.kind if enemy else level.enemy_kind
        enemy_hp = engine.state.enemy_hp if enemy else level.enemy_hp
        set_ai_context(engine.state.player_hp, engine.state.enemy_hp)

        render_status(
            engine.state.player_hp,
            player.max_hp,
            enemy_kind,
            enemy_hp,
            level.enemy_hp,
            engine.state.stamina,
            engine._max_stamina,  # type: ignore[attr-defined]
            engine.state.status,
            engine.state.score,
        )

        selected_item: Optional[str] = None
        action: Optional[str] = None
        refresh_view = False

        while True:
            choice = prompt_player_action()
            if choice == "save":
                save_target = prompt_save_path(str(DEFAULT_SAVE_PATH))
                if save_target is None:
                    continue
                save_path = Path(save_target).expanduser()
                try:
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    engine.save_state(save_path)
                except OSError as exc:
                    print(f"Could not save duel: {exc}")
                else:
                    print(f"Duel saved to {save_path}")
                continue

            if choice == "load":
                load_target = prompt_load_path(str(DEFAULT_SAVE_PATH))
                if load_target is None:
                    continue
                load_path = Path(load_target).expanduser()
                try:
                    engine.load_state(load_path)
                except FileNotFoundError:
                    print(f"No save file found at {load_path}")
                    continue
                except Exception as exc:
                    print(f"Could not load duel: {exc}")
                    continue
                print(f"Loaded duel from {load_path}")
                refresh_view = True
                break

            if choice == "bag":
                item_choice = prompt_inventory_choice(engine.player.inventory)
                if item_choice is None:
                    continue
                selected_item = item_choice
                action = "item"
                break

            action = choice
            break

        if refresh_view:
            print()
            continue

        if action is None:
            continue

        enemy_action = (
            "stalk"
            if action == "exit"
            else choose_enemy_move(engine.state.tick, level.difficulty)
        )

        for line in engine.update(action, enemy_action, selected_item):
            print(line)

        if engine.is_running():
            print()

    print("Professor Flitwick applauds as the training session ends. Well duelled!")


if __name__ == "__main__":
    main()

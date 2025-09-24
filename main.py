"""CLI entry point for the Hogwarts training game."""
from game.ai import choose_enemy_move
from game.engine import GameEngine
from game.entities import Player
from game.levels import load_levels
from game.ui import prompt_player_action, render_header, render_status


def main() -> None:
    print("Welcome to Defence Club! Prepare to hone your skills.")
    levels = load_levels()
    player = Player(name="Apprentice", hp=30)
    engine = GameEngine(player, levels)

    while engine.is_running():
        level = engine.current_level
        render_header(level.get("name", "Unknown"), engine.state.tick)

        enemy = engine.enemy
        enemy_kind = enemy.kind if enemy else "Unknown"
        render_status(engine.state.player_hp, enemy_kind, engine.state.enemy_hp)

        player_action = prompt_player_action()
        enemy_action = "wait" if player_action == "quit" else choose_enemy_move(engine.state.tick)

        for line in engine.update(player_action, enemy_action):
            print(line)

        if engine.is_running():
            print()

    print("Thanks for playing!")


if __name__ == "__main__":
    main()

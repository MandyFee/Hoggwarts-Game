"""CLI entry point for the Hogwarts dueling game."""
from game.ai import choose_enemy_move, set_ai_context
from game.engine import GameEngine
from game.entities import Player
from game.levels import Level, load_levels
from game.ui import prompt_player_action, render_header, render_status


def main() -> None:
    print("Welcome to the Hogwarts Dueling Club!")
    print("Type cast, protego, focus, h for help, or exit when prompted.")
    print()

    levels = load_levels()
    player = Player(name="Hogwarts Champion", hp=30)
    engine = GameEngine(player, levels)

    while engine.is_running():
        level: Level = engine.current_level
        render_header(level.name, engine.state.tick)

        enemy = engine.enemy
        enemy_kind = enemy.kind if enemy else level.enemy_kind
        enemy_hp = enemy.hp if enemy else level.enemy_hp
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

        player_action = prompt_player_action()
        enemy_action = (
            "stalk"
            if player_action == "exit"
            else choose_enemy_move(engine.state.tick, level.difficulty)
        )

        for line in engine.update(player_action, enemy_action):
            print(line)

        if engine.is_running():
            print()

    print("Professor Flitwick applauds as the training session ends. Well duelled!")


if __name__ == "__main__":
    main()

"""Console UI helpers for the Hogwarts training game."""
from typing import Iterable

VALID_ACTIONS = ("attack", "defend", "wait", "quit")


def render_header(level_name: str, tick: int) -> None:
    """Render a simple header showing the current level and turn."""
    divider = "=" * 40
    print(divider)
    print(f" Level: {level_name}")
    print(f" Turn : {tick + 1}")
    print(divider)


def prompt_player_action() -> str:
    """Prompt the player until a supported action is entered."""
    prompt = "Choose action [attack/defend/wait/quit]: "
    while True:
        try:
            choice = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            return "quit"

        action = choice.strip().lower()
        if action in VALID_ACTIONS:
            return action

        print("Invalid action. Try one of:", ", ".join(VALID_ACTIONS))


def render_status(player_hp: int, enemy_kind: str, enemy_hp: int) -> None:
    """Render the player and enemy health."""
    print(f"You: {player_hp:>3} HP  |  {enemy_kind}: {enemy_hp:>3} HP")

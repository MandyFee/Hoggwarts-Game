"""Console UI helpers for Hogwarts duels."""
from __future__ import annotations

from typing import Dict

try:
    from colorama import Fore, Style, init as colorama_init
except ImportError:  # pragma: no cover - colorized output gracefully degrades
    class _ColorFallback:
        def __getattr__(self, _: str) -> str:
            return ""

    Fore = Style = _ColorFallback()  # type: ignore

    def colorama_init(*_: object, **__: object) -> None:  # type: ignore
        """No-op fallback when colorama is not available."""

else:
    colorama_init(autoreset=True)

TITLE_COLOR = Fore.YELLOW + Style.BRIGHT
BORDER_COLOR = Fore.BLUE + Style.BRIGHT
LABEL_COLOR = Fore.CYAN + Style.BRIGHT
PLAYER_COLOR = Fore.GREEN + Style.BRIGHT
ENEMY_COLOR = Fore.MAGENTA + Style.BRIGHT
INFO_COLOR = Fore.WHITE + Style.NORMAL
ALERT_COLOR = Fore.RED + Style.BRIGHT
EMPTY_COLOR = Fore.BLACK + Style.DIM
RESET = Style.RESET_ALL

VALID_ACTIONS = ("cast", "protego", "focus", "exit")
ACTION_DESCRIPTIONS: Dict[str, str] = {
    "cast": "Launch an attacking charm.",
    "protego": "Raise a protective shield.",
    "focus": "Steady yourself to stay sharp.",
    "exit": "Lower your wand and concede.",
}
HELP_ACTIONS = {"h", "help", "?"}

def render_header(level_name: str, tick: int) -> None:
    """Render a duel header showing the current venue and round."""
    title = "HOGWARTS DUELING CLUB"
    round_label = f"Round {tick + 1:02d}"
    venue_label = f"Venue: {level_name}"

    width = max(len(title), len(round_label), len(venue_label)) + 4
    top_border = BORDER_COLOR + "+" + "=" * (width - 2) + "+" + RESET
    separator = BORDER_COLOR + "+" + "-" * (width - 2) + "+" + RESET

    print(top_border)
    print(f"{BORDER_COLOR}| {TITLE_COLOR}{title.center(width - 4)}{RESET}{BORDER_COLOR} |{RESET}")
    print(separator)
    print(f"{BORDER_COLOR}| {LABEL_COLOR}{round_label.ljust(width - 4)}{RESET}{BORDER_COLOR} |{RESET}")
    print(f"{BORDER_COLOR}| {LABEL_COLOR}{venue_label.ljust(width - 4)}{RESET}{BORDER_COLOR} |{RESET}")
    print(top_border)

def render_status(
    player_hp: int,
    player_max_hp: int,
    enemy_kind: str,
    enemy_hp: int,
    enemy_max_hp: int,
    stamina: int,
    max_stamina: int,
    status: str,
    score: int,
) -> None:
    """Render the current stamina of both duelists along with score."""
    print()
    print(f"{LABEL_COLOR}Stamina report:{RESET}")
    player_bar = _build_bar(player_hp, player_max_hp, PLAYER_COLOR)
    enemy_bar = _build_bar(enemy_hp, enemy_max_hp, ENEMY_COLOR)
    stamina_bar = _build_bar(stamina, max_stamina, INFO_COLOR, width=20)
    print(f"  {PLAYER_COLOR}You   {player_hp:>3}/{player_max_hp:<3} HP{RESET} |{player_bar}{RESET}|")
    print(
        f"  {ENEMY_COLOR}Foe   {enemy_hp:>3}/{enemy_max_hp:<3} HP{RESET} |{enemy_bar}{RESET}|"
        f" {INFO_COLOR}({enemy_kind}){RESET}"
    )
    status_label = status.upper()
    print(
        f"  {LABEL_COLOR}Focus {RESET}{stamina:>3}/{max_stamina:<3} |{stamina_bar}{RESET}|"
        f"  {INFO_COLOR}Status:{RESET} {status_label:<10}  {INFO_COLOR}Score:{RESET} {score}"
    )

def prompt_player_action() -> str:
    """Prompt the player until a supported action is entered."""
    print()
    print(f"{LABEL_COLOR}Available spells:{RESET}")
    for action in VALID_ACTIONS:
        description = ACTION_DESCRIPTIONS.get(action, "")
        print(f"  {Fore.WHITE + Style.BRIGHT}{action:<8}{RESET} - {INFO_COLOR}{description}{RESET}")
    print(f"  {Fore.WHITE + Style.BRIGHT}h{'':<7}{RESET} - {INFO_COLOR}Show help screen{RESET}")

    prompt = f"{LABEL_COLOR}Select your spell >>> {RESET}"
    while True:
        try:
            choice = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            return "exit"

        action = choice.strip().lower()
        if action in HELP_ACTIONS:
            render_help_screen()
            continue
        if action in VALID_ACTIONS:
            return action

        valid = ", ".join([*VALID_ACTIONS, "h"])
        print(f"{ALERT_COLOR}That incantation fizzled. Try one of: {valid}{RESET}")

def render_help_screen() -> None:
    """Display a lightweight help overlay without advancing the game."""
    print()
    print(BORDER_COLOR + "=" * 40 + RESET)
    print(f"{TITLE_COLOR} DUELING CLUB HELP {RESET}")
    print(BORDER_COLOR + "=" * 40 + RESET)
    print(f"{INFO_COLOR}cast{RESET}    - Sling an offensive charm at your opponent.")
    print(f"{INFO_COLOR}protego{RESET} - Raise a shield to blunt the next attack.")
    print(f"{INFO_COLOR}focus{RESET}   - Regain stamina and sharpen your aim.")
    print(f"{INFO_COLOR}exit{RESET}    - Bow out of the duel gracefully.")
    print(f"{INFO_COLOR}h{RESET}       - Show this help screen.")
    print(BORDER_COLOR + "=" * 40 + RESET)
    print()

def _build_bar(current: int, maximum: int, color: str, width: int = 24) -> str:
    if maximum <= 0:
        return color + "-" * width + RESET

    ratio = max(0.0, min(1.0, current / maximum))
    filled = max(0, min(width, int(round(ratio * width))))
    empty = width - filled
    return color + "#" * filled + EMPTY_COLOR + "-" * empty + RESET

"""Level loading helpers."""
from typing import Any, Dict, List


def load_levels() -> List[Dict[str, Any]]:
    """Return a simple list of level definitions.

    Each level provides a name and the stats required to spawn the enemy the
    player will face.
    """
    return [
        {
            "name": "Training Grounds",
            "enemy": {"kind": "Animated Dummy", "hp": 12, "attack": 3, "defense": 1},
        },
        {
            "name": "Forbidden Corridor",
            "enemy": {"kind": "Sneaky Pixie", "hp": 16, "attack": 4, "defense": 2},
        },
        {
            "name": "Potion Lab Finale",
            "enemy": {"kind": "Runaway Cauldron", "hp": 20, "attack": 5, "defense": 2},
        },
    ]

from pathlib import Path
from typing import Any, Dict
import yaml


# --------- Config loading ---------
def load_yaml(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# --------- Sanity check ---------
def check_paths_exist(paths: list[Path]):
    missing_paths = []
    for path in paths:
        if not path.exists(): missing_paths.append(path)

    if missing_paths:
        raise FileNotFoundError(
            "Expected paths not found.",
            f"Missing: {'\n'.join(missing_paths)}"
        )

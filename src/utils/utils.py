from pathlib import Path
from typing import Any, Dict
import yaml


# --------- Config loading and saving ---------
def load_yaml(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def save_yaml(yaml_data: Dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(yaml_data, f, sort_keys=False)


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


def expand_param_grid(param_grid: Dict[str, Any]) -> Dict[str, list]:
    """
    Convert a parameter grid into scikit-learn compatible lists.

    Supports explicit lists or range definitions using
    {"start": ..., "stop": ..., "step": ...}.

    Example:
        Input:
            {
                "max_depth": {"start": 5, "stop": 25, "step": 5},
                "n_estimators": [200, 400, 800]
            }
        Output:
            {
                "max_depth": [5, 10, 15, 20, 25],
                "n_estimators": [200, 400, 800]
            }

    Args:
        param_grid: Parameter grid definition.

    Returns:
        Expanded parameter grid as lists of values.
    """
    expanded = {}

    for param, values in param_grid.items():
        if isinstance(values, dict):
            start = values["start"]
            stop = values["stop"]
            step = values.get("step", 1)
            expanded[param] = list(range(start, stop + 1, step))
        else:
            expanded[param] = values

    return expanded

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.utils.utils import load_yaml, save_yaml


def make_model_yaml(
    model_name: str,
    model_type: str,
    class_path: str,
    code_path: str,
    yaml_path: str | Path = "configs/models.yaml",
    overwrite: bool = False,
) -> Dict[str, Any]:
    """
    Create (or optionally overwrite) a model entry in models.yaml.
    """
    models_yaml = load_yaml(yaml_path)

    if model_name in models_yaml and not overwrite:
        raise ValueError(
            f"Model '{model_name}' already exists in {yaml_path}. "
            "Use overwrite=True to replace it."
        )

    models_yaml[model_name] = {
        "model_type": model_type,
        "class_path": class_path,
        "code_path" : code_path,
        "best"      : {
            "path"      : "",
            "parameters": {},
            "metric"    : "",
            "value"     : 0.0,
            "trained_at": "",
        },
        "Tuning"    : {"enabled": False},
    }

    save_yaml(models_yaml, yaml_path)
    return models_yaml


def get_model_yaml(
    model_name: str,
    yaml_path: str | Path = "configs/models.yaml",
) -> Dict[str, Any]:
    """
    Retrieve one model entry from models.yaml.
    """
    models_yaml = load_yaml(yaml_path)

    if model_name not in models_yaml:
        raise KeyError(f"Model '{model_name}' not found in {yaml_path}")

    return models_yaml[model_name]


def update_model_yaml(
    model_name: str,
    parameters: Dict[str, Any],
    best_path: str,
    metric: str,
    value: float,
    yaml_path: str | Path = "configs/models.yaml",
) -> Dict[str, Any]:
    """
    Update the 'best' section and parameters of a model after training.
    """
    models_yaml = load_yaml(yaml_path)

    if model_name not in models_yaml:
        raise KeyError(f"Model '{model_name}' not found in {yaml_path}")

    models_yaml[model_name]["best"] = {
        "path"      : best_path,
        "parameters": parameters,
        "metric"    : metric,
        "value"     : float(value),
        "trained_at": datetime.now().isoformat(),
    }

    save_yaml(models_yaml, yaml_path)
    return models_yaml

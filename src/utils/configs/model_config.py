from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class TuningConfig:
    enabled: bool
    method: str = "grid"
    cv: int = 5
    param_grid: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class BestModelInfo:
    path: Path
    parameters: Dict[str, Any]
    metric: str
    value: float
    trained_at: str


@dataclass(frozen=True)
class ModelConfig:
    model_type: str
    class_path: str
    code_path: Path
    best: BestModelInfo
    tuning: Optional[TuningConfig]


def _parse_tuning_cfg(cfg: Dict[str, Any]) -> Optional[TuningConfig]:
    tuning_cfg = cfg.get("tuning")

    if not tuning_cfg or not tuning_cfg.get("enabled", False):
        return None

    return TuningConfig(
        enabled=True,
        method=tuning_cfg.get("method", "grid"),
        cv=int(tuning_cfg.get("cv", 5)),
        param_grid=tuning_cfg.get("param_grid"),
    )


def _parse_single_model(model_cfg: Dict[str, Any]) -> ModelConfig:
    """
    Get a single model configuration as a dataclass instance

    Args:
        model_cfg: The model's configuration as a Dict

    Returns:
        The model configuration as a dataclass instance
    """
    best_cfg = model_cfg.get("best", {})

    best = BestModelInfo(
        path=Path(best_cfg.get("path", "")),
        parameters=best_cfg.get("parameters", {}),
        metric=best_cfg.get("metric", ""),
        value=float(best_cfg.get("value", 0.0)),
        trained_at=best_cfg.get("trained_at", ""),
    )

    tuning = _parse_tuning_cfg(model_cfg)

    return ModelConfig(
        model_type=model_cfg["model_type"],
        class_path=model_cfg["class_path"],
        code_path=Path(model_cfg["code_path"]),
        best=best,
        tuning=tuning
    )


def parse_model_yaml(
    models_cfg: Dict[str, Any],
    model_name: str,
) -> ModelConfig:
    """
    Get a single model configuration as a dataclass instance from the models yaml file.
    """
    if model_name not in models_cfg:
        raise KeyError(f"Model '{model_name}' not found in models configuration")

    return _parse_single_model(models_cfg[model_name])


def parse_models_yaml(
    models_cfg: Dict[str, Any],
) -> Dict[str, ModelConfig]:
    """
    Get all models configurations as dataclass instances.
    """
    return {
        model_name: _parse_single_model(model_cfg)
        for model_name, model_cfg in models_cfg.items()
    }

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class DataConfig:
    name: str
    source_url: str
    sha256: str
    raw_dir: Path
    processed_dir: Path
    zip_filename: str
    dataset_dirname: str
    hourly_csv: str
    daily_csv: str

    def __post_init__(self):
        self.extracted_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)

    @property
    def zip_path(self) -> Path:
        return self.raw_dir / self.zip_filename

    @property
    def extracted_path(self) -> Path:
        return self.raw_dir / self.dataset_dirname

    @property
    def processed_path(self) -> Path:
        return self.processed_dir / self.dataset_dirname

    @property
    def raw_daily_data_path(self):
        return self.extracted_path / self.daily_csv

    @property
    def raw_hourly_data_path(self):
        return self.extracted_path / self.hourly_csv

    @property
    def processed_daily_data_path(self):
        return self.processed_path / self.daily_csv

    @property
    def processed_hourly_data_path(self):
        return self.processed_path / self.hourly_csv


def parse_config(cfg: Dict[str, Any]) -> DataConfig:
    d = cfg["dataset"]
    f = cfg["files"]

    return DataConfig(
        name=d["name"],
        source_url=d["source_url"],
        sha256=str(d["sha256"]).strip(),
        raw_dir=Path(d["raw_dir"]),
        processed_dir=Path(d["processed_dir"]),
        zip_filename=d["zip_filename"],
        dataset_dirname=d["dataset_dirname"],
        hourly_csv=f["hourly_csv"],
        daily_csv=f["daily_csv"]
    )

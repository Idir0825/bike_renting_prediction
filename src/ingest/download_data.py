from __future__ import annotations

import hashlib
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import requests
import yaml


# --------- Config loading ---------
def load_yaml(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@dataclass(frozen=True)
class DataConfig:
    name: str
    source_url: str
    sha256: str
    raw_dir: str
    processed_dir: str
    zip_filename: str
    extracted_dirname: str
    hourly_csv: str
    daily_csv: str

    @property
    def zip_path(self) -> Path:
        return self.raw_dir / self.zip_filename

    @property
    def extracted_path(self) -> Path:
        return self.raw_dir / self.extracted_dirname


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
        extracted_dirname=d["extracted_dirname"],
        hourly_csv=f["hourly_csv"],
        daily_csv=f["daily_csv"]
    )


# --------- Integrity ---------
def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


# --------- Download ---------
def download_file(url: str, dst: Path, chunk_size: int = 1024 * 1024) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with dst.open("wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)


def ensure_downloaded(cfg: DataConfig) -> None:
    if cfg.zip_path.exists():
        return
    download_file(cfg.source_url, cfg.zip_path)


# --------- Extract ---------
def extract_zip(zip_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir)


def ensure_extracted(cfg: DataConfig) -> None:
    # Extract into a temp folder then move to final folder (avoid partial state)
    if cfg.extracted_path.exists():
        return

    tmp_dir = cfg.raw_dir / (cfg.extracted_dirname + "_tmp")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)

    extract_zip(cfg.zip_path, tmp_dir)

    tmp_dir.rename(cfg.extracted_path)


# --------- Main pipeline ---------
def main(config_path: str = "configs/data.yaml") -> None:
    cfg_dict = load_yaml(config_path)
    cfg = parse_config(cfg_dict)

    cfg.raw_dir.mkdir(parents=True, exist_ok=True)
    cfg.processed_dir.mkdir(parents=True, exist_ok=True)

    ensure_downloaded(cfg)
    ensure_extracted(cfg)

    # Sanity check
    hourly = cfg.extracted_path / cfg.hourly_csv
    daily = cfg.extracted_path / cfg.daily_csv
    if not hourly.exists() or not daily.exists():
        raise FileNotFoundError(
            f"Expected files not found in {cfg.extracted_path}",
            f"Missing: {hourly.name if not hourly.exists() else ''}"
            f"{daily.name if not daily.exists() else ''}"
        )


if __name__ == '__main__':
    main()

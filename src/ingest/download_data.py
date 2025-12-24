from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

import requests

from src.utils.configs.data_config import DataConfig, parse_config
from src.utils.utils import load_yaml, check_paths_exist


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

    tmp_dir = cfg.raw_dir / (cfg.dataset_dirname + "_tmp")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)

    extract_zip(cfg.zip_path, tmp_dir)

    tmp_dir.rename(cfg.extracted_path)


# --------- Main pipeline ---------
def main(config_path: str = "configs/data.yaml") -> None:
    cfg_dict = load_yaml(config_path)
    cfg = parse_config(cfg_dict)

    ensure_downloaded(cfg)
    ensure_extracted(cfg)

    # Sanity check
    check_paths_exist([cfg.raw_hourly_data_path, cfg.raw_daily_data_path])


if __name__ == '__main__':
    main()

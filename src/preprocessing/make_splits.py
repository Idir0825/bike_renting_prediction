import argparse
import pandas as pd

from src.utils.configs.data_config import parse_config
from src.utils.utils import load_yaml, check_paths_exist


# --------- Main pipeline ---------
def main(args: argparse.Namespace, config_path: str = "configs/data.yaml") -> None:
    cfg_dict = load_yaml(config_path)
    cfg = parse_config(cfg_dict)

    check_paths_exist([cfg.processed_daily_data_path, cfg.processed_hourly_data_path])

    daily_df = pd.read_csv(cfg.processed_daily_data_path)
    hourly_df = pd.read_csv(cfg.processed_hourly_data_path)

    train_split, _ = args.splits
    nb_train_records_daily = int(len(daily_df) * train_split)
    nb_train_records_hourly = int(len(hourly_df) * train_split)

    train_hourly_df = hourly_df[:nb_train_records_hourly]
    test_hourly_df = hourly_df[nb_train_records_hourly:]
    train_daily_df = daily_df[:nb_train_records_daily]
    test_daily_df = daily_df[nb_train_records_daily:]

    # Save splitted data
    train_hourly_df.to_csv(cfg.train_hourly_data_path, index=False)
    test_hourly_df.to_csv(cfg.test_hourly_data_path, index=False)
    train_daily_df.to_csv(cfg.train_daily_data_path, index=False)
    test_daily_df.to_csv(cfg.test_daily_data_path, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Data splitting parser")
    parser.add_argument("--splits", nargs=2, type=float, default=[0.85, 0.15], help="How the data should be splitted (train, test) (should sum up to 1)")
    arguments = parser.parse_args()

    if sum(arguments.splits) != 1:
        raise ValueError(f"The sum of all splits should equal to 1, got: {sum(arguments.splits)}")

    main(arguments)

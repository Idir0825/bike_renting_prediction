from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np

from src.utils.configs.data_config import parse_config
from src.utils.utils import load_yaml, check_paths_exist

from src.ingest.ingest_constants import columns_to_drop, categorical_features, column_names_map


def one_hot_encode(df: pd.DataFrame,
                   columns: list[str]
                   ) -> tuple[pd.DataFrame, OneHotEncoder]:
    """
    One-hot encode specified categorical columns and return the transformed dataframe and the fitted encoder
    """
    encoder = OneHotEncoder(
        sparse_output=False,
        handle_unknown="ignore"
    )

    encoded_array = encoder.fit_transform(df[columns])

    encoded_df = pd.DataFrame(
        encoded_array,
        columns=encoder.get_feature_names_out(columns),
        index=df.index
    )

    df_out = df.drop(columns=columns).join(encoded_df)

    return df_out, encoder


def cyclic_encode(df: pd.DataFrame, periods: dict[str, int], drop: bool = True, offsets: dict[str, int] | None = None) -> pd.DataFrame:
    """
    Add cyclic (sin/cos) encoding for specified columns.

    Args:
        df: Input dataframe.
        periods: Mapping column -> period (e.g., {"hr": 24, "weekday": 7, "mnth": 12}).
        drop: If True, drop original columns after encoding.
        offsets: Optional mapping column -> offset to apply before encoding (e.g., {"mnth": 1} for 1..12).

    Returns:
        Transformed dataframe (copy).
    """
    df_out = df.copy()
    offsets = offsets or {}

    for col, period in periods.items():

        if col not in df.columns:
            raise KeyError(f"Column {col} not in dataframe ...")

        offset = offsets.get(col, 0)
        x = (df_out[col].astype(float) - float(offset) % float(period))

        angle = 2.0 * np.pi * x / float(period)
        df_out[f"{col}_sin"] = np.sin(angle)
        df_out[f"{col}_cos"] = np.cos(angle)

    if drop:
        df_out = df_out.drop(columns=list(periods.keys()))

    return df_out


# --------- Main pipeline ---------
def main(config_path: str = "configs/data.yaml") -> None:
    cfg_dict = load_yaml(config_path)
    cfg = parse_config(cfg_dict)

    check_paths_exist([cfg.raw_hourly_data_path, cfg.raw_daily_data_path])

    daily_df = pd.read_csv(cfg.raw_daily_data_path)
    hourly_df = pd.read_csv(cfg.raw_hourly_data_path)

    # Drop unused columns (repetition, data leakage)
    daily_df.drop(columns_to_drop, axis=1, inplace=True)
    hourly_df.drop(columns_to_drop, axis=1, inplace=True)

    # One hot encode categorical features
    daily_df_cat_encoded, daily_df_cat_encoder = one_hot_encode(daily_df, categorical_features)
    hourly_df_cat_encoded, hourly_df_cat_encoder = one_hot_encode(hourly_df, categorical_features)
    for df in [daily_df_cat_encoded, hourly_df_cat_encoded]:
        df.rename(columns=column_names_map, inplace=True)

    # Cyclic encode periodic features
    daily_df_processed = cyclic_encode(daily_df_cat_encoded, periods={"weekday": 7, "mnth": 12}, offsets={"mnth": 1})  # mnth is 1..12 in this dataset
    hourly_df_processed = cyclic_encode(hourly_df_cat_encoded, periods={"hr": 24, "weekday": 7, "mnth": 12}, offsets={"mnth": 1})

    # Save processed data
    daily_df_processed.to_csv(cfg.processed_daily_data_path)
    hourly_df_processed.to_csv(cfg.processed_hourly_data_path)


if __name__ == '__main__':
    main()
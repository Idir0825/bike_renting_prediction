columns_to_drop = ["dteday", "casual", "registered"]

weather_categories = {
    1: "very_good_weather",
    2: "good_weather",
    3: "bad_weather",
    4: "very_bad_weather",
}

season_categories = {
    1: "spring",
    2: "summer",
    3: "fall",
    4: "winter",
}

categorical_features = ["weathersit", "season"]

column_names_map = {f"weathersit_{k}": v for k, v in weather_categories.items()}
column_names_map.update({f"season_{k}": v for k, v in season_categories.items()})
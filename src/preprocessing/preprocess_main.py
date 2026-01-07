import argparse

from extract_features import main as extract
from make_splits import main as split


def main(args: argparse.Namespace):
    extract(args.config_path)
    split(args.splits, args.config_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Data preprocessing")
    parser.add_argument("--splits", nargs=2, type=float, default=[0.85, 0.15],
                        help="How the data should be splitted (train, test) (should sum up to 1)"
                        )
    parser.add_argument("--config_path", type=str, default="configs/data.yaml", help="Path to the data config yaml file")
    arguments = parser.parse_args()

    if sum(arguments.splits) != 1:
        raise ValueError(f"The sum of all splits should equal to 1, got: {sum(arguments.splits)}")

    main(arguments)

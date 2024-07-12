import argparse
from datetime import datetime
from src.browser.library import add_expected_schedule


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=False, help="Fecha en formato YYYY-M-D (Default: today)")
    parser.add_argument("--headless", action="store_true", help="Run browswer in headless mode")
    args = parser.parse_args()
    if args.date:
        args.date = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        args.date = datetime.now()
    return args


if __name__ == "__main__":
    args = parse_args()
    add_expected_schedule(args)

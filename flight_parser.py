
"""Flight Schedule Parser and Query Tool."""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from validator import load_airports
from csv_loader import parse_files
from query import run_queries


STUDENT_ID = "241ADB143"
FIRST_NAME = "RITHWANAHMED"
LAST_NAME = "JABARULLAHKHAN"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flight Schedule Parser and Query Tool"
    )

    source = parser.add_mutually_exclusive_group(required=True)

    source.add_argument("-i", metavar="FILE")
    source.add_argument("-d", metavar="FOLDER")
    source.add_argument("-j", metavar="FILE")

    parser.add_argument("-a", metavar="FILE")
    parser.add_argument("-o", metavar="FILE")
    parser.add_argument("-q", metavar="FILE")
    parser.add_argument("-r", metavar="FOLDER", default=".")

    try:
        args = parser.parse_args(argv)

        if not args.j and not args.a:
            parser.error("-a is required with -i or -d")

        if args.j is not None and args.o is not None:
            parser.error("-o cannot be used with -j")

    except SystemExit as error:
        return error.code

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = None

    try:
        if args.j is not None:
            with open(args.j, "r", encoding="utf-8") as file:
                db = json.load(file)

            if not isinstance(db, list) or not all(
                isinstance(record, dict) for record in db
            ):
                raise ValueError("Invalid database structure")

        else:
            output_path = Path(args.o or "db.json")
            log_path = output_path.parent / "errors.log"

            handler = logging.FileHandler(
                log_path, mode="w", encoding="utf-8"
            )

            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))

            logger.addHandler(handler)

            airports = load_airports(args.a)

            if args.i is not None:
                paths = [args.i]

            else:
                folder = Path(args.d)

                paths = [
                    str(path)
                    for path in sorted(folder.iterdir())
                    if path.is_file() and path.name.endswith(".csv")
                ]

                if not paths:
                    raise ValueError("No CSV files found")

            db, errors = parse_files(paths, airports)

            for error in errors:
                logger.warning(error)

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(db, file, indent=2)

        if args.q is not None:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)

            if not isinstance(queries, dict):
                if not isinstance(queries, list) or not all(
                    isinstance(item, dict) for item in queries
                ):
                    raise ValueError("Invalid query file structure")

            responses = run_queries(db, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            filename = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_"
                f"{LAST_NAME}_{timestamp}.json"
            )

            response_path = Path(args.r) / filename

            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(responses, file, indent=2)

        return 0

    except (OSError, ValueError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())

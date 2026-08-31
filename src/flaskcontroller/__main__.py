"""Main entrypoint, run the app with waitress."""

import argparse
from pathlib import Path

import waitress

from .app import create_app
from .constants import PROGRAM_NAME, PROGRAM_NAME_WITH_FULL_VERSION


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description=PROGRAM_NAME_WITH_FULL_VERSION)
    parser.add_argument("--host", default="127.0.0.1", help="Host to listen on.")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on.")
    parser.add_argument("--instance-path", type=Path, default=None, help="Directory that holds config.json.")
    parser.add_argument("--threads", type=int, default=4, help="Waitress worker threads.")
    return parser.parse_args()


def main() -> None:
    """Main entrypoint."""
    args = _get_args()

    app = create_app(instance_path=args.instance_path)
    waitress.serve(app, host=args.host, port=args.port, threads=args.threads)


if __name__ == "__main__":
    main()  # pragma: no cover

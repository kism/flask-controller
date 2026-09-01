"""Main entrypoint, run the app with uvicorn."""

import argparse
import json
import sys
from pathlib import Path

import uvicorn

from .app import create_app
from .config import Config
from .constants import PROGRAM_NAME, PROGRAM_NAME_WITH_FULL_VERSION


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description=PROGRAM_NAME_WITH_FULL_VERSION)
    parser.add_argument("--host", default="127.0.0.1", help="Host to listen on.")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on.")
    parser.add_argument("--instance-path", type=Path, default=None, help="Directory that holds config.json.")
    parser.add_argument(
        "--dump-openapi",
        action="store_true",
        help="Print the OpenAPI schema to stdout and exit, for `bun run codegen`.",
    )
    return parser.parse_args()


def main() -> None:
    """Main entrypoint."""
    args = _get_args()

    if args.dump_openapi:
        # Default Config() so the instance directory is never touched, and run_socket=False so no thread is started.
        config = Config()
        config.app.run_socket = False
        sys.stdout.write(json.dumps(create_app(config=config).openapi()))
        return

    app = create_app(instance_path=args.instance_path)
    # log_config=None so uvicorn doesn't clobber our logging setup.
    uvicorn.run(app, host=args.host, port=args.port, log_config=None)


if __name__ == "__main__":
    main()  # pragma: no cover

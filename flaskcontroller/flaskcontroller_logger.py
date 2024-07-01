"""Logger functionality for flaskcontroller."""

import logging


def setup_logger(fc_sett: dict | None = None) -> True:
    """APP LOGGING, set config per mca_sett."""
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    if fc_sett and fc_sett.log_level == "DEBUG":
        log.setLevel(logging.DEBUG)

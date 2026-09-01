"""Config loading, validating, writing."""

import logging
from pathlib import (
    Path,  # ruff: ignore[typing-only-standard-library-import] # Cannot be put in type checking block due to pydantic
)
from typing import Self

from pydantic import BaseModel, Field, model_validator

# Logging should be all done at INFO level or higher as the log level hasn't been set yet
logger = logging.getLogger(__name__)

CONFIG_FILE_NAME = "config.json"


class AppConf(BaseModel):
    """Application configuration definition."""

    socket_address: str = "127.0.0.1"
    socket_port: int = 5001
    tick_rate: int = 120  # Inputs per second sent to the emulator, don't flood it.
    run_socket: bool = True  # Set False in tests so no socket thread is started.

    @model_validator(mode="after")
    def tick_rate_positive(self) -> Self:
        """Validate the configuration."""
        if self.tick_rate <= 0:
            msg = "AppConf: tick_rate must be greater than zero"
            raise ValueError(msg)
        return self


class LoggingConf(BaseModel):
    """Logging configuration definition."""

    level: str = "INFO"
    path: Path | None = None


class Config(BaseModel):
    """Settings loaded from a JSON file in the instance directory."""

    app: AppConf = Field(default_factory=AppConf)
    logging: LoggingConf = Field(default_factory=LoggingConf)

    @classmethod
    def load(cls, instance_path: Path) -> Self:
        """Load the config from the instance directory, writing it back with any missing defaults filled in."""
        config_path = instance_path / CONFIG_FILE_NAME
        config = cls.model_validate_json(config_path.read_text()) if config_path.is_file() else cls()

        # ponytail: no backup of the old file, git/your backups can have that job
        instance_path.mkdir(parents=True, exist_ok=True)
        config_path.write_text(config.model_dump_json(indent=2) + "\n")
        logger.info("Config loaded from and written to: %s", config_path)

        return config

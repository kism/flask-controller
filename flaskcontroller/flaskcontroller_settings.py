"""Settings Processing."""

import os
import pwd
import sys

import yaml

DEFAULT_SETTINGS = {
    "log_level": "INFO",
    "socket_address": "127.0.0.1",
    "socket_port": 5001,
    "tick_rate": 120,
}


class FlaskControllerSettings:
    """Object Definition for the settings of the app."""

    def __init__(self) -> None:
        """Initiate settings object, get settings from file."""
        # Load the settings from one of the paths
        self.settings_path = None

        paths = []
        paths.append(os.getcwd() + os.sep + "settings.yml")
        paths.append(os.path.expanduser("~/.config/flaskcontroller/settings.yml"))
        paths.append("/etc/flaskcontroller/settings.yml")

        for path in paths:
            if os.path.exists(path):
                print(
                    f"Found settings at path: {path}",
                )
                if not self.settings_path:
                    print("Using this path as it's the first one that was found")
                    self.settings_path = path
            else:
                print(f"No settings file found at: {path}")

        if not self.settings_path:
            self.settings_path = paths[0]
            print("No configuration file found, creating at default location: %s", self.settings_path)
            self.__write_settings()

        # Load settings file from path
        with open(self.settings_path, encoding="utf8") as yaml_file:
            settings_temp = yaml.safe_load(yaml_file)

        # Set the variables of this object
        for key, default_value in DEFAULT_SETTINGS.items():
            try:
                setattr(self, key, settings_temp[key])
            except (KeyError, TypeError):
                print("%s not defined, using default", key)
                setattr(self, key, default_value)

        self.__write_settings()

        self.__check_settings()

        print("Config looks all good!")

    def __write_settings(self) -> None:
        """Write settings file."""
        try:
            with open(self.settings_path, "w", encoding="utf8") as yaml_file:
                settings_write_temp = vars(self).copy()
                del settings_write_temp["settings_path"]
                yaml.safe_dump(settings_write_temp, yaml_file)
        except PermissionError as exc:
            user_account = pwd.getpwuid(os.getuid())[0]
            err = f"Fix permissions: chown {user_account} {self.settings_path}"
            raise PermissionError(err) from exc

    def __check_settings(self) -> True:
        """Validate Settings."""
        failure = False

        if failure:
            print("Settings validation failed")
            print("Exiting")
            sys.exit(1)

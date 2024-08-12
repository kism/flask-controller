"""Flask webapp flaskcontroller."""

from pprint import pformat

from flask import Flask, render_template

from . import config, controller, logger

__version__ = "0.1.1"

def create_app(test_config: dict | None = None, instance_path: str | None = None) -> Flask:
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)  # Create Flask app object

    logger.setup_logger(app, config.DEFAULT_CONFIG["logging"])  # Setup logger with defaults defined in config module

    if test_config:  # For Python testing we will often pass in a config
        if not instance_path:
            app.logger.critical("When testing supply both test_config and instance_path!")
            raise AttributeError(instance_path)
        fc_conf = config.FlaskControllerConfig(config=test_config, instance_path=app.instance_path)
    else:
        fc_conf = config.FlaskControllerConfig(instance_path=app.instance_path)  # Loads app config from disk

    app.logger.debug("Instance path is: %s", app.instance_path)

    logger.setup_logger(app, fc_conf["logging"])  # Setup logger with config

    # Flask config, at the root of the config object.
    app.config.from_mapping(fc_conf["flask"])

    # Other sections handled by config.py
    for key, value in fc_conf.items():
        if key != "flask":
            app.config[key] = value

    # Do some debug logging of config
    app_config_str = ">>>\nFlask config:"
    for key, value in app.config.items():
        app_config_str += f"\n  {key}: {pformat(value)}"

    app.logger.debug(app_config_str)

    # Register blueprints
    app.register_blueprint(controller.bp)

    # So for modules that need information from the app object we need to start them `with app.app_context():`
    # Since we use `from flask import current_app` in the imported modules to get the config
    with app.app_context():
        controller.start_socket_sender()  # This runs the function that initialises the socket sender

    # Flask homepage, generally don't have this as a blueprint.
    @app.route("/")
    def home() -> str:
        """Flask home."""
        return render_template("home.html.j2")  # Return a webpage

    app.logger.info("Starting Web Server")

    return app

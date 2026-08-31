# Flask to mGBA/Bizhawk Lua

![Check](https://github.com/kism/flask-controller/actions/workflows/check.yml/badge.svg)
![Check](https://github.com/kism/flask-controller/actions/workflows/check_types.yml/badge.svg)
![Test](https://github.com/kism/flask-controller/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/kism/flask-controller/graph/badge.svg?token=9R9ZI99GLP)](https://codecov.io/gh/kism/flask-controller)

Javascript -> HTTP POST -> Flask -> TCP Socket -> mGBA Lua

Javascript -> HTTP POST -> Flask -> TCP Socket -> Bizhawk Lua

Javascript -> HTTP POST -> Flask -> TCP Socket -> Python client that presses keyboard keys

## Prerequisites

Install uv <https://docs.astral.sh/uv/getting-started/installation/>

## Run

### Run Prod

Serves with waitress, config is read from (and created in) `./instance/config.json`.

```bash
uv sync --no-dev
.venv/bin/flaskcontroller --host 127.0.0.1 --port 5000
```

### Run Dev

```bash
uv sync
.venv/bin/flask --app flaskcontroller run --port 5000 --debug
```

### Test

```bash
uv sync --extra test --extra lint --extra type
./scripts/run-ci-local.sh
./scripts/run-coverage.sh
```

## Configuration

`instance/config.json`, written with defaults on first run.

| Key                   | Default       | Description                                        |
| --------------------- | ------------- | -------------------------------------------------- |
| `app.socket_address`  | `127.0.0.1`   | Where the emulator's lua script is listening.       |
| `app.socket_port`     | `5001`        | ditto.                                              |
| `app.tick_rate`       | `120`         | Inputs per second sent to the emulator.             |
| `app.run_socket`      | `true`        | Set false to run the web app without the socket.    |
| `logging.level`       | `INFO`        | Log level.                                          |
| `logging.path`        | `null`        | Log to this file as well as the console.            |
| `flask.DEBUG`         | `false`       | Flask's own config.                                 |
| `flask.TESTING`       | `false`       | ditto.                                              |

## 🎮 mGBA

Tools -> Scripting

File -> Load script

`_emulator/mgba/mgba_grab_web_input.lua`

Client/Server automatically reconnects well.

## 🦅 Bizhawk

Tools -> Lua Console

Script -> Open Script

`_emulator/bizhawk/bizhawk_gba_grab_web_input.lua`

If the python web server exits/closes you will need to reboot the core for it to reconnect, so save in your game and reboot core.

## ⌨️ Generic keyboard client

Instead of an emulator lua script, press real keyboard keys on the machine running the client.

```bash
uv run --extra keyboard _emulator/generic_keyboard/generic_keyboard.py
```

Set `DUMMY_SERVER = False` in that script to actually send key presses.

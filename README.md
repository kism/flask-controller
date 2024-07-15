# Flask to mGBA/Bizhawk Lua

![Check](https://github.com/kism/flaskcontroller/actions/workflows/check.yml/badge.svg)
![Test](https://github.com/kism/flaskcontroller/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/kism/flaskcontroller/graph/badge.svg?token=9R9ZI99GLP)](https://codecov.io/gh/kism/flaskcontroller)

Javascript -> HTTP POST -> Flask -> TCP Socket -> mGBA Lua

Javascript -> HTTP POST -> Flask -> TCP Socket -> Bizhawk Lua

Javascript -> HTTP POST -> Flask -> TCP Socket -> Python Client that presses keyboard keys

## Prerequisites

Install pipx <https://pipx.pypa.io/stable/>

Install poetry with pipx `pipx install poetry`

## Run

### Run Dev

```bash
poetry install
poetry shell
flask --app flaskcontroller run --port 5000
```

### Run Prod

```bash
poetry install --only main
.venv/bin/waitress-serve \
    --listen "127.0.0.1:5000" \
    --trusted-proxy '*' \
    --trusted-proxy-headers 'x-forwarded-for x-forwarded-proto x-forwarded-port' \
    --log-untrusted-proxy-headers \
    --clear-untrusted-proxy-headers \
    --threads 4 \
    --call flaskcontroller:create_app
```

## 🪟 Windows

### 🪟 First time setup

```bash
python -m poetry install
```

### 🪟 Activate environment (optional)

```bash
python -m poetry shell
```

### 🪟 Run App

```bash
python -m poetry run python controller.py
```

Leaving this in for myself

```bash
cd .\src\flaskcontroller\ ; python -m poetry run python controller.py
```

And if you activated the environment

```bash
python controller.py
```

## 🎮 mGBA

Tools -> Scripting

File -> Load script

`flaskcontroller/_emulator/mgba/mgba_grab_web_input.lua`

Client/Server automatically reconnects well.

## 🦅 Bizhawk

Tools -> Lua Console

Script -> Open Script

`flaskcontroller/_emulator/bizhawk/bizhawk_gba_grab_web_input.lua`

If the python web server exits/closes you will need to reboot the core for it to reconnect, so save in your game and reboot core.

# Web Controller

[![Check](https://github.com/kism/flask-controller/actions/workflows/check.yml/badge.svg)](https://github.com/kism/flask-controller/actions/workflows/check.yml)
[![Check](https://github.com/kism/flask-controller/actions/workflows/check_types.yml/badge.svg)](https://github.com/kism/flask-controller/actions/workflows/check_types.yml)
[![CheckFrontend](https://github.com/kism/flask-controller/actions/workflows/check_frontend.yml/badge.svg)](https://github.com/kism/flask-controller/actions/workflows/check_frontend.yml)
[![Test](https://github.com/kism/flask-controller/actions/workflows/test.yml/badge.svg)](https://github.com/kism/flask-controller/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/kism/flask-controller/graph/badge.svg?token=9R9ZI99GLP)](https://codecov.io/gh/kism/flask-controller)

Browser -> HTTP POST -> FastAPI -> TCP Socket -> mGBA Lua

Browser -> HTTP POST -> FastAPI -> TCP Socket -> Bizhawk Lua

Browser -> HTTP POST -> FastAPI -> TCP Socket -> Python client that presses keyboard keys

## Prerequisites

Install uv <https://docs.astral.sh/uv/getting-started/installation/>

Install bun <https://bun.com/docs/installation>, only needed to change the frontend, the built javascript is
committed.

## Run

### Run Prod

Serves with uvicorn, config is read from (and created in) `./instance/config.json`.

```bash
uv sync --no-dev
.venv/bin/webcontroller --host 127.0.0.1 --port 5000
```

### Run Dev

```bash
uv sync
.venv/bin/uvicorn --factory webcontroller:create_app --port 5000 --reload
```

### Test

```bash
uv sync --group test --group lint --group type
./scripts/run-ci-local.sh
./scripts/run-coverage.sh
```

### Test End to End

`tests/test_e2e.py` drives a real browser with Playwright, against a real uvicorn server, wired to a fake GBA
client (a TCP server that records the button bitmasks the app sends). It skips itself unless the `e2e` group is
installed.

```bash
uv sync --group test --group e2e
.venv/bin/playwright install chromium
.venv/bin/pytest
```

## Frontend

The page is rendered server side with Jinja, only the script is TypeScript, bundled with bun. One entrypoint per
template: `frontend/pages/home.ts` builds to `static/home.js`, which `home.html.j2` loads with
`<script type="module">`. The bundle is committed, since the package ships `src/webcontroller/static/` and prod
installs won't have bun.

The api is at `/status` and `/input`, browse it at `/docs`.

```bash
bun install
bun run codegen # Dump the app's OpenAPI schema to frontend/openapi.json, generate frontend/generated/ from it
bun run check   # tsc --noEmit, then biome check, bun build strips types without checking them
bun run fix     # biome check --write, format and autofix
bun run build   # Bundle each frontend/pages/*.ts to src/webcontroller/static/, minified
bun run all     # All three, in order
```

Run `bun run all` after any api change, the typed client in `frontend/generated/` (@hey-api/openapi-ts, configured
in openapi-ts.config.ts) is what makes a renamed endpoint or a new button a compile error instead of an `undefined`
at runtime. `frontend/openapi.json` and `frontend/generated/` are committed too, CI regenerates them and fails on a
diff, so don't hand edit them.

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

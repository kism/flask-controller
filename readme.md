# Flask to mGBA/Bizhawk Lua

Javascript -> HTTP POST -> Flask -> TCP Socket -> mGBA Lua
Javascript -> HTTP POST -> Flask -> TCP Socket -> Bizhawk Lua

## 🐧 Linux

### 🐧 First time setup

Install pipenv for your distro, can install with pip too

```bash
pipenv install
```

### 🐧 Activate environment

```bash
pipenv shell
```

### 🐧 Run App

`python3 controller.py`

`python3 controller.py --help` will show you arguements that you can use.

## 🪟 Windows

### 🪟 First time setup

```bash
python -m pipenv install
```

### 🪟 Activate environment (optional)

```bash
python -m pipenv shell
```

### 🪟 Run App

```bash
python -m pipenv run python controller.py
```

Leaving this in for myself

```bash
cd .\src\flaskcontroller\ ; python -m pipenv run python controller.py
```

And if you activated the environment

```bash
python controller.py
```

## 🎮 mGBA

Tools -> Scripting

File -> Load script

`flaskcontroller/_emulator/mgba/mgba_grabwebinput.lua`

Client/Server automatically reconnects well.

## 🦅 Bizhawk

Tools -> Lua Console

Script -> Open Script

`flaskcontroller/_emulator/bizhawk/bizhawk_gba_grabwebinput.lua`

If the python webserver exits/closes you will need to reboot the core for it to reconnect, so save in your game and reboot core.

## TODO

* ~~get app working with linux uinput~~
* ~~get app working with mgba lua and sockets~~ (much better idea)
* ~~only send valid keys in frontend js~~
* ~~visual feedback in front end~~
* ~~connection status in frontend~~
* ~~clean up lua~~
* ~~separate out vars nicely lua~~
* ~~separate out vars nicely python~~
* ~~up and down press events~~
* ~~buffer (if I cant implement up and down presses)~~
* ~~use dictionaries?~~
* ~~add comments (cringe)~~
* ~~arguments for host and port~~
* ~~connection status for emulator and POST in frontend~~
* ~~create two bytes representing the input in python, send w/socket, use setKeys() with it in lua~~
* ~~buffer failsafe~~
* ~~better readme~~
* ~~add more comments (cringe)~~
* ~~Lua text buffer display for inputs~~
* ~~coloured text for 'player names'~~
* ~~Bizhawk version~~

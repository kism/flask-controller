# Flask to mGBA Lua

Javascript -> HTTP POST -> Flask -> TCP Socket -> mGBA Lua

## Linux

### First time setup

```
pipenv install --dev
```

### Activate environment

```
pipenv shell
```

### Run App

`python3 controller.py`

`python3 controller.py --help` will show you arguements that you can use.

## Windows (needs to be updated for pipenv lol)

### First time setup

```
python.exe -m venv env
& .\env\Scripts\acvivate
pip.exe install -r requirements.txt
```

### Activate environment

```
& .\env\Scripts\acvivate
```

### Run App

`python.exe controller.py`

## Windows

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
* better readme
* add more comments (cringe)
* ~~Lua text buffer display for inputs~~
* ~~coloured text for 'player names'~~

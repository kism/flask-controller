# Flask to MGBA LUA

## Linux

### First time setup Linux

```python -m venv env
pip install -r requirements.txt
```

### Activate environment

```
source env/bin/activate
export FLASK_APP=controller
export FLASK_DEBUG=1
```

### Run App

`./runapp.sh`

## Windows

god knows


## TODO

* only send valid keys in frontend js
* visual feedback in front end
* connection status in frontend
* clean up lua
* up and down press events
* buffer (if I cant implement up and down presses)

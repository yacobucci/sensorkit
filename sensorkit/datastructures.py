import typing

class StateInterface:
    _listeners: dict[str, list[callable]]

    def __init__(self):
        super().__setattr__("_listeners", {})
    
    def add_key_listener(self, key: typing.Any, handler: callable) -> None:
        if key in self._listeners:
            self._listeners[key].append(handler)
        else:
            self._listeners[key] = [ handler ]

class State(StateInterface):
    _state: dict[str, typing.Any]

    def __init__(self, state: dict[str, typing.Any] | None = None):
        super().__init__()
        if state is None:
            state = {}
        super().__setattr__("_state", state)

    def __setattr__(self, key: typing.Any, value: typing.Any) -> None:
        #self._state[key] = value
        self._state.__setattr__(key, value)

        if key in self._listeners:
            for h in self._listeners[key]:
                h(key, value)

    def __getattr__(self, key: typing.Any) -> typing.Any:
        try:
            return self._state.__getattr__(key)
        except (KeyError, AttributeError):
            message = "'{}' object has no attribute '{}'"
            raise AttributeError(message.format(self.__class__.__name__, key))

    def __delattr__(self, key: typing.Any) -> None:
        del self._state[key]

        if key in self._listeners:
            for h in self._listeners[key]:
                h(key, None)

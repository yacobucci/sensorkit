import typing

class Store:
    _store: dict[str, typing.Any]
    _listeners: dict[str, list[callable]]

    def __init__(self, state: dict[str, typing.Any] | None = None):
        if state is None:
            state = {}
        super().__setattr__("_store", state)
        super().__setattr__("_listeners", {})

    def __setattr__(self, key: typing.Any, value: typing.Any) -> None:
        self._store.__setattr__(key, value)

        if key in self._listeners:
            for h in self._listeners[key]:
                h(key, value)

    def __getattr__(self, key: typing.Any) -> typing.Any:
        try:
            return self._store.__getattr__(key)
        except (KeyError, AttributeError):
            message = "'{}' object has no attribute '{}'"
            raise AttributeError(message.format(self.__class__.__name__, key))

    def __delattr__(self, key: typing.Any) -> None:
        del self._store[key]

        if key in self._listeners:
            for h in self._listeners[key]:
                h(key, None)

    def add_key_listener(self, key: typing.Any, handler: callable) -> None:
        if key in self._listeners:
            self._listeners[key].append(handler)
        else:
            self._listeners[key] = [ handler ]

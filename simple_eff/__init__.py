from typing import Any

__version__ = '0.0.1'

class SimpleEffError(RuntimeError):
    pass


class EffectNotHandledError(SimpleEffError):
    pass


class InvalidEffectError(SimpleEffError):
    pass


class _Eff:
    __match_args__ = (
        "id",
        "args",
    )

    def __init__(self, id: int, args):
        self.id = id
        self.args = args


class Effect:
    def __init__(self):
        self.id = id(self)

    def perform(self, v):
        return _Eff(self.id, v)


class Handler:
    class Store:
        def __init__(self):
            self.handlers = {}

        def set(self, r, e):
            self.handlers[r.id] = e

        def get(self, eff):
            return self.handlers[eff.id]

        def get_by_id(self, id: int):
            return self.handlers[id]

        def exists(self, id: int):
            return id in self.handlers

    def __init__(self, vh = lambda x: x):
        self.handlers = self.Store()
        self.value_handler = vh

    def on(self, eff, fun):
        self.handlers.set(eff, fun)
        return self

    def run(self, func, args):
        return self._continue(func(args))(None)

    def _continue(self, co):
        def handle(args):
            try:
                return next(self._handle(co, co.send(args)))
            except StopIteration as e:
                return self.value_handler(e.value)

        return handle

    def _handle(self, co, r):
        match r:
            case _Eff(id, args):
                if self.handlers.exists(id):
                    handler = self.handlers.get_by_id(id)
                    ret = handler(self._continue(co), args)
                    yield ret
                raise EffectNotHandledError()
            case _:
                raise InvalidEffectError()


def eff(func):
    def wrapper(*args,**kwargs):
        class Wrapper:
            def __init__(self):
                self.handler = Handler()
            def on(self, e, h):
                self.handler.on(e, h)
                return self
            def run(self):
                return self.handler.run(func, *args, **kwargs)
        return Wrapper()
    return wrapper

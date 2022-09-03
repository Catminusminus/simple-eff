from typing import Any, Callable, Dict, Generator, TypeVar, Generic

__version__ = "0.0.1a3"


class SimpleEffError(RuntimeError):
    pass


class EffectNotHandledError(SimpleEffError):
    pass


class InvalidEffectError(SimpleEffError):
    pass


_T = TypeVar("_T")


class _Eff(Generic[_T]):
    __match_args__ = (
        "id",
        "args",
    )

    def __init__(self, id: int, args: _T) -> None:
        self.id = id
        self.args = args


Eff = _Eff


class Effect:
    def __init__(self) -> None:
        self.id = id(self)

    def perform(self, v: _T) -> _Eff[_T]:
        return _Eff(self.id, v)


_ARG = TypeVar("_ARG")
_EFFARG = TypeVar("_EFFARG")
_SEND = TypeVar("_SEND")
_RET = TypeVar("_RET")


class Handler:
    class Store:
        handlers: Dict[int, Callable]

        def __init__(self) -> None:
            self.handlers = {}

        def set(self, r: Effect, e: Callable) -> None:
            self.handlers[r.id] = e

        def get(self, eff: _Eff) -> Any:
            return self.handlers[eff.id]

        def get_by_id(self, id: int) -> Callable:
            return self.handlers[id]

        def exists(self, id: int) -> bool:
            return id in self.handlers

    def __init__(self, vh: Callable[[Any], _RET] = lambda x: x) -> None:
        self.handlers = self.Store()
        self.value_handler = vh

    def on(self, eff: Effect, fun: Callable) -> "Handler":
        self.handlers.set(eff, fun)
        return self

    def run(
        self, func: Callable[[_ARG], Generator[_EFFARG, _SEND, _RET]], args: _ARG
    ) -> _RET:
        return self._continue(func(args))(None)

    def _continue(self, co: Generator):
        def handle(args: Any):
            try:
                return next(self._handle(co, co.send(args)))
            except StopIteration as e:
                return self.value_handler(e.value)

        return handle

    def _handle(self, co: Generator, r: Any):
        match r:
            case _Eff(id, args):
                if self.handlers.exists(id):
                    handler = self.handlers.get_by_id(id)
                    ret = handler(self._continue(co), args)
                    yield ret
                raise EffectNotHandledError()
            case _:
                raise InvalidEffectError()


def eff(func: Callable[[_ARG], Generator[_EFFARG, _SEND, _RET]]):
    def wrapper(*args, **kwargs):
        class Wrapper:
            def __init__(self) -> None:
                self.handler = Handler()

            def on(self, e: Effect, h: Callable) -> "Wrapper":
                self.handler.on(e, h)
                return self

            def run(self) -> _RET:
                return self.handler.run(func, *args, **kwargs)

        return Wrapper()

    return wrapper

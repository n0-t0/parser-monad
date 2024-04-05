from typing import Callable
import dataclasses
import functools

@dataclasses.dataclass(frozen=True)
class Left[L]:
    value: L

@dataclasses.dataclass(frozen=True)
class Right[R]:
    value: R

@dataclasses.dataclass(frozen=True)
class Either[L, R]:
    value: Left[L] | Right[R]

    def fmap[XR](self, f: Callable[[R], XR]) -> "Either[L, XR]":
        match self.value:
            case Left(v):
                return Either(Left(v))
            case Right(v):
                return Either(Right(f(v)))

    def bind[XR](self, f: Callable[[R], "Either[L, XR]"]) -> "Either[L, XR]":
        match self.value:
            case Left(v):
                return Either(Left(v))
            case Right(v):
                return f(v)

    def unsafe_get(self) -> Right[R]:
        match self.value:
            case Left(_):
                raise ValueError("Left value")
            case Right(_):
                return self.value

    @staticmethod
    def right(v: R) -> "Either[L, R]":
        return Either(Right(v))

    @staticmethod
    def left(v: L) -> "Either[L, R]":
        return Either(Left(v))

def either_monad(comrehension):
    @functools.wraps(comrehension)
    def computation(*args, **kargs):
        gen = comrehension(*args, **kargs)
        result = next(gen)  # do one computation
        try:
            while True:
                match result.value:
                    case Left(_):
                        return result
                    case Right(v):
                        result = gen.send(v)
                    case _:
                        raise ValueError("Invalid value")
        except StopIteration as e:
            return Either.right(e.value)
    return computation

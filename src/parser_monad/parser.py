from abc import ABC, abstractmethod
from typing import Callable, override, cast, Generator, Any
import functools
import either

class Parser[A](ABC):
    @abstractmethod
    def parse(self, s: str) -> either.Either[str, tuple[A, str]]:
        ...

    @staticmethod
    def fail(message: str) -> "Parser[A]":
        class FailParser(Parser[A]):
            @override
            def parse(self, s: str) -> either.Either[str, tuple[A, str]]:
                return either.Either.left(message)
        return FailParser()

    def bind[B](self, f: Callable[[A], "Parser[B]"]) -> "Parser[B]":
        outer_self = self  # Parser[A] instance
        class BindParser(Parser[B]):
            @override
            def parse(self, s: str) -> either.Either[str, tuple[B, str]]:
                return outer_self.parse(s).bind(lambda x: f(x[0]).parse(x[1]))
        return BindParser()

    def fmap[B](self, f: Callable[[A], B]) -> "Parser[B]":
        outer_self = self  # Parser[A] instance
        class MapParser(Parser[B]):
            @override
            def parse(self, s: str) -> either.Either[str, tuple[B, str]]:
                return outer_self.parse(s).fmap(lambda x: (f(x[0]), x[1]))
        return MapParser()

    def apply[B](self, f: "Parser[Callable[[A], B]]") -> "Parser[B]":
        outer_self = self  # Parser[A] instance
        class ApplyParser(Parser[B]):
            @override
            def parse(self, s: str) -> either.Either[str, tuple[Y, str]]:
                return outer_self.bind(lambda a: f.fmap(lambda x: x(a))).parse(s)
        return ApplyParser()

    def with_filter(self, f: Callable[[A], bool], message: str) -> "Parser[A]":
        outer_self = self  # Parser[A] instance
        class WithFilterParser(Parser[A]):
            @override
            def parse(self, s: str) -> either.Either[str, tuple[A, str]]:
                return outer_self.parse(s).bind(
                    lambda x: either.Either.right(x) if f(x[0]) else either.Either.left(message)
                )
        return WithFilterParser()


class ParserHelper:
    @staticmethod
    def pure[A](a: A) -> Parser[A]:
        class PureParser(Parser[A]):
            @override
            def parse(self, s: str) -> either.Either[str, tuple[A, str]]:
                return either.Either.right((a, s))
        return PureParser()

    @staticmethod
    def either[A, B](p: Parser[A], q: Parser[B]) -> Parser[A | B]:
        class EitherParser(Parser[A | B]):
            @override
            def parse(self, s: str) -> either.Either[str, tuple[A | B, str]]:
                result = p.parse(s)
                match result.value:
                    case either.Left(_):
                        return cast(either.Either[str, tuple[A | B, str]], q.parse(s))
                    case either.Right(_):
                        return cast(either.Either[str, tuple[A | B, str]], result)
        return EitherParser()

    @staticmethod
    def combineLeft[A, B](p: Parser[A], q: Parser[B]) -> Parser[A]:
        class CombineLeftParser(Parser[A]):
            @override
            def parse(self, s: str) -> either.Either[str, tuple[A, str]]:
                return p.apply(q.fmap(lambda b: (lambda a: a))).parse(s)
        return CombineLeftParser()

    @staticmethod
    def combineRight[A, B](p: Parser[A], q: Parser[B]) -> Parser[B]:
        class CombineRightParser(Parser[B]):
            @override
            def parse(self, s: str) -> either.Either[str, tuple[B, str]]:
                return p.apply(q.fmap(lambda b: (lambda a: b))).parse(s)
        return CombineRightParser()

    @staticmethod
    def some[A](p: Parser[A]) -> Parser[list[A]]:
        return p.bind(
            lambda x: ParserHelper.many(p).bind(
                lambda xs: ParserHelper.pure([x] + xs)
            )
        )

    @staticmethod
    def many[A](p: Parser[A]) -> Parser[list[A]]:
        return ParserHelper.either(
            ParserHelper.some(p),
            ParserHelper.pure([])
        )

def parser_monad[R](comprehension: Callable[..., Generator[Any, None, R]]) -> Callable[..., Parser[R]]:
    @functools.wraps(comprehension)
    def computation(*args, **kargs) -> Parser[R]:
        class CombinedParser(Parser[R]):
            def parse(self, s: str) -> either.Either[str, tuple[R, str]]:
                iter = comprehension(*args, **kargs)
                res_s = s
                try:
                    result_parser: Parser = next(iter)
                    while True:
                        result = result_parser.parse(res_s)
                        # print(result.value)
                        match result.value:
                            case either.Left(_):
                                return result
                            case either.Right(v):
                                parsed_value, res_s = v
                                result_parser = iter.send(parsed_value)
                except StopIteration as e:
                    return either.Either.right((e.value, res_s))
        return CombinedParser()
    return computation

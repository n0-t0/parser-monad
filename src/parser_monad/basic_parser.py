from typing import Callable
import either
import parser

class BasicParser:
    @staticmethod
    def peek() -> parser.Parser[str]:
        class PeekParser(parser.Parser[str]):
            def parse(self, s: str) -> either.Either[str, tuple[str, str]]:
                either.Either.right((s, s))
        return PeekParser()

    @staticmethod
    def oneChar() -> parser.Parser[str]:
        class OneCharparser(parser.Parser[str]):
            def parse(self, s: str) -> either.Either[str, tuple[str, str]]:
                if s:
                    return either.Either.right((s[0], s[1:]))
                else:
                    return either.Either.left("s is empty")
        return OneCharparser()

    @staticmethod
    def satisfy(f: Callable[[str], bool], message: str) -> parser.Parser[str]:
        return BasicParser.oneChar().with_filter(f, message)

    @staticmethod
    def char(c: str) -> parser.Parser[str]:
        return BasicParser.satisfy(lambda x: x == c, f"expect {c}")

    @staticmethod
    def prefix(s: str) -> parser.Parser[str]:
        class PrefixParser(parser.Parser[str]):
            def parse(self, s: str) -> either.Either[str, tuple[str, str]]:
                if s.startswith(s):
                    return either.Either.right((s, s[len(s) :]))
                else:
                    return either.Either.left(f"expect {s}")
        return PrefixParser()

    @staticmethod
    def postfix(s: str) -> parser.Parser[str]:
        class PostfixParser(parser.Parser[str]):
            def parse(self, s: str) -> either.Either[str, tuple[str, str]]:
                if s.endswith(s):
                    return either.Either.right((s, s[: -len(s)]))
                else:
                    return either.Either.left(f"expect {s}")
        return PostfixParser()


    @staticmethod
    def space() -> parser.Parser[str]:
        return BasicParser.satisfy(str.isspace, "expect space")

    @staticmethod
    @parser.parser_monad
    def token[X](p: parser.Parser[X]) -> parser.Parser[X]:
        _ = yield parser.ParserHelper.many(BasicParser.space())
        v = yield p
        _ = yield parser.ParserHelper.many(BasicParser.space())
        return v

    @staticmethod
    @parser.parser_monad
    def commaAndValue[X](p: parser.Parser[X]) -> parser.Parser[X]:
        _ = yield BasicParser.token(BasicParser.char(","))
        v = yield BasicParser.token(p)
        return v

    @staticmethod
    @parser.parser_monad
    def commaSeparated[X](p: parser.Parser[X]) -> parser.Parser[list[X]]:
        v = yield p
        vs = yield parser.ParserHelper.many(
            BasicParser.commaAndValue(p)
        )
        return [v] + vs

    @staticmethod
    @parser.parser_monad
    def nonEmptyList[X](p: parser.Parser[X]) -> parser.Parser[list[X]]:
        _ = yield BasicParser.token(BasicParser.char("["))
        v = yield BasicParser.commaSeparated(p)
        _ = yield BasicParser.token(BasicParser.char("]"))
        return v

    @staticmethod
    @parser.parser_monad
    def emptyList[X]() -> parser.Parser[list[X]]:
        _ = yield BasicParser.token(BasicParser.char("["))
        _ = yield BasicParser.token(BasicParser.char("]"))
        return []

    @staticmethod
    @parser.parser_monad
    def list_literal[X](p: parser.Parser[X]) -> parser.Parser[list[X]]:
        v = yield parser.ParserHelper.either.Either(
            BasicParser.nonEmptyList(p), BasicParser.emptyList()
        )
        return v

    @staticmethod
    @parser.parser_monad
    def between[X, Y, Z](open: parser.Parser[X], p: parser.Parser[Y], close: parser.Parser[Z]) -> parser.Parser[Y]:
        _ = yield BasicParser.token(open)
        v = yield p
        _ = yield BasicParser.token(close)
        return v

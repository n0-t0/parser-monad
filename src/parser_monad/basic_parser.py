from typing import Callable
import either
import parser

class BasicParser:
    @staticmethod
    def peek() -> parser.Parser[str]:
        class PeekParser(parser.Parser[str]):
            def parse(self, s: str) -> either.Either[str, tuple[str, str]]:
                return either.Either.right((s, s))
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
    def space() -> parser.Parser[str]:
        return BasicParser.satisfy(str.isspace, "expect space")

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
    @parser.parser_monad
    def token[X](p: parser.Parser[X]):
        _ = yield parser.ParserHelper.many(BasicParser.space())
        v = yield p
        _ = yield parser.ParserHelper.many(BasicParser.space())
        return v

    @staticmethod
    @parser.parser_monad
    def commaAndValue[X](p: parser.Parser[X]):
        _ = yield BasicParser.token(BasicParser.char(","))
        v = yield BasicParser.token(p)
        return v

    @staticmethod
    @parser.parser_monad
    def commaSeparated[X](p: parser.Parser[X]):
        v = yield p
        vs = yield parser.ParserHelper.many(
            BasicParser.commaAndValue(p)
        )
        return [v] + vs

    @staticmethod
    @parser.parser_monad
    def nonEmptyList[X](p: parser.Parser[X]):
        _ = yield BasicParser.token(BasicParser.char("["))
        v = yield BasicParser.commaSeparated(p)
        _ = yield BasicParser.token(BasicParser.char("]"))
        return v

    @staticmethod
    @parser.parser_monad
    def emptyList[X]():
        _ = yield BasicParser.token(BasicParser.char("["))
        _ = yield BasicParser.token(BasicParser.char("]"))
        return []

    @staticmethod
    @parser.parser_monad
    def list_literal[X](p: parser.Parser[X]):
        v = yield parser.ParserHelper.either(
            BasicParser.nonEmptyList(p), BasicParser.emptyList()
        )
        return v

    @staticmethod
    def letter() -> parser.Parser[str]:
        return BasicParser.satisfy(str.isalpha, "expect letter")

    @staticmethod
    def digit() -> parser.Parser[str]:
        return BasicParser.satisfy(str.isdigit, "expect digit")

    @staticmethod
    @parser.parser_monad
    def int_number():
        v = yield parser.ParserHelper.some(BasicParser.digit())
        return int("".join(v))

    @staticmethod
    @parser.parser_monad
    def float_number():
        v1 = yield parser.ParserHelper.some(BasicParser.digit())
        _ = yield BasicParser.token(BasicParser.char("."))
        v2 = yield parser.ParserHelper.some(BasicParser.digit())
        return float("".join(v1) + "." + "".join(v2))

    @staticmethod
    @parser.parser_monad
    def stringWithout(s: str):
        # s must be a char
        if len(s) != 1:
            _ = yield parser.Parser.fail("expect a char")
            return either.Left("expect a char")
        else:
            v = yield parser.ParserHelper.many(
                BasicParser.satisfy(lambda x: x != s, f"expect not {s}")
            )
            return "".join(v)

    @staticmethod
    @parser.parser_monad
    def stringWithouts(ls: list[str]):
        for s in ls:
            if len(s) != 1:
                _ = yield parser.Parser.fail("expect a char")
                return either.Left("expect a char")

        v = yield parser.ParserHelper.many(
            BasicParser.satisfy(lambda x: x in ls, f"expect not {ls}")
        )
        return "".join(v)

    @staticmethod
    @parser.parser_monad
    def line():
        v = yield BasicParser.stringWithout("\n")
        return "".join(v)

    @staticmethod
    @parser.parser_monad
    def nextLine():
        _ = yield BasicParser.char("\n")
        line = yield BasicParser.line()
        return line

    @staticmethod
    @parser.parser_monad
    def eof():
        v = yield BasicParser.peek()
        if v == "" or v == "\n":
            return v
        else:
            _ = yield parser.Parser.fail("expect eof")
            return either.Left("expect eof")

    @staticmethod
    @parser.parser_monad
    def lines():
        first_line = yield BasicParser.line()
        next_lines = yield parser.ParserHelper.either(
            parser.ParserHelper.many(BasicParser.nextLine()),
            BasicParser.eof(),
        )
        all_lines = [first_line] + next_lines
        return [line.rstrip('\r\n') for line in all_lines if line != ""]

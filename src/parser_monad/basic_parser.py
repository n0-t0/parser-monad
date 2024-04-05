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

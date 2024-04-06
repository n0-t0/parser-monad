from dataclasses import dataclass
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from parser import Parser, ParserHelper, parser_monad
from basic_parser import BasicParser


@dataclass(frozen=True)
class Header:
    id: str
    description: str | None

@dataclass(frozen=True)
class Sequence:
    seq: str

@dataclass(frozen=True)
class FastaRecord:
    header: Header
    sequence: Sequence

@dataclass(frozen=True)
class Fasta:
    records: list[FastaRecord]

class FastaParser:
    @staticmethod
    @parser_monad
    def header():
        _ = yield BasicParser.token(BasicParser.char(">"))
        id = yield BasicParser.stringWithout(" ")
        description = yield BasicParser.line()
        return Header(id, description.strip())

    @staticmethod
    @parser_monad
    def sequence():
        seq_parts = yield BasicParser.stringWithout(">")
        return Sequence(seq_parts.replace("\n", "").replace("\r", ""))

    @staticmethod
    @parser_monad
    def fasta_record():
        header = yield FastaParser.header()
        sequence = yield FastaParser.sequence()
        return FastaRecord(header, sequence)

    @staticmethod
    @parser_monad
    def fasta():
        first_record = yield FastaParser.fasta_record()
        records = yield ParserHelper.many(FastaParser.fasta_record())
        return Fasta([first_record] + records)

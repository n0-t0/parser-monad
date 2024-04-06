import os
import sys
from parser_monad.fasta_parser import FastaParser, Fasta
from parser_monad.either import Left, Right, Either

def read_fasta_file(file_path: str):
    with open(file_path, 'r') as file:
        file_content = file.read()
        fasta_parser = FastaParser.fasta()
        parse_result = fasta_parser.parse(file_content)
        return parse_result

fasta_file_path = 'resource/example.fasta'
fasta_data = read_fasta_file(fasta_file_path)
print(fasta_data)

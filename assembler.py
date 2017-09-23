#!/usr/bin/env python

import collections

PREDEFINED_MEM = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,
}

DEST = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
}

JUMP = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

COMP = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101",
}


class Parser():
    def __init__(self, filename):
        free_addresses = iter(range(16, PREDEFINED_MEM['SCREEN']-1))
        self.variables = collections.defaultdict(free_addresses.__next__)
        self.labels = dict()

        with open(filename) as f:
            self.lines = self.preprocess(f)

    def preprocess(self, file):
        lines = []
        for line in file:
            clean_line = line.split("//")[0].strip()
            if clean_line.startswith("("):  # is a label
                label_name = clean_line[1:-1]
                self.labels[label_name] = len(lines)  # line number
            elif clean_line:
                lines.append(clean_line)
            else:  # it's just a whitespace/comment line
                pass
        return lines

    def resolve_symbol(self, symbol):
        if symbol in self.labels:
            return self.labels[symbol]
        if symbol in PREDEFINED_MEM:
            return PREDEFINED_MEM[symbol]
        else:
            return self.variables[symbol]  # autoincrement default

    def assemble_line(self, line):
        if line.startswith("@"):
            return AInstruction(line, parser=self)
        else:
            return CInstruction(line)

    def assemble_binary(self):
        return map(self.assemble_line, self.lines)


class AInstruction():
    def __init__(self, code, parser):
        target = code[1:]
        try:
            self.address = int(target)
        except ValueError:
            self.address = parser.resolve_symbol(target)

    def __str__(self):
        return "0{:0>15b}".format(self.address)


class CInstruction():
    def __init__(self, code):
        self.dest, rest = code.split("=") if "=" in code else ("", code)
        self.comp, self.jump = rest.split(";") if ";" in rest else (rest, "")

    def __str__(self):
        return "111{}{}{}".format(COMP[self.comp], DEST[self.dest],
                                  JUMP[self.jump])


if __name__ == "__main__":
    binary_ops = Parser("Pong.asm").assemble_binary()
    for op in binary_ops:
        print(op)

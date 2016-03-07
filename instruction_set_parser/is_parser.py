import re
from collections import namedtuple

Instruction = namedtuple('Instruction', ('opcode', 'size', 'name'))


class ProcessorArchitecture:
    WORD_SIZE = 8
    INSTRUCTION_SET = []

    def __init__(self):
        self.WORD_SIZE = 8
        self.INSTRUCTION_SET = []


class ParserError(Exception):
    """Specifies an error that occurred while parsing the Instruction Set file"""

    line_number = 0
    error_id = 0
    error_msg = 'An error occurred during the parsing process.'
    context = ''

    def __init__(self, error_id, error_msg):
        self.error_id = error_id
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg

    def print_err(self, ln, ctx):
        print('PREPROCESSOR ERROR {} on line {}: {}\n\t--> {}'.format(self.error_id, ln, self.error_msg, ctx))

    def print_warn(self, ln, ctx):
        print('PREPROCESSOR WARNING {} on line {}: {}\n\t--> {}'.format(self.error_id, ln, self.error_msg, ctx))

    def print_raise(self, ln, ctx):
        self.print_err(ln, ctx)
        raise self

PARSER_ERR_INVALID_FILE = ParserError(1, 'Could not read the input file.')
PARSER_ERR_INVALID_SYNTAX = ParserError(2, 'Invalid syntax. (Bad keyword or argument misuse?)')
PARSER_ERR_DUPLICATE_OPCODE = ParserError(3, 'Duplicate OpCode; an instruction with the same OpCode is already defined.')


class InstructionSetParser:

    @classmethod
    def _keyword_WORD_SIZE(cls, pa, args, ln, line):
        # WORD_SIZE(size)
        assert(len(args) == 1)

        # Set the word size to the first argument, which should be a base-10 integer.
        pa.WORD_SIZE = int(args[0])

    @classmethod
    def _keyword_INSTRUCTION(cls, pa, args, ln, line):
        # INSTRUCTION(opcode, size, syntax)
        assert(len(args) == 3)

        opcode = int(args[0])
        size = int(args[1])
        syntax = args[2]

        # Check that an instruction with the same opcode wasn't added
        for instr in pa.INSTRUCTION_SET:
            if instr.opcode == opcode:
                PARSER_ERR_DUPLICATE_OPCODE.print_raise(ln, line)

        # Create an Instruction and add it to the Instruction Set of our PA
        pa.INSTRUCTION_SET.append(Instruction(opcode, size, syntax))

    KEYWORD_REGEXPS = [
        # WORD_SIZE(8)
        r'^\s*(WORD_SIZE)\s*\(\s*(\d+)\s*\)\s*$',
        # INSTRUCTION(0, 1, 'FOO')
        r'^\s*(INSTRUCTION)\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*\'(.+)\'\s*\)\s*$'
    ]

    KEYWORD_BEHAVIOR = {
        'WORD_SIZE': _keyword_WORD_SIZE,
        'INSTRUCTION': _keyword_INSTRUCTION
    }

    @classmethod
    def _replace_numerals(cls, line):
        """Replaces any hexadecimal or binary numeral to decimal"""

        # Find and convert any numeral to decimal
        hex_numerals = [m.span() for m in re.finditer(r'(0[xX][0-9a-fA-F]+)', line)]
        bin_numerals = [m.span() for m in re.finditer(r'(0[bB][0-1]+)', line)]

        i = 0
        offset = 0
        for span in (hex_numerals + bin_numerals):
            # Remove the matched numeral and replace it with its decimal representation
            # (Also, since 'line' is modified in-place, add the offset produced by the conversions to the span)
            span = (span[0] + offset, span[1] + offset)

            numeral = line[span[0]:span[1]]
            numeral = int(numeral, 16 if i < len(hex_numerals) else 2)

            # Offset = old_len - new_len, so Offset = -new_len + old_len
            offset = len(line)
            line = line[:span[0]] + str(numeral) + line[span[1]:]
            offset = -offset + len(line)

            i += 1
        return line

    @classmethod
    def _parse_line(cls, ln, line, pa):
        """Parses a single line and modifies the ProcessorArchitecture or raises an InvalidSyntax error"""
        keyword_found = False
        for regexp in cls.KEYWORD_REGEXPS:
            match = re.match(regexp, line, re.IGNORECASE)
            if match is None:
                continue
            # If at least one keyword (with correct usage) was matched, set the keyword_found flag
            keyword_found = True
            # We can then use it to index the KEYWORD_BEHAVIOR dictionary and call the required code
            keyword = match.group(1).upper()
            cls.KEYWORD_BEHAVIOR[keyword].__func__(cls, pa, match.groups()[1:], ln, line)
            # And finally we can safely break out of the loop since only one keyword is allowed per line
            break

        # If this flag is not set, no keyword was matched and this line is thus invalid
        if not keyword_found:
            PARSER_ERR_INVALID_SYNTAX.print_raise(ln, line)

    @classmethod
    def parse_file(cls, file):
        """Parses an Instruction Set file and returns a ProcessorArchitecture instance
        :param file: The file to parse.
        """

        lines = []

        # If something that can be read has been passed, use it
        if hasattr(file, 'read'):
                lines = file.read().split('\n')
        # Otherwise assume that file is a filename
        else:
            try:
                with open(file, 'r') as fin:
                    lines = fin.read().split('\n')
            except FileNotFoundError:
                PARSER_ERR_INVALID_FILE.print_raise(-1, '')

        # Remove empty lines
        lines = [line for line in lines if len(line.strip()) > 0]

        # Create a ProcessorArchitecture structure, which is what this parser ultimately outputs
        pa = ProcessorArchitecture()

        # Begin the parsing process
        ln = 0  # Line number
        for cur_line in lines:
            # Convert any non-decimal literal (0xFF -> 255, 0b10 -> 2)
            cur_line = cls._replace_numerals(cur_line)
            # Parse the current line
            cls._parse_line(ln, cur_line, pa)
            ln += 1

        # If everything went fine, return the ProcessorArchitecture object
        return pa

import re
from instruction_set_parser import is_parser


class CompilerError(Exception):
    """Specifies an error that occurred while compiling the source file"""

    line_number = 0
    error_id = 0
    error_msg = 'An error occurred during the compiling process.'
    context = ''

    def __init__(self, error_id, error_msg):
        self.error_id = error_id
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg

    def print_err(self, ln, ctx):
        print('COMPILER ERROR {} on line {}: {}\n\t--> {}'.format(self.error_id, ln, self.error_msg, ctx))

    def print_warn(self, ln, ctx):
        print('COMPILER WARNING {} on line {}: {}\n\t--> {}'.format(self.error_id, ln, self.error_msg, ctx))

    def print_exit(self, ln, ctx):
        self.print_err(ln, ctx)
        exit(self.error_id)


COMPILER_ERR_INVALID_FILE = CompilerError(1, 'Could not read the input file.')
COMPILER_ERR_MISSING_SYMBOL = CompilerError(2, 'Expected variable, number or label but got nothing instead.')
COMPILER_ERR_UNDEFINED_INSTRUCTION = CompilerError(3, 'Undefined instruction signature.')
COMPILER_ERR_UNCOMPILABLE_INSTRUCTION = CompilerError(4, 'The expected instruction size (in WORDs) '
                                                         'and the actual instruction size differ')
COMPILER_WARN_NO_OUTPUT = CompilerError(101, 'No output filename specified or no output flags set. Won\'t do anything.')


class Compiler:

    @classmethod
    def _tokenize_line(cls, line):
        # Note: Please don't try to understand it. One victim is enough already. Just know that it works.
        regexp = r'^(?P<instruction>\w+)(?:\s+(?P<arg1>\.?[a-zA-Z0-9]+)' \
                 r'(?P<extraargs>(?:\s*,\s*\(?\s*[a-zA-Z0-9]+\s*\)?\s*)*))?$'
        # Examples covered by this regex:
        # LD A, B
        # LD A,B
        # LD A, .label
        # LD A, 0
        # CPLX A, 1,   2  , B
        # And many more (see tests/compiler_tests.py)
        match = re.match(regexp, line)
        if match is None:
            # Something in the syntax was wrong, such as a literal not being provided
            # The parse_file method will raise an exception, but this one is private and it should be silent.
            return None

        instr = match.group('instruction')
        arg1 = match.group('arg1')
        if arg1 is not None:
            args = [arg1] + match.group('extraargs').split(',')
            args = [arg.strip() for arg in args if len(arg.strip()) > 0]
        else:
            args = []

        return {'name': instr, 'args': args}

    @classmethod
    def _tokenize_instruction(cls, instr):
        # An instruction's name will contain some magic words, such as:
        # $literal: A numeric constant.
        # $address: A label name.
        # But a line will only contain actual values, and parsing must first be done.

        # Note: This is blasphemy! This is madness!
        #       Madness...
        #       ...
        regexp = r'^(?P<instruction>\w+)(?:\s(?P<arg1>\(?(?:[a-zA-Z]+|\$address|\$literal)\)?)' \
                 r'(?P<extraargs>(?:,[\s_]?\(?(?:[a-zA-Z]+|\$address|\$literal)\)?\s*)*))?$'

        match = re.match(regexp, instr.name)

        if match is None:
            # Ouch. The parser did a good job, but there are syntax errors.
            return None

        instr = match.group('instruction')
        arg1 = match.group('arg1')
        if arg1 is not None:
            args = [arg1] + match.group('extraargs').split(',')
            args = [arg.replace('_', ' ').strip() for arg in args if len(arg.replace('_', ' ').strip()) > 0]
        else:
            args = []

        return {'name': instr, 'args': args}

    @classmethod
    def _find_matching_instruction(cls, pa, tokens):
        matching_instr = None
        best_score = -1  # The number of arguments that are the same
        for instr in pa.INSTRUCTION_SET:
            # instr.name is actually the whole human-readable instruction with some special keywords in it
            # So it must be tokenized as well
            instr_tokens = cls._tokenize_instruction(instr)
            # Find the best match for this instruction
            if instr_tokens['name'] == tokens['name'] and len(instr_tokens['args']) == len(tokens['args']):
                score = 0
                for i in range(0, len(tokens['args'])):
                    score += 1 if tokens['args'][i] == instr_tokens['args'][i] else 0
                    i += 1

                if score > best_score:
                    best_score = score
                    matching_instr = instr

        return matching_instr

    @classmethod
    def _is_literal(cls, arg):
        try:
            return int(arg) is not None
        except ValueError:
            return False

    @classmethod
    def _encode_instruction(cls, signature, args):
        encoded_instr = [signature.opcode]

        if len(args) > 0:
            # Skip non-literals since they can't be encoded and are assumed to be part of the opcode
            for i, arg in enumerate(args):
                if cls._is_literal(arg):
                    encoded_instr.append(int(arg))

        if len(encoded_instr) != signature.size:
            return None

        return encoded_instr

    @classmethod
    def _binary_to_ascii(cls, obj, word_size):
        str_out = ''
        for byte in obj:
            str_out += '{0:b}'.format(byte).zfill(word_size) + '\n'
        return str_out

    @classmethod
    def _calculate_offset(cls, program, until):
        offset = 0
        for i in range(0, until):
            offset += program[i]['instruction'].size - 1
        return offset

    @classmethod
    def _adjust_addresses(cls, call, program):
        # Tokenize the instruction
        instr_tokens = cls._tokenize_instruction(call['instruction'])
        # Get the number of addresses encoded by this instruction
        addrs = [(i, arg) for i, arg in enumerate(instr_tokens['args'])
                 if re.match(r'\$address', arg) is not None]
        # Don't do anything if this instruction doesn't encode any
        if len(addrs) == 0:
            return
        # For each encoded address
        for i, addr in addrs:
            # Calculate the offset from the beginning of the program
            call['args'][i] = int(call['args'][i]) + cls._calculate_offset(program, int(call['args'][i]))

    @classmethod
    def parse_file(cls, lines, output, pa, output_binary=True, output_object=False):
        """Compiles a preprocessed source file and outputs a binary or textual representation.
        :param lines: The preprocessed file to compile. See the 'input_preprocessor' package.
        :param output: What name should the output files have?
        :param pa: A ProcessorArchitecture instance. See the 'is_parser' package.
        :param output_binary: If true, outputs a binary file.
        :param output_object: If true, outputs a text file where each bit is encoded as a character.
        """

        # No output? Nothing to do.
        if not output or (not output_binary and not output_object):
            COMPILER_WARN_NO_OUTPUT.print_warn(-1, '')
            return

        # Program, contains instruction signatures and their given arguments
        program = []
        # Object, contains compiled code
        obj = bytearray()

        ln = 0  # Line number
        for cur_line in lines:
            # Borrow the _replace_numerals function from the InstructionSetParser
            cur_line = is_parser.InstructionSetParser._replace_numerals(cur_line)
            # Split the line in tokens
            tokens = cls._tokenize_line(cur_line)
            if tokens is None:
                COMPILER_ERR_MISSING_SYMBOL.print_exit(ln, cur_line)
            # Find the instruction with the best-matching signature
            instr = cls._find_matching_instruction(pa, tokens)
            if instr is None:
                COMPILER_ERR_UNDEFINED_INSTRUCTION.print_exit(ln, cur_line)
            # Add the instruction and its given args to the program
            program.append({'instruction': instr, 'args': tokens['args']})
            ln += 1

        for i, call in enumerate(program):
            # Apply an offset to every address. An address initially points to the correct line of code (i),
            # but as instructions are encoded, the object file grows larger and the offset must be recalculated.
            # So, if an instruction encodes an address, we have to add the computed sum of the extra size of the i-1
            # instructions preceding it.
            cls._adjust_addresses(call, program)

            # Encode the instruction, and its arguments, and append it to the object file
            encoded_instr = cls._encode_instruction(call['instruction'], call['args'])
            if encoded_instr is None:
                COMPILER_ERR_UNCOMPILABLE_INSTRUCTION.print_exit(i, call['instruction'])

            obj.extend(encoded_instr)

        if output_binary:
            # If something that can be written on has been passed, use it
            if hasattr(output, 'write'):
                output.write(str(obj))
            else:
                # Otherwise assume that output is a filename
                with open(output + '.kasm', 'wb') as fout:
                    fout.write(obj)

        if output_object:
            # If something that can be written on has been passed, use it
            if hasattr(output, 'write'):
                output.write(cls._binary_to_ascii(obj, pa.WORD_SIZE))
            else:
                # Otherwise assume that output is a filename
                with open(output + '.kobj', 'w') as fout:
                    fout.write(cls._binary_to_ascii(obj, pa.WORD_SIZE))

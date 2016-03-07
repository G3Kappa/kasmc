import re


class PreprocessorError(Exception):
    """Specifies an error that occurred while preprocessing the source file"""

    line_number = 0
    error_id = 0
    error_msg = 'An error occurred during the preprocessing process.'
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

PREPROCESSOR_ERR_INVALID_FILE = PreprocessorError(1, 'Could not read the input file.')
PREPROCESSOR_ERR_INVALID_LABEL = PreprocessorError(2, 'Labels must be defined on a separate line.')


class InputPreprocessor:

    @classmethod
    def _remove_comments(cls, line):
        match = re.search(r'(;.*?)$', line)
        if match is None:
            return line
        return line.replace(match.group(1), '')

    @classmethod
    def _strip_trailing_whitespace(cls, line):
        return line.strip()

    @classmethod
    def _is_label_defined(cls, line):
        return re.search(r'\w+:', line) is not None

    @classmethod
    def _replace_label_usage(cls, line, addr_dict):
        labels_used = [l for l in addr_dict if line.find(l)]

        for label in labels_used:
            line = line.replace(label, str(addr_dict[label]))

        return line

    @classmethod
    def _extract_label(cls, line):
        match = re.search(r'^(\w+):$', line)
        if match is None:
            return None
        return match.group(1)

    @classmethod
    def parse_file(cls, file):
        """Parses a source file and performs label replacement, whitespace stripping and comment removal.
        Doesn't care about syntax.
        :param file: The file to parse.
        """

        # If something that can be read has been passed, use it
        if hasattr(file, 'read'):
                lines = file.read().split('\n')
        # Otherwise assume that file is a filename
        else:
            try:
                with open(file, 'r') as fin:
                    lines = fin.read().split('\n')
            except FileNotFoundError:
                PREPROCESSOR_ERR_INVALID_FILE.print_raise(-1, '')

        # Remove empty lines
        lines = [line for line in lines if len(line.strip()) > 0]

        # Keep a list of pre-processed lines to return
        out_lines = []
        # Store the address pointed to by labels
        label_addresses = {}

        # Begin analyzing the file line by line
        ln = 0  # Line number
        for cur_line in lines:
            # Take care of comments
            cur_line = cls._remove_comments(cur_line)
            # Take care of trailing whitespace
            cur_line = cls._strip_trailing_whitespace(cur_line)

            if cls._is_label_defined(cur_line):
                label = cls._extract_label(cur_line)
                # If a label was defined (label:) but it wasn't alone on its own line, raise an INVALID_LABEL error.
                if label is None:
                    PREPROCESSOR_ERR_INVALID_LABEL.print_raise(ln, cur_line)
                # Set the address pointed to by this label to the current line number.
                # NOTE: The compiler will take care of offsetting these values accordingly.
                label_addresses[label] = ln
            else:
                # Otherwise output this line and increase the line counter
                out_lines.append(cur_line)
                ln += 1

        # Re-iterate every line of code and replace labels in instruction calls with their address
        for idx, line in enumerate(out_lines):
            out_lines[idx] = cls._replace_label_usage(line, label_addresses)

        return out_lines

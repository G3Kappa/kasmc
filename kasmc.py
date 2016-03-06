from asm_compiler import compiler
from input_preprocessor import preprocessor
from instruction_set_parser import is_parser
import argparse
import time

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='Compile arbitrary assembly files with arbitrary instruction sets and arbitrary processor specs.')

    arg_parser.add_argument('-i', '--input', help='The source file to compile.')
    arg_parser.add_argument('-a', '--processor_architecture', help='The processor architecture file to compile against')
    arg_parser.add_argument('-o', '--output', help='The name of the compiled file(s)')
    arg_parser.add_argument('-b', '--output_binary', action='store_true', help='If specified, output a binary file.')
    arg_parser.add_argument('-O', '--output_object', action='store_true', help='If specified, output an object file.')

    args = arg_parser.parse_args()

    # Parse the ProcessorArchitecture object
    parse_start = time.time()
    processor_architecture = is_parser.InstructionSetParser.parse_file(args.processor_architecture)
    parse_end = time.time()
    print('Done parsing the processor architecture file. ({0:.3f}s)'.format(parse_end - parse_start))
    # Preprocess the source file
    preprocess_start = time.time()
    source = preprocessor.InputPreprocessor.parse_file(args.input)
    preprocess_end = time.time()
    print('Done preprocessing the source file. ({0:.3f}s)'.format(preprocess_end - preprocess_start))
    # Compile it!
    compile_start = time.time()
    compiler.Compiler.parse_file(source, args.output, processor_architecture, args.output_binary, args.output_object)
    compile_end = time.time()
    print('Done compiling. ({0:.3f}s)'.format(compile_end - compile_start))
    print('\nALL DONE. Program execution took {0:.3f} seconds.'.format(compile_end - parse_start))

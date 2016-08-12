# KASMc: K Assembly Compiler

KASMc is a compiler for **assembly-like** pseudolanguages written in Python 3.5.
It was made for the purpose of generating binary files for a simple virtual microprocessor.

## Using KASMc

The compiler requires both a _processor architecture file_ and a _source file_ in order to produce something. If you're unsure about what this means, have a look at the paragraphs below.

To compile something, invoke `kasmc.py` in the following manner:

`python kasmc.py -i source_file -a architecture_file -o output_file -b -O`

**NOTE**: The `-b` flag is used to produce a binary file, while the `-O` flag is used to create an object file where each byte is encoded as an ASCII character (`1` or `0`).

## The Pipeline

KASMc is divided in 3 components:
- The _instruction set parser_ (or _processor architecture parser_)
- The _source preprocessor_
- The _compiler_

Instruction set parser and source preprocessor work on the same level by reading an input file each and producing data structures to be used by the compiler, which depends on them.

## A quick example

You can look at the most up-to-date examples in the /tests directory. Still, here's one:

_Source file (test_source.txt)_:

```
	INP A		; Read a value from the input to the accumulator
	LD B, A		; B = A
	INP A
	LD C, A		; C = A
	LD A, 0 	; A = 0
loop:
	ADD A, C	; A = A + C
	DEC B		; B = B - 1
	JP P, loop	; If B > 0 goto loop
	OUT A		; Output A
	HALT		; Terminate the program's execution
```

_Processor architecture file (test_architecture.txt)_:

```
WORD_SIZE(4)

INSTRUCTION(0b0000, 1, 'HALT')
INSTRUCTION(0b0001, 2, 'LD A,_$literal')
INSTRUCTION(0b0010, 1, 'LD A,_B')
INSTRUCTION(0b0011, 1, 'LD A,_C')
INSTRUCTION(0b0100, 1, 'LD B,_A')
INSTRUCTION(0b0101, 1, 'LD C,_A')
INSTRUCTION(0b0110, 1, 'ADD A,_B')
INSTRUCTION(0b0111, 1, 'ADD A,_C')
INSTRUCTION(0b1000, 1, 'SUB A,_C')
INSTRUCTION(0b1001, 1, 'INC B')
INSTRUCTION(0b1010, 1, 'DEC B')
INSTRUCTION(0b1011, 2, 'JP $address')
INSTRUCTION(0b1100, 1, 'INP A')
INSTRUCTION(0b1101, 1, 'OUT A')
INSTRUCTION(0b1110, 2, 'JP P,_$address')
INSTRUCTION(0b1111, 2, 'JP M,_$address')
```

_Compiled object file (output.kobj)_:

```
1100
0100
1100
0101
0001
0000
0111
1010
1110
0110
1101
0000
```

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

# """
# PPPP: Pure Python Python Parser
# """

import sys

assert sys.version[0] >= '3'

def cmd_gen():
    from pppp import parsergen

    parsergen.main()


def cmd_tokenize():
    from pppp import tokenizer

    toks = tokenizer.tokenize_file(sys.argv[1])
    
    for t in toks:
        print(t)

def cmd_parse():
    from pppp import tokenizer, parser, parserbase

    toks = tokenizer.tokenize_file(sys.argv[2])
    
    if True:
        for t in toks:
            print(t)

    p = parser.parser(toks)
    T = p.parse_file_input()
    
    if T is not None:
        parserbase.print_tree(T)
    else:
        print(T)

def cmd_compile():
    from pppp import tokenizer, parser, parserbase, compiler

    toks = tokenizer.tokenize_file(sys.argv[2])

    if not toks:
        print("Tokenizer error")
        return

    p = parser.parser(toks)
    T = p.parse_file_input()

    if not T:
        print("Parser error")
        return

    compiler.compile(T)


def main():
    if sys.argv[1] == 'gen':
        cmd_gen()
    elif sys.argv[1] == 'tokenize':
        cmd_tokenize()
    elif sys.argv[1] == 'parse':
        cmd_parse()
    elif sys.argv[1] == 'compile':
        cmd_compile()

if __name__ == '__main__':
    main()


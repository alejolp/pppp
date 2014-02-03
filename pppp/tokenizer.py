#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

# PPPP: Pure Python Python Parser.
# 
# This is the tokenizer in pure python, without the use of regular 
# expressions.

# UTF BOMs magic bytes.
BOM_UTF8 = b'\xef\xbb\xbf'
BOM_UTF16_LE = b'\xff\xfe'
BOM_UTF16_BE = b'\xfe\xff'
BOM_UTF32_BE = b'\x00\x00\xfe\xff'
BOM_UTF32_LE = b'\xff\xfe\x00\x00'

# Sorted by data length.
BOMS = [('utf32', BOM_UTF32_LE), 
    ('utf32', BOM_UTF32_BE), 
    ('utf16', BOM_UTF16_LE), 
    ('utf16', BOM_UTF16_BE), 
    ('utf8', BOM_UTF8)]

# List of tokens. Same values as Include/token.h
T_ENDMARKER = 0
T_NAME = 1
T_NUMBER = 2
T_STRING = 3
T_NEWLINE = 4
T_INDENT = 5
T_DEDENT = 6
T_LPAR = 7
T_RPAR = 8
T_LSQB = 9
T_RSQB = 10
T_COLON = 11
T_COMMA = 12
T_SEMI = 13
T_PLUS = 14
T_MINUS = 15
T_STAR = 16
T_SLASH = 17
T_VBAR = 18
T_AMPER = 19
T_LESS = 20
T_GREATER = 21
T_EQUAL = 22
T_DOT = 23
T_PERCENT = 24
T_LBRACE = 25
T_RBRACE = 26
T_EQEQUAL = 27
T_NOTEQUAL = 28
T_LESSEQUAL = 29
T_GREATEREQUAL = 30
T_TILDE = 31
T_CIRCUMFLEX = 32
T_LEFTSHIFT = 33
T_RIGHTSHIFT = 34
T_DOUBLESTAR = 35
T_PLUSEQUAL = 36
T_MINEQUAL = 37
T_STAREQUAL = 38
T_SLASHEQUAL = 39
T_PERCENTEQUAL = 40
T_AMPEREQUAL = 41
T_VBAREQUAL = 42
T_CIRCUMFLEXEQUAL = 43
T_LEFTSHIFTEQUAL = 44
T_RIGHTSHIFTEQUAL = 45
T_DOUBLESTAREQUAL = 46
T_DOUBLESLASH = 47
T_DOUBLESLASHEQUAL = 48
T_AT = 49
T_RARROW = 50
T_ELLIPSIS = 51
T_OP = 52
T_ERRORTOKEN = 53
T_N_TOKENS = 54

# Conversion from TOKEN_ID to string.

TOK_NAMES = [None] * T_N_TOKENS
TOK_NAMES[T_ENDMARKER] = 'ENDMARKER'
TOK_NAMES[T_NAME] = 'NAME'
TOK_NAMES[T_NUMBER] = 'NUMBER'
TOK_NAMES[T_STRING] = 'STRING'
TOK_NAMES[T_NEWLINE] = 'NEWLINE'
TOK_NAMES[T_INDENT] = 'INDENT'
TOK_NAMES[T_DEDENT] = 'DEDENT'
TOK_NAMES[T_LPAR] = 'LPAR'
TOK_NAMES[T_RPAR] = 'RPAR'
TOK_NAMES[T_LSQB] = 'LSQB'
TOK_NAMES[T_RSQB] = 'RSQB'
TOK_NAMES[T_COLON] = 'COLON'
TOK_NAMES[T_COMMA] = 'COMMA'
TOK_NAMES[T_SEMI] = 'SEMI'
TOK_NAMES[T_PLUS] = 'PLUS'
TOK_NAMES[T_MINUS] = 'MINUS'
TOK_NAMES[T_STAR] = 'STAR'
TOK_NAMES[T_SLASH] = 'SLASH'
TOK_NAMES[T_VBAR] = 'VBAR'
TOK_NAMES[T_AMPER] = 'AMPER'
TOK_NAMES[T_LESS] = 'LESS'
TOK_NAMES[T_GREATER] = 'GREATER'
TOK_NAMES[T_EQUAL] = 'EQUAL'
TOK_NAMES[T_DOT] = 'DOT'
TOK_NAMES[T_PERCENT] = 'PERCENT'
TOK_NAMES[T_LBRACE] = 'LBRACE'
TOK_NAMES[T_RBRACE] = 'RBRACE'
TOK_NAMES[T_EQEQUAL] = 'EQEQUAL'
TOK_NAMES[T_NOTEQUAL] = 'NOTEQUAL'
TOK_NAMES[T_LESSEQUAL] = 'LESSEQUAL'
TOK_NAMES[T_GREATEREQUAL] = 'GREATEREQUAL'
TOK_NAMES[T_TILDE] = 'TILDE'
TOK_NAMES[T_CIRCUMFLEX] = 'CIRCUMFLEX'
TOK_NAMES[T_LEFTSHIFT] = 'LEFTSHIFT'
TOK_NAMES[T_RIGHTSHIFT] = 'RIGHTSHIFT'
TOK_NAMES[T_DOUBLESTAR] = 'DOUBLESTAR'
TOK_NAMES[T_PLUSEQUAL] = 'PLUSEQUAL'
TOK_NAMES[T_MINEQUAL] = 'MINEQUAL'
TOK_NAMES[T_STAREQUAL] = 'STAREQUAL'
TOK_NAMES[T_SLASHEQUAL] = 'SLASHEQUAL'
TOK_NAMES[T_PERCENTEQUAL] = 'PERCENTEQUAL'
TOK_NAMES[T_AMPEREQUAL] = 'AMPEREQUAL'
TOK_NAMES[T_VBAREQUAL] = 'VBAREQUAL'
TOK_NAMES[T_CIRCUMFLEXEQUAL] = 'CIRCUMFLEXEQUAL'
TOK_NAMES[T_LEFTSHIFTEQUAL] = 'LEFTSHIFTEQUAL'
TOK_NAMES[T_RIGHTSHIFTEQUAL] = 'RIGHTSHIFTEQUAL'
TOK_NAMES[T_DOUBLESTAREQUAL] = 'DOUBLESTAREQUAL'
TOK_NAMES[T_DOUBLESLASH] = 'DOUBLESLASH'
TOK_NAMES[T_DOUBLESLASHEQUAL] = 'DOUBLESLASHEQUAL'
TOK_NAMES[T_AT] = 'AT'
TOK_NAMES[T_RARROW] = 'RARROW'
TOK_NAMES[T_ELLIPSIS] = 'ELLIPSIS'
TOK_NAMES[T_OP] = 'OP'
TOK_NAMES[T_ERRORTOKEN] = 'ERRORTOKEN'

# Tokens table, to convert from string to a token ID.
TOK_STR = {
    '(': T_LPAR,
    ')': T_RPAR,
    '[': T_LSQB,
    ']': T_RSQB,
    ':': T_COLON,
    ',': T_COMMA,
    ';': T_SEMI,
    '+': T_PLUS,
    '-': T_MINUS,
    '*': T_STAR,
    '/': T_SLASH,
    '|': T_VBAR,
    '&': T_AMPER,
    '<': T_LESS,
    '>': T_GREATER,
    '=': T_EQUAL,
    '.': T_DOT,
    '%': T_PERCENT,
    '{': T_LBRACE,
    '}': T_RBRACE,
    '^': T_CIRCUMFLEX,
    '~': T_TILDE,
    '@': T_AT,
    
    '==': T_EQEQUAL,
    '!=': T_NOTEQUAL,
    '<>': T_NOTEQUAL,
    '<=': T_LESSEQUAL,
    '<<': T_LEFTSHIFT,
    '>=': T_GREATEREQUAL,
    '>>': T_RIGHTSHIFT,
    '+=': T_PLUSEQUAL,
    '-=': T_MINEQUAL,
    '->': T_RARROW,
    '**': T_DOUBLESTAR,
    '*=': T_STAREQUAL,
    '//': T_DOUBLESLASH,
    '/=': T_SLASHEQUAL,
    '|=': T_VBAREQUAL,
    '%=': T_PERCENTEQUAL,
    '&=': T_AMPEREQUAL,
    '^=': T_CIRCUMFLEXEQUAL,
    
    '<<=': T_LEFTSHIFTEQUAL,
    '>>=': T_RIGHTSHIFTEQUAL,
    '**=': T_DOUBLESTAREQUAL,
    '//=': T_DOUBLESLASHEQUAL,
    '...': T_ELLIPSIS,
}

P_WHITESPACE = ' \t'
P_DIGITS = set('0123456789')
P_DIGITS_HEX = set("abcdefABCDEF").union(P_DIGITS)
P_DIGITS_BIN = "01"
P_DIGITS_OCT = set("01234567")
P_LETTERS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
P_LETTERS_DIGITS = P_LETTERS.union(P_DIGITS)

P_LETTERS_UNDER = P_LETTERS.union("_")
P_LETTERS_DIGITS_UNDER = P_LETTERS_DIGITS.union("_")

STR_PREFIXES = None
STR_PREFIXES_LEN = None

def init_tables():
    global STR_PREFIXES, STR_PREFIXES_LEN
    
    # (T_STRING, r"(([ruRU]|[bB]|[bB][rR]|[rR][bB])?'''([^\\]|\\.)*?''')"),
    # (T_STRING, r'(([ruRU]|[bB]|[bB][rR]|[rR][bB])?"""([^\\]|\\.)*?""")'),
    # (T_STRING, r"(([ruRU]|[bB]|[bB][rR]|[rR][bB])?'([^\\']|\\.)*?')"),
    # (T_STRING, r'(([ruRU]|[bB]|[bB][rR]|[rR][bB])?"([^\\"]|\\.)*?")'),

    STR_PREFIX1 = ["r", "R", "u", "U", "b", "B",
        "br", "BR", "bR", "Br",
        "rb", "RB", "rB", "Rb"]
    STR_PREFIX2 = ['"""', "'''", '"', "'"]
    STR_PREFIXES = set()

    for x in STR_PREFIX1:
        for y in STR_PREFIX2:
            STR_PREFIXES.add(x+y)

    for y in STR_PREFIX2:
        STR_PREFIXES.add(y)

    STR_PREFIXES_LEN = sorted(set(map(len, STR_PREFIXES)), reverse=True)

def detect_encoding(S):
    # http://www.python.org/dev/peps/pep-0263/
    
    bom = None
    i = 0
    p = 0
    eol = False
    line_number = 1
    
    for bom_name, bom_data in BOMS:
        if S.startswith(bom_data):
            i += len(bom_data)
            bom = bom_name
            break

    while i < len(S) and line_number <= 2:
        if S[i] == ord('\n'):
            line_number = line_number + 1
            eol = True
        elif S[i] == ord('\r'):
            i = i + 1
            continue
        if eol:
            eol = False
            if S[p] == ord('#'):
                try:
                    L = S[p:i].decode('ascii', 'replace')
                except UnicodeDecodeError:
                    L = None

                if L is not None:
                    pos = L.find('coding:')
                    if pos == -1:
                        pos = L.find('coding=')
                    if pos != -1:
                        pos += 7
                        while pos < len(L) and L[pos] == ' ':
                            pos = pos + 1
                        pos2 = pos
                        while pos2 < len(L) and L[pos2] != ' ':
                            pos2 = pos2 + 1
                        encoding = L[pos:pos2].lower()

                        if bom is not None \
                            and encoding.replace('-', '') != bom:
                            raise Exception("BOM mismatch")

                        #print(repr(encoding))
                        return encoding
            p = i + 1
        i = i + 1
    return None

def get_next_op_len(S, i):
    if S[i:i+3] in TOK_STR:
        return 3
    if S[i:i+2] in TOK_STR:
        return 2
    if S[i:i+1] in TOK_STR:
        return 1
    return 0

def is_next_string(S, i):
    for n in STR_PREFIXES_LEN:
        if S[i:i+n] in STR_PREFIXES:
            return S[i:i+n]
    return None
    
def tokenize_file(file_name):
    if STR_PREFIXES is None:
        init_tables()

    with open(file_name, 'rb') as f:
        S = f.read()
    
    # Detect file encoding
    encoding = detect_encoding(S)
    if encoding is None:
        encoding = 'utf-8'

    print("Encoding: " + encoding)
    
    S = S.decode(encoding)
    
    # Genera un token y su metadata:
    # 0 - Codigo/ID del token
    # 1 - Posicion de inicio
    # 2 - Posicion de fin
    # 3 - Numero de linea
    # 4 - String literal que valida el token
    toks = []
    i = 0
    line_start = True
    indent_stack = [0]
    line_num = 1
    level = 0
    
    while i < len(S):
        if False and len(toks):
            print(toks[-1])
            print("i: " + str(i) + " line_start: " + str(line_start))

        if S[i] in P_WHITESPACE:
            p = i
            while p < len(S) and S[p] in P_WHITESPACE:
                p = p + 1
            if line_start:
                line_start = False
                # Check if we need to create indent tokens.
                if p < len(S) and S[p] in '#\n\\':
                    # Line is blank. Eat the comment until EOL.
                    while p < len(S) and S[p] != '\n':
                        p = p + 1
                    # Only create an indent token on a non-empty line.
                    # Ignore this line.
                    i = p
                else:
                    # Line is not blank. Create an indent tokens.
                    dist = p - i
                    # Create an indent token
                    if level == 0:
                        if dist > indent_stack[-1]:
                            toks.append((T_INDENT, i, p, line_num, None))
                            indent_stack.append(dist)
                        elif dist < indent_stack[-1]:
                            while dist < indent_stack[-1]:
                                indent_stack.pop(-1)
                                toks.append((T_DEDENT, i, p, line_num, None))
                    i = p
            else:
                # Just eat the whitespace.
                i = p
        elif S[i] == '\n':
            # Create a newline token
            if len(toks) > 0 and toks[-1][0] != T_NEWLINE and level == 0 and not line_start:
                toks.append((T_NEWLINE, i, p, line_num, '\n'))
            line_num = line_num + 1
            if level == 0:
                line_start = True
            i = i + 1
        elif line_start:
            line_start = False
            while 0 < indent_stack[-1]:
                indent_stack.pop(-1)
                toks.append((T_DEDENT, i, p, line_num, None))
        elif (i+1) < len(S) and S[i] == "\\" and S[i+1] == '\n':
            line_num = line_num + 1
            i = i + 2
        elif S[i] == '#':
            # Comments.
            p = i
            while p < len(S) and S[p] != '\n':
                p = p + 1
            i = p # i points to EOL.
        elif (S[i] in P_DIGITS) or ((i+1) < len(S) and S[i] == '.' and S[i+1] in P_DIGITS):
            # Number
            p = i
            if S[i] == '0' and (i+1) < len(S) and S[i+1] in 'xXbBoO':
                p = i + 2
                
                if S[i+1] in "xX": # Hex
                    while p < len(S) and S[p] in P_DIGITS_HEX:
                        p = p + 1
                if S[i+1] in "bB": # Bin
                    while p < len(S) and S[p] in P_DIGITS_BIN:
                        p = p + 1
                if S[i+1] in "oO": # Oct
                    while p < len(S) and S[p] in P_DIGITS_OCT:
                        p = p + 1
            else:
                while p < len(S) and S[p] in P_DIGITS:
                    p = p + 1
                if p < len(S) and S[p] == '.':
                    while p < len(S) and S[p] in P_DIGITS:
                        p = p + 1
                if p < len(S) and S[p] in "eE":
                    # Exponent, 1e3
                    p = p + 1
                    if p < len(S) and S[p] in '+-':
                        p = p + 1
                    if p < len(S) and not (S[p] in P_DIGITS):
                        raise Exception("SyntaxError: Error")
                    while p < len(S) and S[p] in P_DIGITS:
                        p = p + 1
                if p < len(S) and S[p] in "jJ":
                    # Imaginary
                    p = p + 1
           
            toks.append((T_NUMBER, i, p, line_num, S[i:p]))
            i = p
        elif get_next_op_len(S, i) > 0:
            # General operators: +, -, <<=, ...
            op_len = get_next_op_len(S, i)
            op_str = S[i:i+op_len]
            op_id = TOK_STR[op_str]
            assert op_str in TOK_STR and op_len == len(op_str)
            
            toks.append((op_id, i, p, line_num, op_str))
            i = i + len(op_str)
            
            if len(op_str) == 1:
                if op_str in "[{(":
                    level = level + 1
                elif op_str in "]})":
                    level = level - 1
        elif is_next_string(S, i) is not None:
            # String literals, "hi"
            start_tok = is_next_string(S, i)
            
            if start_tok.endswith("'''"):
                quote = "'''"
            elif start_tok.endswith('"""'):
                quote = '"""'
            elif start_tok.endswith('"'):
                quote = '"'
            elif start_tok.endswith("'"):
                quote = "'"
            else:
                assert False
            
            p = i + len(start_tok)
            
            if len(quote) == 1:
                # If we find an EOL raise an error
                Q = '\n' + quote
                while p < len(S) and S[p] not in Q:
                    p = p + 1
                if p < len(S) and S[p] == '\n':
                    raise Exception("SyntaxError: EOL while scanning string literal")
            else:
                while p < len(S) and not S.startswith(quote, p):
                    if S[p] == '\n':
                        line_num = line_num + 1
                    p = p + 1
            p = p + len(quote)
            toks.append((T_STRING, i, p, line_num, S[i:p]))
            i = p
        elif S[i] in P_LETTERS_UNDER:
            p = i
            while p < len(S) and S[p] in P_LETTERS_DIGITS_UNDER:
                p = p + 1
            toks.append((T_NAME, i, p, line_num, S[i:p]))
            i = p
        else:
            raise Exception("SyntaxError: Unknown token.")
    
    while indent_stack[-1] > 0:
        indent_stack.pop(-1)
        toks.append((T_DEDENT, i, i, line_num, None))
    
    toks.append((T_ENDMARKER, i, i, line_num, None))
    
    return toks

def main():
    import sys
    toks = tokenize_file(sys.argv[1])

    if True:
        for t in toks:
            print((TOK_NAMES[t[0]], ) + t)
            #print((t[0], t[3]))

    return 0

if __name__ == '__main__':
    main()


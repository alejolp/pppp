#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

"""
PPPP: Pure Python Python Parser
"""

from . import tokenizer

class EndOfFile(Exception):
    pass

class astnode:
    def __init__(self, ntype, tok=None):
        self.ntype = ntype
        self.tok = tok
        self.childs = []
        self.parent = None

    def is_terminal(self):
        return self.tok is not None

    def addchild(self, child):
        self.childs.append(child)
        child.parent = self

def print_tree(node, level=0):
    assert type(node) is astnode
    
    if node.tok is not None and node.tok[4] is not None:
        ww = repr(node.tok[4])
    else:
        ww = ""
    print((" " * level) + node.ntype + "(" + ww + ")")
    if node.childs is not None:
        for x in node.childs:
            print_tree(x, level + 1)

class parser_base:
    def __init__(self, toks):
        self.toks = toks
        self.root = None
        self.pos = 0

    def tok_peek(self):
        if self.pos < len(self.toks):
            return self.toks[self.pos]
        #return None # EOF
        raise EndOfFile()

    def tok_peek_gstr(self):
        # returns token "Grammar String" repr.
        #
        # The Python Grammar is a bit tricky to get right; the keywords are 
        # tokenized as "NAME" terminals, but a variable or function name is 
        # also a "NAME" terminal.
        #
        # ie, the 'def' keyword token will return: set(["'def'", "NAME"])
        #
        t = self.tok_peek()
        if t[4] is not None:
            return set(["'" + t[4] + "'", tokenizer.TOK_NAMES[t[0]]])
        return set([tokenizer.TOK_NAMES[t[0]]])
        
    def tok_get(self):
        if self.pos < len(self.toks):
            t = self.toks[self.pos]
            self.pos = self.pos + 1
            return t
        raise EndOfFile()

    def tok_test(self, tok_id, name=None):
        t = self.tok_peek()
        
        if t is None or t[0] != tok_id:
            return False
            
        if name is not None and t[4] != name:
            return False

        if name is None and tok_id == tokenizer.T_NAME and t[4] is not None and self.is_special_name("'" + t[4] + "'"):
            return False

        return True

    def tok_test_and_add(self, tok_id, node, name=None):
        if self.tok_test(tok_id, name):
            node.addchild(astnode(tokenizer.TOK_NAMES[tok_id], self.tok_get()))
            return True
        return False

    def is_special_name(self, name):
        return False


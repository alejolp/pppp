#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

"""
PPPP: Pure Python Python Parser

PPPP Parser Generator. This is the code generator por the "parser.py" file.
"""

import sys
import textwrap
import pprint

from . import grammarparse
from . import tokenizer

GrammarNode = grammarparse.GrammarNode


def indent(L, prefix):
    return '\n'.join([(prefix + x) for x in L])

def longest_seq(N):
    if type(N) is str:
        return 1
    assert type(N) is GrammarNode
    if N.type == 'S':
        assert type(N.data) is list
        return max(len(N.data), max([longest_seq(x) for x in N.data]))
    elif N.type == 'A':
        assert type(N.data) is list
        return max([longest_seq(x) for x in N.data])
    elif N.type == '[':
        assert type(N.data) is GrammarNode
        return longest_seq(N.data)
    elif N.type == '*':
        assert type(N.data) is GrammarNode
        return longest_seq(N.data)
    elif N.type == '+':
        assert type(N.data) is GrammarNode
        return longest_seq(N.data)
    assert False

class parser_gen:
    def __init__(self):
        self.G = None
        self.header = ""
        self.header2 = ""
        self.methods = []
        self.hidx = 1 # Index counter for sub-expressions
        self.tables = [] # Sub-sets of FIRST subexpressions

    def newTable(self, data):
        idx = len(self.tables)
        self.tables.append(data)
        return idx

    def parseSubexpr(self, N, ctx):
        helper_name = "parsehelper_" + str(self.hidx)
        self.hidx = self.hidx + 1
        
        m = """
    def {0}(self, node):
        \"\"\" ## subexpr ##
        {1}
        \"\"\"
        oldpos = self.pos
        #
""".format(helper_name, repr(N))

        if type(N) is str:
            if self.G.isTerminal(N):
                if N[0] == "'" and N[-1] == "'" and N[1:-1] in tokenizer.TOK_STR:
                    # Special token code
                    m += """
        # Terminal literal operator
        if not self.tok_test(tokenizer.T_{0}, {1}):
            return None
        tok = self.tok_peek()
        self.pos = self.pos + 1
        return [astnode({2}, tok)]
""".format(tokenizer.TOK_NAMES[tokenizer.TOK_STR[N[1:-1]]], # 0
    repr(N[1:-1]),                              # 1
    repr(N))                                    # 2
                elif N[0] == "'" and N[-1] == "'":
                    # T_NAME
                    m += """
        # Terminal NAME
        if not self.tok_test(tokenizer.T_NAME, {1}):
            return None
        tok = self.tok_peek()
        self.pos = self.pos + 1
        return [astnode({0}, tok)]
""".format(repr(N), repr(N[1:-1]))
                else:
                    m += """
        # Terminal std
        if not self.tok_test(tokenizer.T_{0}):
            return None
        tok = self.tok_peek()
        self.pos = self.pos + 1
        return [astnode({1}, tok)]
""".format(N, repr(N))
            else:
                m += """
        # Non-terminal
        c = self.parse_{0}()
        if c is None:
            self.pos = oldpos
            return None
        return [c]
""".format(N)
            self.methods.append(m)
            return helper_name

        assert type(N) is GrammarNode
        if N.type == 'S':
            assert type(N.data) is list
            childs = [(self.parseSubexpr(x, ctx), x) for x in N.data]
            m += """
        # S-type
        childs = []
"""
            for x, _subp in childs:
                m += """
        c = self.{0}(node) # {1}
        if c is None:
            self.pos = oldpos
            return None
        childs.extend(c)
""".format(x, _subp)
            m += """
        return childs
"""
            self.methods.append(m)
            return helper_name
        elif N.type == 'A':
            assert type(N.data) is list
            #' | '.join([printNodeStr(x) for x in N.data])
            
            def name_count(N):
                f = self.G.FIRST(N)
                if 'NAME' in f:
                    return 0
                return 1
            
            def has_eps(N):
                f = self.G.FIRST(N)
                if grammarparse.EPS_SYMBOL in f:
                    return 0
                return 1
            
            childs = [(self.parseSubexpr(x, ctx), (has_eps(x), longest_seq(x), name_count(x)), x) for x in N.data]
            
            # This is a simple attempt to fix some issues of production parsing:
            #
            # 1. In the production:
            #   testlist_comp: (test|star_expr) ( comp_for | (',' (test|star_expr))* [','] )
            #
            # The last alternative in the part has \epsilon in the FIRST set. That's it, 
            #
            #   \epsilon \in FIRST("""(',' (test|star_expr))* [',']""")
            #
            # Every alternative which has \epsilon should be tested last.
            #
            # 2. In the production:
            #   comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
            #
            # an LL(1) parser needs to take into account that the last two choices have
            # the same FIRST set. This is why we try to eat the longest first.
            #
            # 3. In the production:
            #   small_stmt: (expr_stmt | del_stmt | pass_stmt | flow_stmt |
            #       import_stmt | global_stmt | nonlocal_stmt | assert_stmt)
            #
            # the same as above, the NAME terminal is in the FIRST set of all of the 
            # choices. We fisrt try the specific NAME terminals (ie 'import'), and last
            # we try the general 'expr_stmt' one.
            #
            
            childs.sort(key=(lambda x: x[1]), reverse=True)

            # For each terminal we check if it is contained in only one FIRST set, or more.
            # If it is present in only one we dispatch the function using the table. 
            # If it is present in two or more, we iterate each alternative using the order of precedence.

            N_first_set=self.G.FIRST(N)
            N_first_set_idx=self.newTable(N_first_set)

            m += """
        # A-type (alt)
        if self.tok_peek_gstr().isdisjoint(TABLE[{0}]) and not ({1} in TABLE[{0}]):
            self.pos = oldpos
            return None
""".format(N_first_set_idx, repr(grammarparse.EPS_SYMBOL))

            alts_first_sets=[]
            for x, _xlen, _subp in childs:

                # FIRST stuff.
                this_first_set=self.G.FIRST(_subp)
                disjoint=[]
                for sidx, s in enumerate(alts_first_sets):
                    if not s.isdisjoint(this_first_set):
                        disjoint.append((sidx, s.intersection(this_first_set)))
                alts_first_sets.append(this_first_set)
                if len(disjoint) > 0:
                    disjoint_str = "INTERSECTION: YES " + ', '.join(map(str, disjoint))
                else:
                    disjoint_str = "INTERSECTION: EMPTY"

                m += """
        c = self.{0}(node) # {1}, {2} FIRST: {3} {4}
        if c is not None:
            return c
""".format(x, _xlen, _subp, this_first_set, disjoint_str)
            m += """
        self.pos = oldpos
        return None
"""
            self.methods.append(m)
            return helper_name
        elif N.type == '[':
            assert type(N.data) is GrammarNode
            #"[" + printNodeStr(N.data) + "]"
            child = self.parseSubexpr(N.data, ctx)
            
            m += """
        # [-type (opt)
        c = self.{0}(node)
        if c is None:
            self.pos = oldpos
            return []
        return c
""".format(child)
            self.methods.append(m)
            return helper_name
        elif N.type == '*':
            assert type(N.data) is GrammarNode
            #"(" + printNodeStr(N.data) + ")*"
            child = self.parseSubexpr(N.data, ctx)

            m += """
        # *-type (0+)
        childs = []
        while True:
            oldpos2 = self.pos
            c = self.{0}(node)
            if c is None:
                self.pos = oldpos2
                break
            childs.extend(c)
        return childs
""".format(child)
            self.methods.append(m)
            return helper_name
        elif N.type == '+':
            assert type(N.data) is GrammarNode
            #"(" + printNodeStr(N.data) + ")+"
            child = self.parseSubexpr(N.data, ctx)

            m += """
        # +-type (1+)
        childs = []
        i = 0
        while True:
            oldpos2 = self.pos
            c = self.{0}(node)
            if c is None:
                self.pos = oldpos2
                break
            childs.extend(c)
            i = i + 1
        if i == 0:
            self.pos = oldpos
            return None
        return childs
""".format(child)
            self.methods.append(m)
            return helper_name
        assert False
        
    def run(self):
        self.G = grammarparse.parse_grammar_file('Grammar')
        self.header = ("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

# Autogenerated file. Do not edit!

from pppp import parserbase
from pppp import tokenizer

from pppp.parserbase import astnode


SPECIAL_NAMES = {0}

""".format(self.G.special_terminals))

        self.header += "FIRST=" + pprint.pformat(dict([(x[0], self.G.FIRST(x[0])) for x in self.G.productions]))
        self.header += """\n"""

        self.header2 = ("""
class parser(parserbase.parser_base):
    def __init__(self, toks):
        parserbase.parser_base.__init__(self, toks)
        
    def is_special_name(self, name):
        return name in SPECIAL_NAMES
""".format())
    
        for x, p in zip(self.G.productions, self.G.productions_text):
            #print(x)
            #print(p)
            #print()
            assert type(x[2]) is GrammarNode

            subexp = self.parseSubexpr(x[2], {})
            
            m = ("""
    def parse_{0}(self):
        \"\"\"
{1}
        
{2}
        \"\"\"
        node = astnode('{0}')
        if self.tok_peek_gstr().isdisjoint(FIRST[{3}]):
            return None
        #
        startpos = self.pos
        c = self.{4}(node)
        if c is None:
            self.pos = startpos
            return None
""".format(x[0],                                        # 0
            indent(textwrap.wrap(p), " " * 8),          # 1
            indent(textwrap.wrap(repr(x)), " " * 8),    # 2
            repr(x[0]),                                 # 3
            subexp))                                    # 4
        
            m += ("""
        for x in c:
            node.addchild(x)
        return node
""")
        
            self.methods.append(m)

        print(self.header)
        #print('\n'.join(("TABLE_" + str(i) + "=" + repr(x)) for i, x in enumerate(self.tables)))
        print("""TABLE=""" + pprint.pformat(self.tables))
        print(self.header2)
        print('\n\n'.join(map(lambda x: x.strip("\n").rstrip(), self.methods)))

def main():
    pg = parser_gen()
    pg.run()
    
if __name__ == '__main__':
    main()


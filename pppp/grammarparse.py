#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

"""
PPPP: Pure Python Python Parser

Python grammar parser, Grammar/Grammar.
"""

#import os
import sys
import string
import pprint
import functools

from . import tokenizer
from . import utils

# Caracteres válidos en un identificador no terminal.
NT = set(string.ascii_letters + "_")
assert len(NT) == 53

# Símbolos especiales de EBNF.
SYM = set("[]()*+|")

# Símbolo epsilon para denotar el string vacío, \eps.
EPS_SYMBOL = 'EPS'

# Símbolo fin de entrada.
ENDMARK_SYMBOL = tokenizer.T_ENDMARKER

# Para buscar eficientemente si un string es un terminal.
TOK_NAMES = set(tokenizer.TOK_NAMES)

INPUT_END_SYMBOL = tokenizer.TOK_NAMES[tokenizer.T_ENDMARKER]

def splitInAlternatives(T):
    """
    Dada una secuencia de alternativas separadas por '|', 
    devuelve una lista de cada una de estas, con la barra '|' 
    como separador, teniendo en cuenta que pueden haber paréntesis y corchetes.
    
    >>> grammarparse.splitInAlternatives([])
    [[]]
    >>> grammarparse.splitInAlternatives(['A', 'B'])
    [['A', 'B']]
    >>> grammarparse.splitInAlternatives(['A', '|', 'B'])
    [['A'], ['B']]
    >>> grammarparse.splitInAlternatives(list("A|B"))
    [['A'], ['B']]
    >>> grammarparse.splitInAlternatives(list("(A|B)|C"))
    [['(', 'A', '|', 'B', ')'], ['C']]

    """ 
    pila = []
    i = 0
    inicio = 0
    salida = []
    
    while i < len(T):
        if type(T[i]) is str:
            if T[i] in "[(":
                pila.append((T[i], i))
            elif T[i] in "])":
                if T[i] == ']':
                    assert pila[-1][0] == '['
                elif T[i] == ')':
                    assert pila[-1][0] == '('
                else:
                    assert False
                pila.pop(-1)
            elif T[i] == '|':
                if len(pila) == 0:
                    salida.append(T[inicio:i])
                    inicio = i + 1
        i = i + 1
    salida.append(T[inicio:])
    return salida

class GrammarNode:
    __slots__=('type', 'data')
    def __init__(self, type_, data):
        """
        Nodo del arbol para representar la gramática de Python.
        
        - "X|Y" GrammarNode('A', [X, Y]): Hay que elegir entre X o Y. data es un list.
    
        - "X Y" GrammarNode('S', [X, Y]): Es una secuencia que primero viene X y luego Y. data es un list.
        
        - "[X]" GrammarNode('[', X). data es un GrammarNode.
        
        - "(X)*" GrammarNode('*', X). data es un GrammarNode.
        
        - "(X)+" GrammarNode('+', X). data es un GrammarNode.
        """
        self.type = type_
        self.data = data
        assert type(data) is list or type(data) is GrammarNode

    def __repr__(self):
        return "GrammarNode('" + self.type + "', " + repr(self.data) + ")"

def buildTree(T):
    """
    Construye una representacion de Arbol de una linea de produccion.
    """
    
    parts = splitInAlternatives(T)
    
    if len(parts) > 1:
        L = []
        for e in parts:
            L.append(buildTree(e))
        return GrammarNode('A', L)
    else:
        P = list(parts[0])
        S = [] # Pila, Stack.
        i = 0
        while i < len(P):
            e = P[i]
            W = None
            X = None
            if type(e) is str:
                if e in '[(':
                    S.append((e, i))
                elif e in '])':
                    X = S.pop(-1)
                    W = buildTree(P[(X[1] + 1):i])
                    if e == ']':
                        del P[(X[1]):i]
                        P[X[1]] = GrammarNode('[', W)
                        i = X[1]
                    elif (i + 1) < len(P):
                        if P[i+1] == '*':
                            del P[(X[1]):(i+1)]
                            P[X[1]] = GrammarNode('*', W)
                            i = X[1]
                        elif  P[i+1] == '+':
                            del P[(X[1]):(i+1)]
                            P[X[1]] = GrammarNode('*', W)
                            i = X[1]
                        else:
                            # Parentesis sin cuantificador
                            del P[(X[1]):i]
                            P[X[1]] = W
                            i = X[1]
                    else:
                        # Parentesis sin cuantificador
                        del P[(X[1]):i]
                        P[X[1]] = W
                        i = X[1]
                elif e in '*+':
                    del P[i]
                    P[i - 1] = GrammarNode(e, GrammarNode('S', [P[i - 1]]))
                    i = i - 1
            i = i + 1
        return GrammarNode('S', P)

def collectLeaves(N, out):
    if type(N) is str:
        out.append(N)
    else:
        assert type(N) is GrammarNode
        if N.type == 'S':
            assert type(N.data) is list
            for x in N.data:
                collectLeaves(x, out)
        elif N.type == 'A':
            assert type(N.data) is list
            for x in N.data:
                collectLeaves(x, out)
        elif N.type == '[':
            assert type(N.data) is GrammarNode
            collectLeaves(N.data, out)
        elif N.type == '*':
            assert type(N.data) is GrammarNode
            collectLeaves(N.data, out)
        elif N.type == '+':
            assert type(N.data) is GrammarNode
            collectLeaves(N.data, out)
        else:
            assert False

def printNodeStr(N):
    if type(N) is str:
        return N
    assert type(N) is GrammarNode
    if N.type == 'S':
        assert type(N.data) is list
        return ' '.join([printNodeStr(x) for x in N.data])
    elif N.type == 'A':
        assert type(N.data) is list
        return ' | '.join([printNodeStr(x) for x in N.data])
    elif N.type == '[':
        assert type(N.data) is GrammarNode
        return "[" + printNodeStr(N.data) + "]"
    elif N.type == '*':
        assert type(N.data) is GrammarNode
        return "(" + printNodeStr(N.data) + ")*"
    elif N.type == '+':
        assert type(N.data) is GrammarNode
        return "(" + printNodeStr(N.data) + ")+"
    assert False

def printNodeList(N):
    if type(N) is str:
        return [N]
    assert type(N) is GrammarNode
    if N.type == 'S':
        assert type(N.data) is list
        return functools.reduce(lambda x, y: (x+y), [printNodeList(x) for x in N.data])
    elif N.type == 'A':
        assert type(N.data) is list
        return ['('] + functools.reduce(lambda x, y: (x + ['|'] + y), [printNodeList(x) for x in N.data]) + [')']
    elif N.type == '[':
        assert type(N.data) is GrammarNode
        return ["["] + printNodeList(N.data) + ["]"]
    elif N.type == '*':
        assert type(N.data) is GrammarNode
        return ["("] + printNodeList(N.data) + [")", "*"]
    elif N.type == '+':
        assert type(N.data) is GrammarNode
        return ["("] + printNodeList(N.data) + [")", "+"]
    assert False

class GrammarParser:
    def __init__(self):
        self.G = None
        self.productions = None
        self.productions_text = None
        self.tokens = TOK_NAMES
        self.first_table = {}
        self.first_table_build = set()
        self.follow_table = {}
        #self.m_table = {} # LL(1)

        # FIXME: 
        self.start_symbs = ['file_input']

    def parseLineTokenize(self, line):
        """
        Tokenizer de una linea de producción. Convierte un string en una lista
        de strings separados por significado.

        >>> ParseLineTokenize("expr: xor_expr ('|' xor_expr)*")
        ['expr', ':', 'xor_expr', '(', "'|'", 'xor_expr', ')', '*']
        """

        R = []
        i = 0
        L = len(line)

        # Nombre de la produccion: "nombre: "
        while i < L and line[i] in NT:
            i = i + 1
        
        if i == L or line[i] != ':':
            raise ValueError("Produccion invalida")

        R.append(line[:i])
        R.append(':')
        i = i + 1

        while i < L:
            # DEBUG(line, i, R)

            # Come-blancos.
            while i < L and line[i] in (' ', '\t'):
                i = i + 1

            # Identificadores de no terminales.
            start = i
            while i < L and line[i] in NT:
                i = i + 1
            if start < i:
                R.append(line[start:i])

            # Simbolos de 1 char
            while i < L and line[i] in SYM:
                R.append(line[i])
                i = i + 1

            # String literales: '<'
            if i < L and line[i] == "'":
                start = i
                i = i + 1
                while i < L and line[i] != "'":
                    i = i + 1
                if i < L:
                    R.append(line[start:i+1])
                    i = i + 1
                else:
                    raise ValueError("Produccion invalida")

        return R

    def parseLineToTree(self, T):
        """
        Construye el arbol que representa la produccion
        """

        #print("T: ", T)        
        
        partes = T[2:]
        partes2 = buildTree(partes)
        
        #print("partes: ", partes)
        #print("partes2: ", partes2)
        
        return T[:2] + [partes2]

    def parseLine(self, line):
        """
        Se realiza en dos pasos:
          1. Tokenizar
          2. Convertir EBNF en BNF.
        """
        # 1. Tokenizar.
        T = self.parseLineTokenize(line)
        
        # 2. Convertir de EBNF plano a un arbol.
        G = self.parseLineToTree(T)
        
        #print(T)
        #print(G[0:2] + printNodeList(G[2]))
        #print()
        
        return [G]

    def parseFile(self, fileName):
        """
        Devuelve una estructura de datos adecuada para procesar el archivo
        Grammar/Grammar de Python.
        """
        with open(fileName) as f:
            productions = []
            productions_text = []
            prevLine = None
            for line in f:
                # Descartar líneas en blanco o totalmente comentadas
                lineStripp = line.strip()
                if len(lineStripp) == 0 or lineStripp.startswith('#'):
                    continue

                # Descartar comentarios in-line
                rPos = line.rfind('#')
                if rPos != -1:
                    line = line[:rPos]

                # Cada producción puede ocupar más de una línea. Si la línea
                # siguiente está identada, es una continuación de la anterior.
                if line.startswith((' ', '\t')):
                    prevLine += " " + line.strip()
                else:
                    if prevLine is not None:
                        productions_text.append(prevLine)
                        productions += (self.parseLine(prevLine))
                    prevLine = line.rstrip()

            # La última línea.
            if prevLine is not None:
                productions_text.append(prevLine)
                productions += (self.parseLine(prevLine))

        # productions es una lista de listas, donde cada una dice: ['A', ':', W]
        # donde 'A' es el nombre de la produccion, ':' es el separador inicial, simbolo de metagramatica del archivo Grammar,
        # y W es el nodo del arbol de EBNF
        self.productions = productions
        self.productions_text = productions_text
        
        #
        # El diccionario G contiene las producciones de la gramática procesada.
        # La clave es el nombre del símbolo no terminal, y como valor 
        # contiene una lista de alternativas de producción.
        #
        self.G = dict([(x[0], x[2]) for x in productions])
        assert len(self.productions) == len(self.G.keys())
        
        # Aplana el arbol EBNF en uno equivalente BNF. La nueva gramática se almacena en G2 de la forma:
        # A -> Q W | E | EPS
        # {'A': [[Q, W], [E], [EPS]]}
        
        # FIXME:
        ## self.transform_to_bnf()

        out = []
        for n in self.G:
            prod = self.G[n]
            collectLeaves(prod, out)
        
        self.special_terminals = set([x for x in out if x.startswith("'")])
        
    def isNonterminal(self, X):
        assert (X != EPS_SYMBOL)
        return X in self.G

    def isTerminal(self, X):
        assert (X != EPS_SYMBOL)
        return X in TOK_NAMES or (X[0] == "'" and X[-1] == "'")

    def print(self):
        pprint.pprint(self.G)

    def FIRST(self, N):
        """
        Devuelve el conjunto de terminales que pueden comenzar una derivación desde N.
        """
        #print("$$$ ", N)
        
        ret = None
        # memorize = False
        
        #if memorize:
        #    if N in self.first_table_build:
        #        return set()
        #    self.first_table_build |= set([N])
        
        if type(N) is str:
            #if memorize:
            #    if N in self.first_table:
            #        ret = self.first_table[N]
            
            if ret is None:
                if self.isTerminal(N):
                    ret = frozenset([N])
                else:
                    ret = self.FIRST(self.G[N])
                
                #if memorize:
                #    self.first_table[N] = ret
        else:
            #print("!!!", N)
            if N.type == 'S':
                t = frozenset()
                # Hay que cortar el recorrido de la secuencia en el primer elemento que no tenga EPS, 
                # y agregar EPS solo cuando todos lo tienen.
                eps_count = 0
                for x in N.data:
                    u = self.FIRST(x)
                    eps_was_here = (EPS_SYMBOL in u)
                    if eps_was_here:
                        u = u - frozenset([EPS_SYMBOL])
                        eps_count = eps_count + 1
                    t = t | u
                    if not eps_was_here:
                        break
                if eps_count == len(N.data):
                    t = t | frozenset([EPS_SYMBOL])
                ret = t
            elif N.type == 'A':
                t = frozenset()
                for x in N.data:
                    u = self.FIRST(x)
                    if False and len(u.intersection(t)) != 0:
                        # Si esto da True en algun lugar, la gramatica hace falta
                        # procesarla con backtracking, ya que existe "P -> A | B", 
                        # con (FIRST(A) \intersection FIRST(B)) != \empty . Por lo tanto
                        # en una alternativa "A|B" no alcanza con saber el proximo simbolo,
                        # y A y B tienen un prefijo de terminales en común.
                        print(t)
                        print(u)
                        print(N)
                        # assert False
                    t = t | u
                ret = t
            elif N.type == '*':
                t = frozenset([EPS_SYMBOL])
                t |= self.FIRST(N.data)
                ret = t
            elif N.type == '+':
                t = frozenset([])
                t |= self.FIRST(N.data)
                ret = t
            elif N.type == '[':
                t = frozenset([EPS_SYMBOL])
                t |= self.FIRST(N.data)
                ret = t

        assert ret is not None
        #if memorize:
        #    self.first_table_build.remove(N)
        return ret

    def build_FIRST(self):
        """Construye la tabla FIRST para cada noterminal A"""
        for A in self.productions:
            self.first_table[A[0]] = self.FIRST(A[0])

    #~ def FIRST2(self, N):
        #~ """
        #~ Devuelve FIRST a partir de la definicion de gramatica traducida G2
        #~ N puede ser un string terminal, no terminal, o una secuencia de produccion (lista).
        #~ """
        #~ # print("??? ", N)
        #~ if type(N) is str:
            #~ if self.isTerminal(N):
                #~ return frozenset([N])
                #~ 
            #~ prods = self.G2[N]
            #~ ret = frozenset()
            #~ for p in prods:
                #~ r2 = self.FIRST2(p)
                #~ ret = ret | r2
            #~ return ret
        #~ else:
            #~ i = 0
            #~ eps_counter = 0
            #~ ret = frozenset()
            #~ while i < len(N):
                #~ if N[i] == EPS_SYMBOL:
                    #~ assert len(N) == 1
                    #~ return frozenset([EPS_SYMBOL])
                #~ r2 = self.FIRST2(N[i])
                #~ if EPS_SYMBOL in r2:
                    #~ r2 = r2 - frozenset([EPS_SYMBOL])
                    #~ eps_counter = eps_counter + 1
                    #~ ret = ret | r2
                #~ else:
                    #~ ret = ret | r2
                    #~ break
                #~ i = i + 1
            #~ if eps_counter == len(N):
                #~ ret = ret | frozenset([EPS_SYMBOL])
            #~ return ret
#~ 
    #~ def FIRST2memo(self, N):
        #~ if self.isNonterminal(N):
            #~ if not N in self.first_table:
                #~ self.first_table = self.FIRST2(N)
            #~ return self.first_table[N]
        #~ return self.FIRST2(N)
#~ 
    #~ def transform_to_bnf(self):
        #~ """
        #~ Transforma el arbol de gramatica EBNF en uno equivalente BNF
        #~ """
        #~ self.G2 = {}
        #~ self.G2_count = {}
        #~ for n in self.G:
            #~ prod = self.G[n]
            #~ self.G2_count[n] = 0
            #~ self.G2[n] = [[self.bnf_rec(n, prod)]]
#~ 
    #~ def get_next_id(self, n):
        #~ self.G2_count[n] += 1
        #~ return str(self.G2_count[n])
        #~ 
    #~ def bnf_rec(self, original_name, N):
        #~ """
        #~ Transforma recursivamente un nodo de arbol (y sus hijos) en una produccion equivalente BNF.
        #~ Devuelve siempre un unico string que representa la producción o el terminal equivalente.
        #~ Las nuevas producciones se insertan automaticamente en self.G2.
        #~ """
        #~ if type(N) is str:
            #~ return N
        #~ assert type(N) is GrammarNode
        #~ if N.type == 'S':
            #~ assert type(N.data) is list
            #~ newprod_name = original_name + "_ARB_" + self.get_next_id(original_name)
            #~ newprod_data = [[self.bnf_rec(original_name, x) for x in N.data]]
            #~ assert newprod_name not in self.G2
            #~ self.G2[newprod_name] = newprod_data
            #~ return newprod_name
        #~ elif N.type == 'A':
            #~ assert type(N.data) is list
            #~ newprod_name = original_name + "_ARB_" + self.get_next_id(original_name)
            #~ newprod_data = [[self.bnf_rec(original_name, x)] for x in N.data]
            #~ assert newprod_name not in self.G2
            #~ self.G2[newprod_name] = newprod_data
            #~ return newprod_name
        #~ elif N.type == '[':
            #~ """
            #~ A -> [B]
            #~ 
            #~ A -> B'
            #~ B' -> B | EPS
            #~ """
            #~ assert type(N.data) is GrammarNode
            #~ newprod_name = original_name + "_ARB_" + self.get_next_id(original_name)
            #~ newprod_data = [[self.bnf_rec(original_name, N.data)], [EPS_SYMBOL]]
            #~ assert newprod_name not in self.G2
            #~ self.G2[newprod_name] = newprod_data
            #~ return newprod_name
        #~ elif N.type == '*':
            #~ """
            #~ A -> B*
            #~ 
            #~ A -> C
            #~ B' -> B
            #~ C -> B' C | EPS
            #~ """
            #~ assert type(N.data) is GrammarNode
            #~ newprod1_name = original_name + "_ARB_" + self.get_next_id(original_name) # B'
            #~ newprod1_data = [[self.bnf_rec(original_name, N.data)]]
            #~ newprod2_name = original_name + "_ARB_" + self.get_next_id(original_name) # C
            #~ newprod2_data = [[newprod1_name, newprod2_name], [EPS_SYMBOL]]
            #~ assert newprod1_name not in self.G2
            #~ self.G2[newprod1_name] = newprod1_data
            #~ self.G2[newprod2_name] = newprod2_data
            #~ return newprod2_name
        #~ elif N.type == '+':
            #~ """
            #~ A -> B+
            #~ 
            #~ A -> C
            #~ B' -> B
            #~ C -> B' | B' C
            #~ """
            #~ assert type(N.data) is GrammarNode
            #~ newprod1_name = original_name + "_ARB_" + self.get_next_id(original_name) # B'
            #~ newprod1_data = [[self.bnf_rec(original_name, N.data)]]
            #~ newprod2_name = original_name + "_ARB_" + self.get_next_id(original_name) # C
            #~ newprod2_data = [[newprod1_name], [newprod1_name, newprod2_name]]
            #~ assert newprod1_name not in self.G2
            #~ self.G2[newprod1_name] = newprod1_data
            #~ self.G2[newprod2_name] = newprod2_data
            #~ return newprod2_name
        #~ assert False

        
def parse_grammar_file(grammarFile):
    P = GrammarParser()
    P.parseFile(grammarFile)
    # P.print()
    
    # P.build_FIRST()

    if False:
        print(P.special_terminals)

    if False:
        for n in sorted(P.G):
            a = P.FIRST(n)
            b = P.FIRST2(n)
            if len(a.intersection(b)) != len(a):
                print("!!!, ", n)
                print(a)
                print(b)
    
    if False:
        for n in P.G:
            print("%%%, ", n)
            print(P.FIRST(n))
            print()
            print()
    
    if False:
        for n in sorted(P.G2):
            print(n, ": ", P.G2[n])
    
    return P

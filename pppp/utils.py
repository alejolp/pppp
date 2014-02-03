#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PPPP: Pure Python Python Parser
"""

# Degub.
if True:
    def DEBUG(*args, **kwargs):
        print(*args, **kwargs)
else:
    def DEBUG(*args, **kwargs):
        pass

def num2ascii(n):
    S = chr(ord('a') + (n % 26))
    n = n // 26
    while n > 0:
        S = chr(ord('a') + (n % 26)) + S
        n = n // 26
    return S

def split_list(L, sep):
    """
    Devuelve una lista de listas, donde cada sublista es una subsecuencia
    continua de la lista L original, separada por sep.

    >>> split_list([1,99,3], 99)
    [[1], [3]]
    """
    start = 0
    pos = -1
    R = []
    while pos < len(L):
        try:
            pos = L.index(sep, start)
        except ValueError:
            pos = len(L)
        R.append(L[start:pos])
        start = pos + 1
    return R



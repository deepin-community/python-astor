#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright (c) 2015 Patrick Maupin

This module reads the strings generated by build_expressions,
and runs them through the Python interpreter.

For strings that are suboptimal (too many spaces, etc.),
it simply dumps them to a miscompare file.

For strings that seem broken (do not parse after roundtrip)
or are maybe too compressed, it dumps information to the console.

This module does not take too long to execute; however, the
underlying build_expressions module takes forever, so this
should not be part of the automated regressions.

"""

import sys
import ast
import astor

try:
    import importlib
except ImportError:
    try:
        import all_expr_2_6 as mymod
    except ImportError:
        print("Expression list does not exist -- building")
        from . import build_expressions
        build_expressions.makelib()
        print("Expression list built")
        import all_expr_2_6 as mymod
else:
    mymodname = 'all_expr_%s_%s' % sys.version_info[:2]

    try:
        mymod = importlib.import_module(mymodname)
    except ImportError:
        print("Expression list does not exist -- building")
        from . import build_expressions
        build_expressions.makelib()
        print("Expression list built")
        mymod = importlib.import_module(mymodname)


def checklib():
    print("Checking expressions")
    parse = ast.parse
    dump_tree = astor.dump_tree
    to_source = astor.to_source
    with open('mismatch_%s_%s.txt' % sys.version_info[:2], 'wb') as f:
        for srctxt in mymod.all_expr.strip().splitlines():
            srcast = parse(srctxt)
            dsttxt = to_source(srcast)
            if dsttxt != srctxt:
                srcdmp = dump_tree(srcast)
                try:
                    dstast = parse(dsttxt)
                except SyntaxError:
                    bad = True
                    dstdmp = 'aborted'
                else:
                    dstdmp = dump_tree(dstast)
                    bad = srcdmp != dstdmp
                if bad or len(dsttxt) < len(srctxt):
                    print(srctxt, dsttxt)
                    if bad:
                        print('****************** Original')
                        print(srcdmp)
                        print('****************** Extra Crispy')
                        print(dstdmp)
                        print('******************')
                        print()
                        print()
                f.write(('%s      %s\n' % (repr(srctxt),
                                           repr(dsttxt))).encode('utf-8'))


if __name__ == '__main__':
    checklib()

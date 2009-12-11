#!/usr/bin/env python


import sys
import os
import unittest


def regressionTest():
    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    modules = []
    
    for file in os.listdir(path):
        if file == os.path.basename(sys.argv[0]) or not file.endswith('.py'):
            continue
        filename = os.path.splitext(file)[0]
        module = __import__(filename)
        modules.append(unittest.defaultTestLoader.loadTestsFromModule(module))
    
    return unittest.TestSuite(modules)      


if __name__ == "__main__":                   
    unittest.main(defaultTest="regressionTest")


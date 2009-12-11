#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest


from lilyplayer.utils.utils import levenshtein_distance
from lilyplayer.utils.utils import reduce_fraction


class LevenshteinDistanceTestCase(unittest.TestCase):
    def testEqual(self):
        self.assertEquals(levenshtein_distance('',     ''),     0)
        self.assertEquals(levenshtein_distance('abcd', 'abcd'), 0)
        
    def testAdd(self):
        self.assertEquals(levenshtein_distance('abcd',   'abcdXY'), 2)
        self.assertEquals(levenshtein_distance('abcdXY', 'abcd'),   2)
        self.assertEquals(levenshtein_distance('abZZcd', 'abcd'),   2)
        self.assertEquals(levenshtein_distance('abcd',   'abUcd'),  1)
        
        
    def testReplace(self):
        self.assertEquals(levenshtein_distance('abcd', 'abCd'), 1)
        self.assertEquals(levenshtein_distance('abXd', 'abcd'), 1)
        self.assertEquals(levenshtein_distance('abcd', 'ab12'), 2)
        
    def testDelete(self):
        self.assertEquals(levenshtein_distance('abcd', 'abc'), 1)
        self.assertEquals(levenshtein_distance('abXd', 'ab'),  2)
        self.assertEquals(levenshtein_distance('abcd', 'a'),   3)
        self.assertEquals(levenshtein_distance('abcd', ''),    4)
        
        self.assertEquals(levenshtein_distance('abcd', 'bcd'), 1)
        self.assertEquals(levenshtein_distance('abcd', 'cd'),  2)
        self.assertEquals(levenshtein_distance('abcd', 'd'),   3)
        self.assertEquals(levenshtein_distance('abcd', ''),    4)
        
        
class ReduceRractionTestCase(unittest.TestCase):
    def testSimple(self):
        self.assertEquals(reduce_fraction(624, 352),   (39, 22))
        self.assertEquals(reduce_fraction(1920, 1080), (16, 9))
        self.assertEquals(reduce_fraction(1920, 720),  (8, 3))


if __name__ == '__main__':
    unittest.main()




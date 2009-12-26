#!/usr/bin/env python


import unittest


from lilyplayer.utils.arguments import PrefixArg, FloatArg, IntArg, TimeArg, StrArg, EnumArg
from lilyplayer.utils.arguments import Cmd, CmdNotFound


# TODO: tests for *Arg and parsing


class VerseTestCase(unittest.TestCase):
    def test1Types(self):
        class T:
            cmd = Cmd()
            @cmd()
            def a(self):
                pass
        
        t = T()
        
        self.assert_(hasattr(t, 'cmd'))
        
        self.assert_( 'a' in t.cmd )
        self.assert_( 'b' not in t.cmd )
        
        self.assertEquals( len(t.cmd['a']), 1)
        
        self.assert_( isinstance(t.cmd['a'], list) )
        self.assert_( isinstance(t.cmd['a'][0], (tuple, list)) )
        
        self.assert_( callable(t.cmd['a'][0][0]) )
        self.assert_( isinstance(t.cmd['a'][0][1], (tuple, list)) )
        
    def test2Names(self):
        class T:
            cmd = Cmd()
            @cmd(1)
            def foo_bar(self):
                pass
            @cmd(1)
            def foo_bar__baz(self):
                pass
            @cmd('baz#2', 1)
            def qwerty(self):
                pass
            @cmd('baz#2', 1)
            def asdf(self):
                pass
            
        t = T()
        
        self.assertEquals( len(t.cmd['foo-bar']), 2)
        self.assertEquals( len(t.cmd['baz#2']),   2)
        
    def test3Params(self):
        class T:
            cmd = Cmd()
            @cmd(1,2,3)
            def a(self):
                pass
            @cmd(True, False, None)
            def b(self):
                pass
        
        t = T()
        
        self.assertEquals( t.cmd['a'][0][1], (1,2,3) )
        self.assertEquals( t.cmd['b'][0][1], (True, False, None) )
        
    def test4Params(self):
        class T:
            cmd = Cmd()
            @cmd(IntArg(), IntArg())
            def a(self):
                pass
            @cmd(IntArg())
            def b(self):
                pass
        
        t = T()
        
        self.assertEquals( t.cmd.parse('a 123 456')[1], [123, 456] )
        self.assertEquals( t.cmd.parse('b 144')[1], [144] )
        
        
        
        self.assertRaises(CmdNotFound, t.cmd.parse, 'a foo bar')
        self.assertRaises(CmdNotFound, t.cmd.parse, 'a 123')
        self.assertRaises(CmdNotFound, t.cmd.parse, 'a')
        
        self.assertRaises(CmdNotFound, t.cmd.parse, 'b foo bar')
        self.assertRaises(CmdNotFound, t.cmd.parse, 'b 123 456')
        self.assertRaises(CmdNotFound, t.cmd.parse, 'b foo')
        self.assertRaises(CmdNotFound, t.cmd.parse, 'b')

        self.assertRaises(CmdNotFound, t.cmd.parse, 'x')        

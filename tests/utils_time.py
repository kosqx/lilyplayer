#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest


from lilyplayer.utils.play_time import Time


class TimeTestCase(unittest.TestCase):
    def testFormat(self):
        # ToDo: more asserts
        time0 = Time()
        time1 = Time(h=1, m=2, s=3, ms=456)

        self.assertEquals(time1.format("foobar"), "foobar")
        self.assertEquals(time1.format("foo%%bar"), "foo%bar")
        self.assertEquals(time1.format("%%"), "%")

        self.assertEquals(time1.format("%h"), "1")
        self.assertEquals(time1.format("%0h"), "1")
        self.assertEquals(time1.format("%1h"), "1")
        self.assertEquals(time1.format("%2h"), "01")
        self.assertEquals(time1.format("%3h"), "001")

        self.assertEquals(time0.format("%0h"), "")
        self.assertEquals(time0.format("%1h"), "0")
        self.assertEquals(time0.format("%2h"), "00")
        self.assertEquals(time0.format("%3h"), "000")

        self.assertEquals(time1.format("%m"), "2")
        self.assertEquals(time1.format("%2m"), "02")

        self.assertEquals(time1.format("%s"), "3")
        self.assertEquals(time1.format("%2s"), "03")

    def testParse(self):
        self.assertEquals(Time(h=1, m=2, s=3, ms=456), Time.parse('1:2:3.456'))

        self.assertEquals(Time(h=0, m=2, s=3, ms=456), Time.parse(':2:3.456'))
        self.assertEquals(Time(h=0, m=2, s=3, ms=456), Time.parse('2:3.456'))

        self.assertEquals(Time(h=1, m=0, s=3, ms=456), Time.parse('1::3.456'))
        self.assertEquals(Time(h=0, m=0, s=3, ms=456), Time.parse(':3.456'))
        self.assertEquals(Time(h=0, m=0, s=3, ms=456), Time.parse('3.456'))

        self.assertEquals(Time(h=1, m=2, s=0, ms=456), Time.parse('1:2:.456'))
        self.assertEquals(Time(h=1, m=0, s=0, ms=456), Time.parse('1::.456'))
        self.assertEquals(Time(h=0, m=0, s=0, ms=456), Time.parse('0:0:.456'))
        self.assertEquals(Time(h=0, m=0, s=0, ms=456), Time.parse(':0:.456'))
        self.assertEquals(Time(h=0, m=0, s=0, ms=456), Time.parse('0::.456'))

        self.assertEquals(Time(h=0, m=0, s=0, ms=456), Time.parse('.456'))
        self.assertEquals(Time(h=0, m=0, s=0, ms=456), Time.parse(',456'))

        self.assertEquals(Time(h=0, m=0, s=1234, ms=456), Time.parse('1234,456'))

        self.assertEquals(Time(h=0, m=0, s=0, ms=0), Time.parse(''))

        self.assertEquals(Time(h=1, m=2, s=3), Time.parse('1:2:3,'))
        self.assertEquals(Time(h=1, m=2, s=3), Time.parse('1:2:3'))
        self.assertEquals(Time(h=1, m=2, s=3), Time.parse('3723'))
        self.assertEquals(Time(h=0, m=2, s=3), Time.parse('2:3'))
        self.assertEquals(Time(h=1, m=0, s=3), Time.parse('1::3'))
        self.assertEquals(Time(h=0, m=0, s=3), Time.parse('::3'))
        self.assertEquals(Time(h=0, m=0, s=3), Time.parse(':3'))
        self.assertEquals(Time(h=0, m=0, s=3), Time.parse('3'))

        self.assertRaises(ValueError, Time.parse, 'ala has a cat')
        self.assertRaises(ValueError, Time.parse, '1.3:2')
        self.assertRaises(ValueError, Time.parse, None)

if __name__ == '__main__':
    unittest.main()


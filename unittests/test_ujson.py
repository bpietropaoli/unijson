"""
Copyright (c) 2018 Bastien Pietropaoli

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import absolute_import
import unittest
import datetime, pytz

# Relative import from parent directory as found here:
# https://gist.github.com/JungeAlexander/6ce0a5213f3af56d7369
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import ujson, json


#########################################################################################
#########################################################################################
#########################################################################################


# -------------
# Test classes:
# -------------

class NothingDefined(object):
    def __init__(self, a1, a2):
        self.a1 = a1
        self.a2 = a2
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    def __ne__(self, other):
        return not self.__eq__(other)


class DefineEncoder(object):
    def __init__(self, a1, a2):
        self.a1 = a1
        self.a2 = a2
    def __json_encode__(self):
        return {"a1":self.a1, "a2":self.a2, "source":"__json_encode__"}
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    def __ne__(self, other):
        return not self.__eq__(other)


class DefineDecoder(object):
    def __init__(self, a1, a2):
        self.a1 = a1
        self.a2 = a2
        self.source = ""
    @staticmethod
    def __json_decode__(d):
        o = DefineDecoder(**d)
        o.source = "__json_decode__"
        return o
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    def __ne__(self, other):
        return not self.__eq__(other)


class DefineBoth(object):
    def __init__(self, a1, a2):
        self.a1 = a1
        self.a2 = a2
    def __json_encode__(self):
        return {"a1":self.a1, "a2":self.a2}
    @staticmethod
    def __json_decode__(d):
        return DefineBoth(d["a1"], d["a2"])
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    def __ne__(self, other):
        return not self.__eq__(other)


#########################################################################################
#########################################################################################
#########################################################################################


class TestUJSON(unittest.TestCase):

    def test_encoder(self):
        # Test already supported types:
        d = {"peuh":12}
        expected = '{"peuh": 12}'
        self.assertEqual(ujson.dumps(d), expected)
        self.assertEqual(ujson.dumps(d), json.dumps(d))

        l = [False, True, None, ("Well", "I test thoroughly")]
        expected = '[false, true, null, ["Well", "I test thoroughly"]]'
        self.assertEqual(ujson.dumps(l), expected)
        self.assertEqual(ujson.dumps(l), json.dumps(l))

        # Test custom classes:
        o = NothingDefined(12, 55789)
        s = ujson.dumps(o)
        d = json.loads(s)
        expected = {"__module__": "test_ujson", "__class__": "NothingDefined", "a1": 12, "a2": 55789}
        self.assertDictEqual(d, expected)

        o = DefineEncoder(1643, NothingDefined("sgfd", [12, False, True, "peuh"]))
        s = ujson.dumps(o)
        d = json.loads(s)
        expected = {"__module__": "test_ujson", "__class__": "DefineEncoder", "a1": 1643,
                    "a2": {"__module__": "test_ujson", "__class__": "NothingDefined", "a1": "sgfd",
                            "a2": [12, False, True, "peuh"]}, "source":"__json_encode__"}
        self.assertDictEqual(d, expected)

        # Test datetime types: (also testing that registering methods actually works)
        o = pytz.timezone("UTC")
        s = ujson.dumps(o)
        d = json.loads(s)
        expected = {"__module__":"pytz", "__class__":"timezone", "zone":"UTC"}
        self.assertDictEqual(d, expected)

        o = datetime.date(2018, 8, 13)
        s = ujson.dumps(o)
        d = json.loads(s)
        expected = {"__module__":"datetime", "__class__":"date", "year":2018, "month":8, "day":13}
        self.assertDictEqual(d, expected)

        o = datetime.datetime(2018, 8, 13, 18, 53, 42, tzinfo=pytz.timezone("Europe/Dublin"))
        s = ujson.dumps(o)
        d = json.loads(s)
        expected = {"__module__":"datetime", "__class__":"datetime", "year":2018, "month":8, "day":13,
                    "hour":18, "minute":53, "second":42, "microsecond":0, "tzinfo":{"__module__":"pytz",
                    "__class__":"timezone", "zone":"Europe/Dublin"}}
        self.assertDictEqual(d, expected)

        o = datetime.time(18, 53, 42)
        s = ujson.dumps(o)
        d = json.loads(s)
        expected = {"__module__":"datetime", "__class__":"time", "hour":18, "minute":53, "second":42,
                    "microsecond":0, "tzinfo":None}
        self.assertDictEqual(d, expected)

        o = datetime.timedelta(seconds=3672)
        s = ujson.dumps(o)
        d = json.loads(s)
        expected = {"__module__":"datetime", "__class__":"timedelta", "seconds":3672}
        self.assertDictEqual(d, expected)


    def test_decoder(self):
        # Test already supported types:
        s = '{"peuh":12}'
        o = ujson.loads(s)
        expected = {"peuh":12}
        self.assertDictEqual(o, expected)
        self.assertDictEqual(o, json.loads(s))

        s = '[false, true, null, ["Well", "I test thoroughly"]]'
        o = ujson.loads(s)
        expected = [False, True, None, ["Well", "I test thoroughly"]]
        self.assertEqual(o, expected)
        self.assertEqual(o, json.loads(s))

        # Test custom classes:
        s = '{"__module__": "test_ujson", "__class__": "NothingDefined", "a1": 12, "a2": 55789}'
        o = ujson.loads(s)
        expected = NothingDefined(12, 55789)
        self.assertEqual(o, expected)

        s = '{"__module__":"test_ujson", "__class__":"DefineDecoder", "a1":12, "a2":55789}'
        o = ujson.loads(s)
        expected = DefineDecoder(12, 55789)
        expected.source = "__json_decode__"
        self.assertEqual(o, expected)

        s = '''{"a1": 1643, "a2": {"a1": "sgfd", "a2": [12, false, true, "peuh"], "__class__": "NothingDefined",
                "__module__": "test_ujson"}, "__class__": "DefineDecoder", "__module__": "test_ujson"}'''
        o = ujson.loads(s)
        expected = DefineDecoder(1643, NothingDefined("sgfd", [12, False, True, "peuh"]))
        expected.source = "__json_decode__"
        self.assertEqual(o, expected)

        # Test the datetime types:
        s = '{"__module__":"pytz", "__class__":"timezone", "zone":"UTC"}'
        o = ujson.loads(s)
        expected = pytz.timezone("UTC")
        self.assertEqual(o, expected)

        s = '{"__module__":"datetime", "__class__":"date", "year":2018, "month":8, "day":13}'
        o = ujson.loads(s)
        expected = datetime.date(2018, 8, 13)
        self.assertEqual(o, expected)

        s = '''{"__module__":"datetime", "__class__":"datetime", "year":2018, "month":8, "day":13,
                "hour":18, "minute":53, "second":42, "microsecond":0, "tzinfo":{"__module__":"pytz",
                "__class__":"timezone", "zone":"Europe/Dublin"}}'''
        o = ujson.loads(s)
        expected = datetime.datetime(2018, 8, 13, 18, 53, 42, tzinfo=pytz.timezone("Europe/Dublin"))

        s = '''{"__module__":"datetime", "__class__":"time", "hour":18, "minute":53, "second":42,
                "microsecond":0, "tzinfo":null}'''
        o = ujson.loads(s)
        expected = datetime.time(18, 53, 42)
        self.assertEqual(o, expected)

        s = '{"__module__":"datetime", "__class__":"timedelta", "seconds":3672}'
        o = ujson.loads(s)
        expected = datetime.timedelta(seconds=3672)
        self.assertEqual(o, expected)


    def test_serialiser(self):
        # Test equality of various objects before and after
        # a round of encoding and decoding.
        o = {"peuh": 12, "pouet":[False, True, None, ["Well", "I test thoroughly"]]}
        self.assertEqual(o, ujson.loads(ujson.dumps(o)))

        o = NothingDefined(12, 55789)
        self.assertEqual(o, ujson.loads(ujson.dumps(o)))

        o = DefineBoth("fduhghdgg", [None, "sdifj", 12, False, True])
        self.assertEqual(o, ujson.loads(ujson.dumps(o)))

        for tz in pytz.all_timezones:
            o = pytz.timezone(tz)
            self.assertEqual(o, ujson.loads(ujson.dumps(o)))

        o = datetime.date(2018, 8, 13)
        self.assertEqual(o, ujson.loads(ujson.dumps(o)))

        o = datetime.datetime(2018, 8, 13, 18, 53, 42, tzinfo=pytz.timezone("Europe/Dublin"))
        self.assertEqual(o, ujson.loads(ujson.dumps(o)))

        o = datetime.time(18, 53, 42)
        self.assertEqual(o, ujson.loads(ujson.dumps(o)))

        o = datetime.timedelta(seconds=3672)
        self.assertEqual(o, ujson.loads(ujson.dumps(o)))


#########################################################################################
#########################################################################################
#########################################################################################


if __name__ == "__main__":
    unittest.main()

'''
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
'''

import json, unijson


###################################################################################################
# unijson for already supported types:
d = {"peuh": 123, "pouet": [True, False, None, "ruguhregr"]}

# Both will return the same string:
json.dumps(d)
unijson.dumps(d)


###################################################################################################
# unijson for custom classes:

# Define a custom class
class Test(object):
    def __init__(self, a1, a2):
        self.a1, self.a2 = a1, a2

o1 = Test(12, 34)

# json.dumps(o1) would raise an exception.
# TypeError: Object of type 'Test' is not JSON serializable

# unijson won't blink:
unijson.dumps(o1) # {"a1": 12, "a2": 34, "__class__": "Test", "__module__": "examples"}


###################################################################################################
# Define __json_encode__() and __json_decode__():

# Define a custom class that defines methods for the universal serialiser:
class DefineMethods(object):
    def __init__(self, a1, a2):
        self.a1, self.a2 = a1, a2

    def __json_encode__(self):
        return {"a1":self.a1, "a2":self.a2, "extra":"for the fun"}

    @staticmethod
    def __json_decode__(d):
        return DefineMethods(d["a1"], d["a2"])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

o = DefineMethods("whatever", False)
s = unijson.dumps(o) # '{"a1": "whatever", "a2": false, "extra": "for the fun", "__class__": "DefineMethods", "__module__": "examples"}'
d = unijson.loads(s) # o == d should be True


###################################################################################################
# Register a new encoder:

def json_encode_date(d):
    """Encoder for dates (from module datetime)."""
    return {"day"   : d.day,
            "month" : d.month,
            "year"  : d.year}
UniversalJSONEncoder.register(datetime.date, json_encode_date)

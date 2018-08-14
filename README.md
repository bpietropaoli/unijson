# Universal JSON Encoder/Decoder for Python Objects #

This small Python package enables encoding / decoding most Python objects into / from JSON. It offers an API similar to the `json` standard library package but provides automated functionalities to encode / decode most objects that cannot be converted into JSON by default (e.g. datetimes or custom classes). To do this, it adds two properties `__class__` and `__module__` to the generated JSON for all types normally not supported.

The rationale for this package is pretty simple: I like to be able to dump/load my objects in an easily readable format pretty much anywhere (e.g. a DB, another program, another Python program). This is particularly practical to use with applications using MongoDB.

This package works with Python version 2.7, 3.4, 3.5, 3.6 and 3.7 (the unit tests passed for all those versions). To install it, clone the git and simply use `python setup.py install` OR you can also install it via `pip install unijson` since it's also registered on PyPi [here](https://pypi.org/project/unijson/).

Here is what you can do with this little package.

## The types already supported by `json` are unchanged ##

All the types already supported by `json` are supported by `unijson` and behave in the exact same way since `UniversalJSONEncoder` uses the default `JSONEncoder` for all the types already supported.

```python
import json, unijson

d = {"peuh": 123, "pouet": [True, False, None, "ruguhregr"]}

# Both will return the same string:
json.dumps(d)
unijson.dumps(d)
```

## Automatically find a way to encode your custom classes ##

Using `unijson`, converting your custom classes instances into JSON objects has never been more simple.
For most simple classes, the `UniversalJSONEncoder` will find a way to transform them into JSON compliant objects without the need for extra methods.

```python
# Define a custom class
class Test(object):
    def __init__(self, a1, a2):
        self.a1, self.a2 = a1, a2

o1 = Test(12, 34)

# json.dumps(o1) would raise an exception.
# TypeError: Object of type 'Test' is not JSON serializable

# unijson won't blink:
unijson.dumps(o1) # {"a1": 12, "a2": 34, "__class__": "Test", "__module__": "examples"}
```

## Define encoders / decoders for your custom classes ##

With `unijson`, providing encoding / decoding functions for your custom classes is really simple. You just implement `__json_encode__()` / `__json_decode__()` in your custom classes. They will then be taken into account automatically by the `UniversalJSONEncoder` / `UniversalJSONDecoder`. This can be used to add some extra information into the resulting JSON object, or to provide a way to transform complex object into a JSON-serialisable dictionnary.

```python
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
```

Here is what you need to know on the two methods illustrated above:
* `__json_encode__()`: should take no argument and return a dictionary of unijson-serialisable objects (remember that many objects are unijson-serialisable by default!).
* `__json_decode__()`: should be static, take a single argument (a dict), and return an instance of the class it's defined in.

## Define and register encoders / decoders for any class ##

If you use external libraries, or non-JSON-serialisable types from the standard library (e.g. datetime), you might find yourself stuck on a simple way to convert those objects into JSON. Worry no more, my friend, for `unijson` has a solution for that. You can register encoding / decoding functions to the `UniversalJSONEncoder` / `UniversalJSONDecoder` to specify how to encode / decode anything. `unijson` already offers a few extra encoders / decoders for all the types found in `datetime` and `pytz` (for the management of timezones). If you have a look at `unijson`'s code, you will find those encoders. Here is an example that demonstrates how to register encoding functions:

```python
#Encoding function:
def json_encode_date(d):
    """Encoder for dates (from module datetime)."""
    return {"day"   : d.day,
            "month" : d.month,
            "year"  : d.year}
UniversalJSONEncoder.register(datetime.date, json_encode_date)
# Won't even require a decoding function since the created dictionnary can be used as arguments to the constructor (that's one of the automated methods used by UniversalJSONDecoder to build objects).
```

If you want to add your own encoders / decoders and register them, the functions you register must do the following:
* encoders should take single argument (the object to encode) and return a dictionary of UniJSON-serialisable objects.
* decoders should take a single argument (the dict extracted by the decoder) and return an instance of the decoded object.

# Additional information #

Author: Bastien Pietropaoli

Contact: bastien.pietropaoli@gmail.com

License: [Apache v2.0](http://www.apache.org/licenses/LICENSE-2.0)

If you have suggestions, remarks, or questions, do not hesitate to contact me.
Also, if you have made nice encoders/decoders that you think could be a good addition to this package, feel free to submit a pull request.

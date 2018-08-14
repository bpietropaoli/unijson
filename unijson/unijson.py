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
import sys, warnings

# Core features:
import json
import types, importlib, re, __main__

# Convertible types:
import datetime, pytz
# Used to parse datetimes/dates/times:
import parse


#########################################################################################
#########################################################################################
#########################################################################################


# ------------------------------------------------
# API similar to the standard library json package
# ------------------------------------------------


def dumps(obj, **kwargs):
    """
    Serialise a given object into a JSON formatted string. This function
    uses the `UniversalJSONEncoder` instead of the default JSON encoder
    provided in the standard library. Takes the same keyword arguments as
    `json.dumps()` except for `cls` that is used to pass our custom encoder.
    Args:
        obj (object): The object to serialise.
        kwargs (**): Keyword arguments normally passed to `json.dumps()` except
            for `cls`. Unpredictable behaviour might occur if `cls` is passed.
    Return:
        str - The object serialised into a JSON string.
    """
    return json.dumps(obj, cls = UniversalJSONEncoder, **kwargs)


def dump(obj, fp, **kwargs):
    """
    Serialise a given object into a JSON formatted file / stream. This function
    uses the `UniversalJSONEncoder` instead of the default JSON encoder provided
    in the standard library. Takes the same keyword arguments as `json.dump()`
    except for `cls` that is used to pass our custom encoder.
    Args:
        obj (object): The object to serialise.
        fp (file-like object): A .write()-supporting file-like object.
        kwargs (**): Keyword arguments normally passed to `json.dump()` except
            for `cls`. Unpredictable behaviour might occur if `cls` is passed.
    """
    json.dump(obj, fp, cls = UniversalJSONEncoder, **kwargs)


def loads(s, **kwargs):
    """
    Deserialise a given JSON formatted str into a Python object using the
    `UniversalJSONDecoder`. Takes the same keyword arguments as `json.loads()`
    except for `cls` that is used to pass our custom decoder.
    Args:
        s (str): The JSON formatted string to decode.
        kwargs (**): Keyword arguments normally passed to `json.loads()` except
            for `cls`. Unpredictable behaviour might occur if `cls` is passed.
    Return:
        object - A Python object corresponding to the provided JSON formatted string.
    """
    return json.loads(s, cls = UniversalJSONDecoder, **kwargs)


def load(fp, **kwargs):
    """
    Deserialise a given JSON formatted stream / file into a Python object using
    the `UniversalJSONDecoder`. Takes the same keyword arguments as `json.load()`
    except for `cls` that is used to pass our custom decoder.
    Args:
        fp (file-like object): A .write()-supporting file-like object.
        kwargs (**): Keyword arguments normally passed to `json.load()` except
            for `cls`. Unpredictable behaviour might occur if `cls` is passed.
    Return:
        object - A Python object corresponding to the provided JSON formatted stream / file.
    """
    return json.load(fp, cls = UniversalJSONDecoder, **kwargs)


#########################################################################################
#########################################################################################
#########################################################################################


# ----------------------------
# Universal encoder / decoder:
# ----------------------------


class UniversalJSONEncoder(json.JSONEncoder):
    """
    A universal JSON encoder for Python objects. This encoder will work with
    simple custom objects by default and can automatically take into account methods
    `__json_encoder__()` defined in custom classes if implemented correctly. Those
    methods should return a dictionnary (with only strings as keys) and take only
    `self` as an argument.

    In addition, it is possible to register functions for types over which you have
    no control (standard / external library types). For this, use static method
    `UniversalJSONEncoder.register()`.

    The encoder adds attributes `__module__` and `__class__` to the resulting JSON
    objects to enable the identification of the object from which they were constructed.
    They both can be added directly into your encoder to use the same encoder for
    multiple objects (by setting it to a superclass for instance). See the encoders
    for timezones for an example of this. If your encoder already sets them, then they
    won't be modified in this universal encoder. Your values will stay.

    How to use this class:
        `json.dumps(obj, cls=UniversalJSONEncoder)`
                        OR
        `unijson.dumps(obj)`
    """
    # The registered encoding functions:
    _encoders = {}

    @staticmethod
    def register(obj_type, encoding_function):
        """
        Register a function as an encoder for the provided type/class. The provided
        encoder should take a single argument (the object to serialise) and return
        a JSON serialisable dictionnary (by the standard of this serialiser).
        Passing a new encoding function to a type already registered will overwrite
        the previously registered encoding function.
        Args:
            type (obj_type): The type to be encoded by the provided encoder. Can be
                easily obtained by simply providing a class directly.
            encoding_function (function): The function to use as an encoder for the
                provided type. Takes a single argument, a returns a dictionnary.
        """
        if not isinstance(obj_type, type):
            raise ValueError("Expected a type/class, a %s was passed instead." % type(obj_type))
        if not callable(encoding_function):
            raise ValueError("Expected a function, a %s was passed instead." % type(encoding_function))

        UniversalJSONEncoder._encoders[obj_type] = encoding_function


    def default(self, obj):
        """
        Extends the default behaviour of the default JSON encoder. It will try
        the different methods to encode the provided object in the following order:
         - Default JSON encoder (for known types)
         - Registered encoding function (if one is found)
         - `__json_encode__()` as provided by the custom class (if it's found)
         - Use the default __dict__ property of the object (for custom classes)
        Args:
            obj (object): The object to serialise.
        Return:
            dict - A dictionnary of JSON serialisable objects.
        Raises:
            TypeError - If none of the methods worked.
        """
        # Default JSON encoder:
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            pass

        already_encoded = False

        # Use a registered encoding function:
        if type(obj) in UniversalJSONEncoder._encoders:
            try:
                d = UniversalJSONEncoder._encoders[type(obj)](obj)
                already_encoded = True
            except:
                warnings.warn("Encoding function %s used for type %s raised an exception. Trying something else." % \
                    (UniversalJSONEncoder._encoders[type(obj)].__name__, type(obj)))

        # Trying to use __json_encode__():
        if not already_encoded:
            try:
                d = obj.__json_encode__()
                already_encoded = True
            except AttributeError: # No method __json_encode__() found
                pass
            except:
                warnings.warn("Method __json_encode__() used for type %s raised an exception. Trying something else." % \
                    type(obj))

        # Trying the default __dict__ attribute:
        if not already_encoded:
            try:
                d = dict(obj.__dict__)
                already_encoded = True
            except AttributeError: pass

        # If nothing worked, raise an exception like the default JSON encoder would:
        if not already_encoded:
            raise TypeError("Type %s is not JSON serializable." % type(obj))

        # Add the metadata used to reconstruct the object (if necessary):
        if "__class__" not in d: d["__class__"] = str(obj.__class__.__name__)
        if "__module__" not in d: d["__module__"] = _get_object_module(obj)

        return d


#########################################################################################


class UniversalJSONDecoder(json.JSONDecoder):
    """
    A universal JSON decoder for Python objects. To be used with JSON strings created
    using the `UniversalJSONEncoder`. Will use static methods `__json_decode__()` if
    provided in your custom classes. It will use the default JSON decoder whenever
    possible and then try multiple techniques to decode the provided objects.

    In addition, it is possible to register functions for types over which you have
    no control (standard / external library types). For this, use static method
    `UniversalJSONDecoder.register()`.

    How to use this class:
        `json.loads(s, cls=UniversalJSONDecoder)`
                        OR
        `unijson.loads(s)`
    """
    # The registered decoding functions:
    _decoders = {}

    @staticmethod
    def register(obj_type, decoding_function):
        """
        Register a function as a decoder for the provided type/class. The provided
        decoder should take a single argument (the raw dict to deserialise) and return
        an instance of that object.
        Passing a new decoding function to a type already registered will overwrite
        the previously registered decoding function.
        Args:
            type (obj_type): The type to be decoded by the provided decoder. Can be
                easily obtained by simply providing a class directly.
            decoding_function (function): The function to use as a decoder for the
                provided type. Takes a single argument, a returns an object.
        """
        if not isinstance(obj_type, type):
            raise ValueError("Expected a type/class, a %s was passed instead." % type(obj_type))
        if not callable(decoding_function):
            raise ValueError("Expected a function, a %s was passed instead." % type(decoding_function))

        UniversalJSONDecoder._decoders[obj_type] = decoding_function


    # Required to redirect the hook for decoding.
    def __init__(self, *args, **kwargs):
        """Constructor redirecting the hook for decoding JSON objects."""
        json.JSONDecoder.__init__(self, object_hook=self.universal_decoder, *args, **kwargs)


    def universal_decoder(self, d):
        """
        Universal decoder for JSON objects encoded using the UniversalJSONEncoder.
        It will try the following methods in order:
         - Default JSON encoder (for known types)
         - Registered encoding function (if one is found)
         - `__json_encode__()` as provided by the custom class (if it's found)
         - Use a constructor taking as argument the raw dictionary
         - Use the default constructor and replace the __dict__ property of the
           object (for custom classes)
        Args:
            d (dict): A raw dictionnary obtained from the JSON string to be made
                into a beautiful Python object.
        Return:
            object - A Python object corresponding to the provided JSON object. If
                nothing could be done for that object, the raw dictionary is returned
                as is.
        """
        # Base object:
        if "__class__" not in d:
            return d

        # Get the class and module of the object:
        cls = d.pop("__class__")
        mod = d.pop("__module__")

        # Import the necessary module if not already imported:
        # (necessary to retrieve the class as an attribute of the module)
        all_mods = _get_imported_modules()
        if mod not in all_mods:
            m = importlib.import_module(mod)
            c = getattr(m, cls)
        else:
            c = getattr(all_mods[mod], cls)

        # Registered decoder if any:
        if c in UniversalJSONDecoder._decoders:
            try:
                return UniversalJSONDecoder._decoders[c](d)
            except:
                warnings.warn("Decoding function %s used for type %s raised an exception. Trying something else." % \
                    (UniversalJSONDecoder._decoders[c].__name__, c))

        # __json_decode__() static method if any:
        try:
            return getattr(c, "__json_decode__")(d)
        except AttributeError:
            pass
        except:
            warnings.warn("Static method __json_deconde__ used for type %s raised an exception. Trying something else." % c)

        # Try the constructor with the dictionary as arguments:
        try:
            return c(**d)
        except:
            pass

        # Try the default constructor (no arguments)
        # and replace __dict__
        try:
            o = c()
            o.__dict__ = d
            return o
        except:
            pass

        # Default, return the raw dict:
        return d


#########################################################################################
#########################################################################################
#########################################################################################


# --------------------------------
# Some useful encoders / decoders:
# --------------------------------


def json_encode_timezone(t):
    """Encoder for timezones (from pytz)."""
    return {"zone" : t.zone, "__class__" : "timezone", "__module__":"pytz"}
UniversalJSONEncoder.register(pytz.tzinfo.BaseTzInfo, json_encode_timezone)
UniversalJSONEncoder.register(pytz.tzinfo.DstTzInfo, json_encode_timezone)
UniversalJSONEncoder.register(pytz.tzinfo.StaticTzInfo, json_encode_timezone)
# Register all timezones since they all have various classes and whatever all that mess is:
for tz in pytz.all_timezones:
    UniversalJSONEncoder.register(type(pytz.timezone(tz)), json_encode_timezone)
# Won't need a decoder since I use `timezone` instead of the classes.

#########################################################################################

def json_encode_date(d):
    """Encoder for dates (from module datetime)."""
    return {"date" : str(d)}
UniversalJSONEncoder.register(datetime.date, json_encode_date)

def json_decode_date(d):
    """Decoder for dates (from module datetime)."""
    p = parse.parse("{year:d}-{month:d}-{day:d}", d["date"])
    return datetime.date(p["year"], p["month"], p["day"])
UniversalJSONDecoder.register(datetime.date, json_decode_date)

#########################################################################################

def json_encode_datetime(d):
    """Encoder for datetimes (from module datetime)."""
    return {"datetime" : d.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "tzinfo"   : d.tzinfo}
UniversalJSONEncoder.register(datetime.datetime, json_encode_datetime)

def json_decode_datetime(d):
    """Decoder for datetimes (from module datetime)."""
    return datetime.datetime.strptime(d["datetime"], "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=d["tzinfo"])
UniversalJSONDecoder.register(datetime.datetime, json_decode_datetime)

#########################################################################################

def json_encode_time(t):
    """Encoder for times (from module datetime)."""
    return {"time"   : t.strftime("%H:%M:%S.%f"),
            "tzinfo" : t.tzinfo}
UniversalJSONEncoder.register(datetime.time, json_encode_time)

def json_decode_time(d):
    """Decoder for times (from module datetime)."""
    p = parse.parse("{hh:d}:{mm:d}:{ss:d}.{ms:d}", d["time"])
    return datetime.time(p["hh"], p["mm"], p["ss"], p["ms"], tzinfo=d["tzinfo"])
UniversalJSONDecoder.register(datetime.time, json_decode_time)

#########################################################################################

def json_encode_timedelta(t):
    """Encoder for timedeltas (from module datetime)."""
    return {"seconds" : t.total_seconds()}
UniversalJSONEncoder.register(datetime.timedelta, json_encode_timedelta)
# Won't require a decoder since "seconds" will be automatically passed to a constructor.


#########################################################################################
#########################################################################################
#########################################################################################


# -----------------------------------
# Dark magic you probably don't need:
# -----------------------------------


def _get_object_module(obj):
    """
    Get the name of the module from which the given object was created.
    Args:
        obj (object): Any object.
    Return:
        str - The name of the module from which the given object was created.
    """
    try:
        r = str(obj.__module__)
    except AttributeError:
        r = _get_type_module(obj.__class__)
    if r == "__main__":
        r = __main__.__file__[:-3] # Prevents having __main__ as a module.
    return r

    # Remark 1: Builtin objects don't have a __module__ attribute.
    # Remark 2: inspect.getmodule(obj) should work but it doesn't.


# Expressions used to find module names:
__class_expression = re.compile(r"^<class '([a-zA-Z0-9._]*)'>")
__type_expression  = re.compile(r"^<type '([a-zA-Z0-9._]*)'>")

def _get_type_module(t):
    """
    Get the name of the module containing the given type.
    Args:
        t (type): The type for which the module is requested.
    Return:
        str - The name of the module containing the given type.
    """
    # 1) Extract the name of the module from str(type).
    # 2) Get the chain of submodules separated by dots.
    # 3) Join them together while getting rid of the last one.
    try:
        return ".".join(__class_expression.search(str(t)).group(1).split(".")[:-1])
    except AttributeError: # A type instead of a class
        return ".".join(__type_expression.search(str(t)).group(1).split(".")[:-1])


def _get_imported_modules():
    """
    Get all the already imported modules.
    Found here: http://stackoverflow.com/a/4858123/5321016
    Return:
        dict[str:module] - A dictionary of the already imported modules.
            Keys are modules' names.
    """
    result = {}
    for name, val in (globals().items() if sys.version_info[0] == 3 else
                      globals().iteritems()): # Python 2 and 3 compatible dict iteration
        if isinstance(val, types.ModuleType):
            result[val.__name__] = val
    return result

# unijson - Changelog #

The aim of this file is to track the various changes that have / will occur in the development of this package. This is supposed to be human readable. For that purpose, the [Keep a CHANGELOG](https://keepachangelog.com/en/1.0.0/) is used. Moreover, this package adheres to [Semantic Versioning](http://semver.org/).

# CHANGELOG

## [1.0.0] - 2018-08-13

First release of the package. Here is what if offers:
* A `json`-like API with the same `dumps()` / `loads()` functions with extended functionalities.
* A `UniversalJSONEncoder` and a `UniversalJSONDecoder` class for everyone to use and extend.
* An easy way to provide encoders / decoders by simply adding the `__json_encode__()` method and `__json_decode__()` static method to your classes.
* An easy way to register new encoders / decoders when working with standard library and external libraries types.

"""
Installer for the ujson Python package.
Do not modify.
"""

from setuptools import setup, find_packages
import re, os

def get_version():
    """
    Extracts the version number from a version file.
    Found here: https://milkr.io/kfei/5-common-patterns-to-version-your-Python-package
    """
    VERSIONFILE = os.path.join('ujson', '__init__.py')
    initfile_lines = open(VERSIONFILE, 'rt').readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError("Unable to find version string in %s." % VERSIONFILE)


# Setup configuration
setup(name = "ujson",
      version = get_version(),
      url = "",
      author = "Bastien Pietropaoli",
      author_email = "bastien.pietropaoli@gmail.com",
      description = "Universal JSON Encoder/Decoder for Python objects",
      license = "Apache v2.0",
      packages = find_packages(),
      install_requires = [
        "pytz"  # For timezones management in datetimes
      ],
      zip_safe = False)

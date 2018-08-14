"""
Installer for the unijson Python package.
Do not modify.
"""


from setuptools import setup, find_packages
import re, os


with open("README.md", "r") as fh:
    long_description = fh.read()


def get_version():
    """
    Extracts the version number from a version file.
    Found here: https://milkr.io/kfei/5-common-patterns-to-version-your-Python-package
    """
    VERSIONFILE = os.path.join('unijson', '__init__.py')
    initfile_lines = open(VERSIONFILE, 'rt').readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError("Unable to find version string in %s." % VERSIONFILE)


# Setup configuration
setup(name = "unijson",
      version = get_version(),
      url = "https://github.com/bpietropaoli/unijson",
      author = "Bastien Pietropaoli",
      author_email = "bastien.pietropaoli@gmail.com",
      description = "Universal JSON encoder/decoder for Python objects",
      long_description=long_description,
      long_description_content_type="text/markdown",
      license = "Apache v2.0",
      packages = find_packages(),
      install_requires = [
        "pytz",  # For timezones management in datetimes
        "parse"  # For the parsing of dates and times
      ],
      classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities"
      ],
      zip_safe = False)

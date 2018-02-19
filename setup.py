#!/usr/bin/env python
# -*- coding: utf-8 -*-


description = """Villeneuve Lab PET Pipeline"""

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

from glob import glob
from setuptools import setup


DISTNAME = "vlpp"
DESCRIPTION = description
VERSION = "1.2.1"
AUTHOR = "Christophe Bedetti"
AUTHOR_EMAIL = "christophe.bedetti@umontreal.ca"
#URL = "https://github.com/"
#DOWNLOAD_URL = URL + "/archive/" + VERSION + ".tar.gz"
with open("requirements.txt", "r") as f:
    INSTALL_REQUIRES = f.read().splitlines()


if __name__ == "__main__":
    setup(
            name=DISTNAME,
            version=VERSION,
            description=description,
            long_description=long_description,
            author=AUTHOR,
            author_email=AUTHOR_EMAIL,
            #url=URL,
            #download_url=DOWNLOAD_URL,
            packages=[DISTNAME],
            #scripts=glob('scripts/*') + glob('pipelines/*.nf'),
            install_requires=INSTALL_REQUIRES,
            )

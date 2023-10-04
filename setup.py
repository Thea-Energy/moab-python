#!/usr/bin/env python

import glob
import os
import sys
from packaging import version
import numpy as np  # needed for numpy include paths
import Cython
from setuptools import setup, Extension, find_packages
from Cython.Distutils import build_ext

# make sure cython isn't too old
if version.parse(Cython.__version__) < version.parse("0.26"):
    sys.exit(
        "Cython version is old. Upgrade to Cython 0.29 using pip install cython==0.29.36 [--user]"
    )

# setup moab include paths
moab_root = "moab"
moab_source_include = moab_root + "/src/moab/"
moab_other_source_include = moab_root + "/src/"
moab_binary_include = "moab-build/src/"
moab_lib_path = "moab-build/lib/"
pymoab_src_dir = "moab/pymoab/pymoab"
include_paths = [
    moab_source_include,
    moab_other_source_include,
    moab_binary_include,
    np.get_include(),
    pymoab_src_dir,
]

moab_rpath = moab_lib_path

# set values for each module
ext_modules = []
for f in os.listdir(pymoab_src_dir):
    if f.endswith(".pyx"):
        fbase = f.split(".")[0]
        ext = Extension(
            "pymoab." + fbase,
            [
                "moab/pymoab/pymoab/" + f,
            ],
            language="c++",
            include_dirs=include_paths,
            runtime_library_dirs=[
                moab_rpath,
            ],
            library_dirs=[
                moab_lib_path,
            ],
            libraries=[
                "MOAB",
            ],
        )
        ext_modules.append(ext)

# setup pymoab
setup(
    name="pymoab",
    cmdclass={"build_ext": build_ext},
    ext_modules=ext_modules,
    package_dir={"": "moab/pymoab"},
    packages=["pymoab"],
    package_data={
        "pymoab": [
            "*.pxd",
        ]
    },
    version="5.5.0",
    author="Patrick Shriwise, Guilherme Caminha, Vijay Mahadevan, Iulian Grindeanu, Anthony Scopatz",
    author_email="moab-dev@mcs.anl.gov",
)

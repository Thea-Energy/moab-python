#!/usr/bin/env python

import os
import platform
import numpy as np  # needed for numpy include paths
import re
import subprocess
from setuptools import setup, Extension
from pathlib import Path
from Cython.Distutils import build_ext

# setup moab include paths
moab_root = "moab"
moab_source_include = moab_root + "/src/moab/"
moab_other_source_include = moab_root + "/src/"
moab_build_dir = "moab-build"
moab_binary_include = moab_build_dir + "/src/"
moab_lib_path = moab_build_dir + "/lib/"
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


with open(Path(__file__).parent / "moab" / "CMakeLists.txt") as f:
    content = f.read()
    match = re.search(r'SET\(PACKAGE_VERSION "(\d+\.\d+\.\d+)"\)', content)
    if match:
        version = match.group(1)
    else:
        raise ValueError("Unable to find PACKAGE_VERSION in CMakeLists.txt")

# setup pymoab
setup(
    name="pymoab",
    ext_modules=ext_modules,
    package_dir={"": "moab/pymoab"},
    packages=["pymoab"],
    package_data={
        "pymoab": [
            "*.pxd",
        ]
    },
    version=version,
    author="Patrick Shriwise, Guilherme Caminha, Vijay Mahadevan, Iulian Grindeanu, Anthony Scopatz",
    author_email="moab-dev@mcs.anl.gov",
)

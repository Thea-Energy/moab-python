import platform
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from subprocess import check_call
import sys
import shutil
import logging
from typing import List, Dict
from pathlib import Path
import os


class MOABExtension(Extension):
    root_dir: Path

    def __init__(self, name: str, version: str):
        super().__init__(name, sources=[])
        self.root_dir = Path(__file__).parent.absolute()


class MOABBuild(build_ext):
    def run(self):
        try:
            check_call(["cmake", "--version"])
        except OSError:
            raise RuntimeError("CMake must be installed")

        if platform.system() not in ("Windows", "Linux", "Darwin"):
            raise RuntimeError(f"Unsupported os: {platform.system()}")

        for ext in self.extensions:
            if isinstance(ext, MOABExtension):
                self.build_extension(ext)

    def build_extension(self, ext: MOABExtension):
        ext_dir = Path(self.get_ext_fullpath(ext.name)).parent.absolute()
        _ed = ext_dir.as_posix()

        build_dir = create_directory(Path(self.build_temp))

        # package builds in 2 steps, first to compile the nlopt package and second to build the DLL
        cmd = [
            "cmake",
            "-LAH",
            "-S",
            (ext.root_dir / "moab").as_posix(),
            "-B",
            build_dir.as_posix(),
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={_ed}",
            f"-DPython_EXECUTABLE={sys.executable}",
            "-DBUILD_SHARED_LIBS=ON",
            "-DENABLE_HDF5=ON",
            "-DENABLE_NETCDF=OFF",
            "-DENABLE_FORTRAN=OFF",
            "-DENABLE_BLASLAPACK=OFF",
            "-DENABLE_PYMOAB=OFF",
        ]

        if platform.system() == "Windows":
            cmd.insert(
                2, f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{self.config.upper()}={_ed}"
            )

        execute_command(
            cmd=cmd,
            cwd=ext.root_dir,
            env={
                **os.environ.copy(),
                "CXXFLAGS": f'{os.environ.get("CXXFLAGS", "")} -DVERSION_INFO="{self.distribution.get_version()}"',
            },
        )

        # build the DLL
        execute_command(
            [
                "cmake",
                "--build",
                build_dir.as_posix(),
                # "--config",
                # self.config,
                "--",
                "-m" if platform.system() == "Windows" else "-j2",
            ],
            cwd=ext.root_dir,
        )
        # self.copy_tree(self.build_temp, self.build_lib)


def create_directory(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(exist_ok=True, parents=True)
    return path


def execute_command(cmd: List[str], cwd: Path, env: Dict[str, str] = os.environ):
    logging.info(f"Running Command: {cwd.as_posix()}: {' '.join(cmd)}: {env['CXX']}")
    check_call(cmd, cwd=cwd.as_posix(), env=env)


setup(
    ext_modules=[MOABExtension("moab._moab", "5.5.0")],
    cmdclass={"build_ext": MOABBuild},
    zip_safe=False,
)

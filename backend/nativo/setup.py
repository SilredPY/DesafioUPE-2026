from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup

setup(ext_modules=[Pybind11Extension("naangareko_nativo", ["src/agrupacion.cpp"], cxx_std=17)])

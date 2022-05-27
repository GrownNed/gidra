from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension("lkcp.core",
        sources = ["lkcp/core.pyx", "lkcp/ikcp.c"],
        )

core = cythonize(ext)

setup(
        name = "lkcp",
        version = '0.1',
        packages = ["lkcp"],
        description = "python-kcp for skywind3000's kcp",
        author = "xingshuo",
        license = "MIT",
        url = "https://github.com/xingshuo/python-kcp.git",
        keywords=["kcp", "python"],
        ext_modules = core,
        )

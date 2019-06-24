from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
  name = 'Test app',
  ext_modules=[
    Extension('cython_core',
              sources=['cython_core.pyx'],
  extra_compile_args=['-O3','-fopenmp', '-march=native'],
  extra_link_args=['-fopenmp', '-march=native'],
              ),

    ],
  cmdclass = {'build_ext': build_ext},
)

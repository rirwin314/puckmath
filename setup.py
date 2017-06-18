from distutils.core import setup

setup(name='puckmath',
      version='1.0',
      description='',
      author='Rob Irwin',
      author_email='rirwin314@gmail.com',
      url='',
      packages=['puckmath', 'puckmath.core', 'puckmath.core.builder', 'puckmath.core.schema',
                'puckmath.core.tools.NHLDownloader', 'puckmath.core.tools.NHLParser', 'puckmath.core.tools'])
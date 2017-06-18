from distutils.core import setup

setup(name='puckmath',
      version='0.1',
      description='',
      author='Rob Irwin',
      author_email='rirwin314@gmail.com',
      url='',
      packages=['puckmath.puckdb', 'puckmath.puckdb', 'puckmath.puckdb.builder', 'puckmath.puckdb.schema',
                'puckmath.puckdb.tools.nhl_downloader', 'puckmath.puckdb.tools.nhl_parser', 'puckmath.puckdb.tools',
                'puckmath.db_utils', 'puckmath.interfaces', 'puckmath.models', 'puckmath.models.markov'])
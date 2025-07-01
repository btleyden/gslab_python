import os
import re
import sys
import shutil
import site
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from glob import glob
 
# Determine if the user has specified which paths to report coverage for
include_indices = [i for i, arg in enumerate(sys.argv) if re.search('^--include=', arg)]

if include_indices:
    include_arg = sys.argv[include_indices[0]]
    del sys.argv[include_indices[0]]
else:
    include_arg = None

# Additional build commands
class TestRepo(build_py):
    '''Build command for running tests in repo'''
    def run(self):
        if include_arg:
            coverage_command = 'coverage report -m %s' % include_arg
        else:
            coverage_command = 'coverage report -m --omit=setup.py,*/__init__.py,.eggs/*'


        if sys.platform != 'win32':
            os.system("coverage run --branch --source ./ setup.py test1 2>&1 "
                      "| tee test.log")
            # http://unix.stackexchange.com/questions/80707/
            #   how-to-output-text-to-both-screen-and-file-inside-a-shell-script
            os.system("%s  2>&1 | tee -a test.log" % coverage_command) 
        else:
            os.system("coverage run --branch --source ./ setup.py "
                      "> test.log")
            os.system("%s >> test.log" % coverage_command)

        sys.exit()


class CleanRepo(build_py):
    '''Build command for clearing setup directories after installation'''
    def run(self):
        # i) Remove the .egg-info or .dist-info folders
        egg_directories = glob('./*.egg-info')
        for directory in egg_directories:
            if os.path.exists(directory):
                shutil.rmtree(directory)
        dist_directories = glob('./*.dist-info')
        for directory in dist_directories:
            if os.path.exists(directory):
                shutil.rmtree(directory)
        # ii) Remove the ./build and ./dist directories
        if os.path.isdir('./build'):
            shutil.rmtree('./build')
        if os.path.isdir('./dist'):
            shutil.rmtree('./dist')

# Requirements
requirements = ['requests', 'pymmh3']

setup(name         = 'GSLab_Tools',
      version      = '4.1.2',
      description  = 'Python tools for GSLab',
      url          = 'https://github.com/gslab-econ/gslab_python',
      author       = 'Matthew Gentzkow, Jesse Shapiro',
      author_email = 'gentzkow@stanford.edu, jesse_shapiro_1@brown.edu',
      license      = 'MIT',
      packages     = find_packages(),
      install_requires = requirements,
      zip_safe     = False,
      cmdclass     = {'test': TestRepo, 'clean': CleanRepo},
      setup_requires = ['pytest-runner', 'coverage'],
      tests_require = ['pytest', 'coverage'])


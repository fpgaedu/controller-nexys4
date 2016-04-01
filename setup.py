from setuptools import setup

setup(name='fpgaedu',
        version='0.1',
        author='Matthijs Bos',
        packages=['fpgaedu'],
        install_required=['myhdl'],
        test_suite='pytest-runner',
        tests_require=['pytest'])

#!/usr/bin/env python

from setuptools import setup

setup(name='fpgaedu',
        version='0.1',
        author='Matthijs Bos',
        packages=['fpgaedu'],
        install_requires=['myhdl', 'pytest-runner'],
        test_suite='pytest-runner',
        tests_require=['pytest', 'pytest-xdist'],
        entry_points={
            'console_scripts': [
                'fpgaedu = fpgaedu.script:test'
            ]
        })

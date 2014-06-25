#!/usr/bin/env python

import os.path
from glob import glob
from distutils.core import setup

import versioneer
versioneer.VCS = 'git'
versioneer.versionfile_source = 'netman/_version.py'
versioneer.versionfile_build = 'netman/_version.py'
versioneer.tag_prefix = 'v'
versioneer.parentdir_prefix = 'django-netman-'


setup(
    name='django-netman',
    version=versioneer.get_version(),
    description='Network management modules for Django',
    author='Darryl Ross',
    author_email='darryl@afoyi.com',
    url='https://git.afoyi.com/django-modules/django-netman/',
    packages=['netman', 'netman/ipaddr'],
    cmdclass=versioneer.get_cmdclass()
)

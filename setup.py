#!/usr/bin/env python

from glob import glob
from setuptools import setup

import versioneer
versioneer.VCS = 'git'
versioneer.versionfile_source = 'netman/_version.py'
versioneer.versionfile_build = 'netman/_version.py'
versioneer.tag_prefix = 'v'
versioneer.parentdir_prefix = 'django-netman-'


setup(
    name='django-netman',
    cmdclass=versioneer.get_cmdclass(),
    version=versioneer.get_version(),
    description='Network management modules for Django',
    author='Darryl Ross',
    author_email='darryl@afoyi.com',
    url='https://git.afoyi.com/django-modules/django-netman/',
    packages=[ 'netman', 'netman/ipaddr' ],
    package_data={
        'netman': glob('netman/static/css/*.css') + glob('netman/templates/*.html'),
        'netman/ipaddr': glob('netman/templates/ipaddr/*.html')
    },
    include_package_data=True
)

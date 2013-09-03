from setuptools import setup, find_packages
import os

version = '0.8'

setup(name='django_layers',
      version=version,
      description="Support different frontend templates/statics on same instance",
      long_description=open("README.md").read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Ivo van der Wijk',
      author_email='djangoprojects@in.m3r.nl',
      url='http://github.com/iivvoo/django_layers',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pytest',
          'twotest',
      ],
      entry_points={
      },

      )


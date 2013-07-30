django layers
=============

This package provides layers of templates that can be included in the
django template path search depending on certain conditions

Why?
----

Using layers you can provide alternative sets of templates ("skins")
depending on different contexts. For example, using the same CMS you
can, from a single code base, host different frontend designs.

A/B testing


How?
----

You define your layer insite a layer/ folder in your django app(s). Using
the django_layer.loader.Loader template loader you can search these folders
for additional templates in the same way as templates/ folders are searched.
However, whether or not a layer is included can be context depending.

The context is determined... how?

- a map
- a function
- layers.py in a package?

It requires middleware

Settings
--------

Example
-------

pkg1/templates/pkg1/foo.html
pkg2/templates/pkg1/foo.html
pkg2/layers/foo.org/pkg1/foo.html
pkg2/layers/bar.org/pkg1/foo.html

pkg2/layers.py
  def select(request):
      if request.get_host() == 'foo.org':
          return 'foo.org'
      if request.get_host() == 'bar.org':
          return 'bar.org'
      return None

INSTALLED_APPS = (pkg1, pkg2)

request for foo.org? -> pkg2/layers/foo.org/foo.html
request for bar.org? -> pkg2/layers/bar.org/foo.html
request for example.org? -> pkg2/templates/pkg1/foo.html

Why not static?
---------------

Static files are collected and must therefore have unique paths anyway.


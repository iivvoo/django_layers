django layers
=============

This package provides support for "layers" of templates and static resources
that can be selecting depending on the request context.

WARNING: The API documented below may change significantly before version 1.0

Why?
----

Using layers you can provide alternative sets of templates ("skins")
depending on different contexts. For example, using the same CMS you
can, from a single code base, host different frontend designs, have
a different visitor/admin frontend, do A/B testing, etc.

All of this within the same instance (so no separate instances each running
with their own settings.py configuration)


How?
----

pip/easy_install this package, django_layers

Then add 'layers.middleware.LayerLoaderMiddleware' to your
MIDDLEWARE_CLASSES, e.g.

    MIDDLEWARE_CLASSES = (
        'layers.middleware.LayerLoaderMiddleware',
        ...
    )

Also, add 'layers.loader.LayerLoader' to your TEMPLATE_LOADERS, e.g.

    TEMPLATE_LOADERS = (
        'layers.loader.LayerLoader',
        ...
    )

Optionally, if you have separate collections of static resources for each layer,
add 'layers.finders.AppLayerFinder' as the first STATICFILE_FINDERS:

    STATICFILES_FINDERS = (
        'layers.finders.AppLayerFinder',
        # ...
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

and define which layers you have and where they need to be collected to

    LAYERS = {
        'visitor-a':STATIC_ROOT + '/visitor-a',
        'visitor-b':STATIC_ROOT + '/visitor-b'
        }


Now you can start using layers.

Create the same templates as before but in stead (or on top of) storing them
in your package's templates folder, store them in a folder called 
'layers/<layername>/templates'.

E.g. you could have

mypackage/templates/mypackage/foo.html
mypackage/layers/visitor-a/templates/mypackage/foo.html
mypackage/layers/visitor-b/templates/mypackage/foo.html

This creates two layers, "visitor-a" and "visitor-b" and a fallback if no
layer is selected.

Additionally, create a file "layers.py" with a function "get_layers" that
will return the layer to be used, e.g.

    def get_layer(request):
        if request.get_host().startswith("a."):
            return "visitor-a"
        if request.get_host().startswith("b."):
            return "visitor-b"


You can do anything you like in the "get_layer" callable, as long as you return
a layer or nothing.

When requesting Django to render the template "mypackage/foo.html", it will
render any of the three templates above depending on the request context (the
hostname used).

Configuration per layer
-----------------------

You can also provide some global shared configuration per layer. Since all
layers will share the same settings.py, it's not possible to use that for
layer specific configuration.

You can do this by defining a 'get_config' method in your package's layers.py
file. This will simply return a dict containing the layer specific data for
each layer.

E.g.

    def get_config():
        return {'visitor-a': dict(site_id=1, mailto='visitor-a@example.com'),
                'visitor-b': dict(site_id=2, mailto='visitor-b@example.com')
               }

You can then access the current layer's configuration using 'get_current_layer':

    from layers.middleware import get_current_layer

    def myview(request):
        layer = get_current_layer()
        return SomeModel.objects.filter(site_id=layer['site_id'])

Static resources per layer
--------------------------

You can store your per-layer statics in any app installed in your application
in the layers/<layer>/<layername>/statics folder, e.g. you could have

mypackage/static/css/foo.css
mypackage/layers/visitor-a/static/css/foo.css
mypackage/layers/visitor-b/static/css/foo.css

A request for /static/css/foo.css will result in visitor-a/static/css/foo.css
if the visitor-a layer is active, it will result in visitor-b/static/css/foo.css
if the visitor-b layer is active or in mypackage/static/css/foo.css otherwise.


Static resources are served by the django 'runserver' command or by a webserver
running in front of your application.

django_layers provides an upgraded 'runserver' command that knows which static
resources to serve depending on the active layer. It also comes with a 
'collectlayers' command that collects the layers into distinct staticfolders,
similar to how 'collectstatic' works. Which layer is collected where is defined
by the 'LAYERS' settings.py setting.

E.g. given the previous LAYERS definition

    python manage.py collectlayers

will collect the global static resources and visitor-a specific resources into
STATIC_ROOT + '/visitor-a' and another copy of the global static resources
and visitor-b specific resources into STATIC_ROOT + '/visitor-b'


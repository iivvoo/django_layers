django layers
=============

This package provides support for layers of templates that can be included
in the django template path search depending on certain conditions.

Why?
----

Using layers you can provide alternative sets of templates ("skins")
depending on different contexts. For example, using the same CMS you
can, from a single code base, host different frontend designs.

Or you can use a simple randomize function for A/B testing.


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

Now you can start using layers.

Create the same templates as before but in stead (or on top of) storing them
in your package's templates folder, store them in a folder called 
'layers/<layername>'.

E.g. you could have

mypackage/templates/mypackage/foo.html
mypackage/layers/visitor-a/mypackage/foo.html
mypackage/layers/visitor-b/mypackage/foo.html

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


Why not static?
---------------

django_layers does not handle static files. Since these can be collected,
different layers could overwrite each other. This means your CSS, js, etc 
needs to have a unique name and be included explicitly.


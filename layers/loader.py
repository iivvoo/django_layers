import os
import sys

from django.template.base import TemplateDoesNotExist
from django.template.loaders.app_directories import Loader as BaseLoader
from django.conf import settings
from layers.middleware import get_current_request
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured


from django.utils import six

# taken from / inspired by django.template.loaders.app_directories
# At compile time, cache the directories to search.
if not six.PY3:
    fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()

app_templates_dirs = []
app_layers_dirs = []

for app in settings.INSTALLED_APPS:
    try:
        mod = import_module(app)
    except ImportError as e:
        raise ImproperlyConfigured('ImportError %s: %s' % (app, e.args[0]))
    layers_dir = os.path.join(os.path.dirname(mod.__file__), 'layers')
    if os.path.isdir(layers_dir):
        if not six.PY3:
            layers_dir = layers_dir.decode(fs_encoding)
        app_layers_dirs.append(layers_dir)

    template_dir = os.path.join(os.path.dirname(mod.__file__), 'templates')
    if os.path.isdir(template_dir):
        if not six.PY3:
            template_dir = template_dir.decode(fs_encoding)
        app_templates_dirs.append(template_dir)

# It won't change, so convert it to a tuple to save memory.
app_templates_dirs = tuple(app_templates_dirs)
app_layers_dirs = tuple(app_layers_dirs)

"""
    Resolve the callable that resolves the layer to be activated, if any
"""
app_layers_funcs = []
for app in settings.INSTALLED_APPS:
    try:
        mod = import_module(app + ".layers")

        if callable(mod.get_layer):
            app_layers_funcs.append(mod.get_layer)
    except (ImportError, AttributeError):
        pass  # don't care

app_layers_funcs = tuple(app_layers_funcs)

class LayerLoader(BaseLoader):
    def load_template_source(self, template_name, layers_dirs=None, templates_dirs=None, layers_funcs=None):
        #if template_name.endswith("reserveren.html"):
        #    import pdb; pdb.set_trace()

        request = get_current_request()
        layers_dirs = layers_dirs or app_layers_dirs
        templates_dirs = templates_dirs or app_templates_dirs
        layers_funcs = layers_funcs or app_layers_funcs

        for f in layers_funcs:
            ## optimization: check if we didn't already try this prefix in a previous iteration
            prefix = f(request)

            if prefix:
                if layers_dirs:
                    for filepath in self.get_template_sources(os.path.join(prefix, "templates", template_name), layers_dirs):
                        try:
                            with open(filepath, 'rb') as fp:
                                return (fp.read().decode(settings.FILE_CHARSET), filepath)
                        except IOError:
                            pass
                if templates_dirs:
                    for filepath in self.get_template_sources(os.path.join(prefix, template_name), templates_dirs):
                        try:
                            with open(filepath, 'rb') as fp:
                                return (fp.read().decode(settings.FILE_CHARSET), filepath)
                        except IOError:
                            pass
        raise TemplateDoesNotExist(template_name)

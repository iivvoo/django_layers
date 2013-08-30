try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django.utils.importlib import import_module
from django.conf import settings

_thread_locals = local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

def get_current_layer():
    return getattr(_thread_locals, 'layer', {})

layer_confs = {}

for app in settings.INSTALLED_APPS:
    try:
        mod = import_module(app + ".layers")

        if hasattr(mod, 'get_config') and callable(mod.get_config):
            conf = mod.get_config()
            for k, v in conf.iteritems():
                if k not in layer_confs:
                    layer_confs[k] = v

                layer_confs[k].update(v)

    except (ImportError, AttributeError):
        pass  # don't care

from layers.loader import app_layers_funcs

def get_active_layer(request):
    """ return the first layer func result that is not false """
    for f in app_layers_funcs:
        prefix = f(request)
        if prefix:
            return prefix

class LayerLoaderMiddleware(object):
    def process_request(self, request):
        _thread_locals.request = request
        _thread_locals.layer = layer_confs.get(get_active_layer(request))


from django.contrib.staticfiles.management.commands.runserver import Command as BaseCommand
from django.conf import settings

from layers.handlers import LayeredStaticFilesHandler

class Command(BaseCommand):
    """
        Override the StaticFilesHandler to use with one that will store
        a reference to the request, which we need in the StaticFileFinder
    """
    def get_handler(self, *args, **options):
        """
        Returns the static files serving handler wrapping the default handler,
        if static files should be served. Otherwise just returns the default
        handler.

        """
        handler = super(Command, self).get_handler(*args, **options)
        use_static_handler = options.get('use_static_handler', True)
        insecure_serving = options.get('insecure_serving', False)
        if use_static_handler and (settings.DEBUG or insecure_serving):
            return LayeredStaticFilesHandler(handler)
        return handler


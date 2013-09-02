from django.contrib.staticfiles.handlers import StaticFilesHandler

from .middleware import _thread_locals

class LayeredStaticFilesHandler(StaticFilesHandler):
    def serve(self, request):
        """
            Store a reference to the request object
        """
        _thread_locals.request = request

        return super(LayeredStaticFilesHandler, self).serve(request)

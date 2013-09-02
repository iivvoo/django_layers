from django.contrib.staticfiles.handlers import StaticFilesHandler

from .middleware import _thread_locals

class LayeredStaticFilesHandler(StaticFilesHandler):
    def serve(self, request):
        """
        Actually serves the request path.
        """
        _thread_locals.request = request

        return super(LayeredStaticFilesHandler, self).serve(request)

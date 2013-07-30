import os

from django.template.base import TemplateDoesNotExist
from django.template.loaders.app_directories import Loader as BaseLoader
from django.conf import settings
from layers.middleware import get_current_request

class VisitorLoader(BaseLoader):
    def load_template_source(self, template_name, template_dirs):
        request = get_current_request()

        hostmap = getattr(settings, 'VISITOR_HOST_MAP', {})
        prefix = hostmap.get(request.get_host().split(":")[0])
        if prefix:
            for filepath in self.get_template_sources(os.path.join(prefix, template_name), template_dirs):
                try:
                    with open(filepath, 'rb') as fp:
                        return (fp.read().decode(settings.FILE_CHARSET), filepath)
                except IOError:
                    pass
        raise TemplateDoesNotExist(template_name)

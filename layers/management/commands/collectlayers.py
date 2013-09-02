from django.contrib.staticfiles.management.commands.collectstatic import Command as BaseCommand
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.core.management.base import NoArgsCommand
from django.conf import settings


class Command(NoArgsCommand):
    """
        voor iedere layer
        stel settings STATIC_ROOT in op layer's root
        roep commando aan
    """
    option_list = BaseCommand.option_list

    def handle_noargs(self, **options):
        self.opts = options

        layers = getattr(settings, "LAYERS", {})
        if layers:
            for layer, path in layers.iteritems():
                self.invoke_collectstatic(layer, path)
        else:
            self.invoke_collectstatic(layer, settings.STATIC_ROOT)

    def invoke_collectstatic(self, layer, path):
        self.stdout.write("Collecting layer %s to path %s\n" % (layer, path))
        cmd = BaseCommand()
        cmd.storage = StaticFilesStorage(path)
        cmd.stdout = self.stdout

        cmd.handle_noargs(**self.opts.copy())


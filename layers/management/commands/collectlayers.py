import os
import sys

from django.utils.datastructures import SortedDict

from django.contrib.staticfiles.management.commands.collectstatic import Command as BaseCommand
from django.core.files.storage import FileSystemStorage

from django.contrib.staticfiles.storage import StaticFilesStorage
from django.core.management.base import CommandError
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.staticfiles import finders



class Command(BaseCommand):
    """
        Do a 'collectstatic' for each LAYER definde in the settings
        (or default to collectstatic behaviour)

        This, unfortunately, means copy / repeating some original collectstatic
        code.
    """
    option_list = BaseCommand.option_list

    def __init__(self, *args, **kwargs):
        """ Make sure there's always a self.layer """
        self.layer = ""
        super(Command, self).__init__(*args, **kwargs)

    def handle_noargs(self, **options):
        """ Handle the invocation similarly to collectstatic """
        self.set_options(**options)
        # Warn before doing anything more.
        if (isinstance(self.storage, FileSystemStorage) and
                self.storage.location):
            destination_path = self.storage.location
            destination_display = ':\n\n    %s' % destination_path
        else:
            destination_path = None
            destination_display = '.'

        if self.clear:
            clear_display = 'This will DELETE EXISTING FILES!'
        else:
            clear_display = 'This will overwrite existing files!'

        if self.interactive:
            confirm = raw_input(u"""
You have requested to collect static files at the destination
location as specified in your settings%s

%s
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """
% (destination_display, clear_display))
            if confirm != 'yes':
                raise CommandError("Collecting static files cancelled.")

        layers = getattr(settings, "LAYERS", {})

        modified_count = 0
        unmodified_count = 0
        post_processed_count = 0

        ## .. but iterate over the layers
        if layers:
            for layer, path in layers.iteritems():
                collected= self.invoke_collect(layer, path)
                modified_count += len(collected['modified'])
                unmodified_count += len(collected['unmodified'])
                post_processed_count += len(collected['post_processed'])

        else:
            collected = self.collect()
            modified_count = len(collected['modified'])
            unmodified_count = len(collected['unmodified'])
            post_processed_count = len(collected['post_processed'])

        if self.verbosity >= 1:
            template = ("\n%(modified_count)s %(identifier)s %(action)s"
                        "%(destination)s%(unmodified)s%(post_processed)s.\n")
            summary = template % {
                'modified_count': modified_count,
                'identifier': 'static file' + (modified_count != 1 and 's' or ''),
                'action': self.symlink and 'symlinked' or 'copied',
                'destination': (destination_path and " to '%s'"
                                % destination_path or ''),
                'unmodified': (collected['unmodified'] and ', %s unmodified'
                               % unmodified_count or ''),
                'post_processed': (collected['post_processed'] and
                                   ', %s post-processed'
                                   % post_processed_count or ''),
            }
            self.stdout.write(smart_str(summary))

    def invoke_collect(self, layer, path):
        """ Invoke collect, reset all instance storage first and initialize
            a self.storage that's bound to the layers target STATIC_ROOT
        """
        self.stdout.write("Collecting layer %s to path %s\n" % (layer, path))
        self.storage = StaticFilesStorage(path)
        try:
            self.storage.path('')
        except NotImplementedError:
            self.local = False
        else:
            self.local = True
        self.copied_files = []
        self.symlinked_files = []
        self.unmodified_files = []
        self.post_processed_files = []
        self.layer = layer

        return self.collect()

    def collect(self):
        """
            Copied from collectstatic's Command.collect() with a tiny
            storage-layer check ..
        """
        if self.symlink:
            if sys.platform == 'win32':
                raise CommandError("Symlinking is not supported by this "
                                   "platform (%s)." % sys.platform)
            if not self.local:
                raise CommandError("Can't symlink to a remote destination.")

        if self.clear:
            self.clear_dir('')

        if self.symlink:
            handler = self.link_file
        else:
            handler = self.copy_file

        found_files = SortedDict()
        for finder in finders.get_finders():
            for path, storage in finder.list(self.ignore_patterns):
                ## .. is the storage part of the current layer?
                if hasattr(storage, 'layer') and storage.layer != self.layer:
                    continue

                # Prefix the relative path if the source storage contains it
                if getattr(storage, 'prefix', None):
                    prefixed_path = os.path.join(storage.prefix, path)
                else:
                    prefixed_path = path

                if prefixed_path not in found_files:
                    found_files[prefixed_path] = (storage, path)
                    handler(path, prefixed_path, storage)

        # Here we check if the storage backend has a post_process
        # method and pass it the list of modified files.
        if self.post_process and hasattr(self.storage, 'post_process'):
            processor = self.storage.post_process(found_files,
                                                  dry_run=self.dry_run)
            for original_path, processed_path, processed in processor:
                if processed:
                    self.log(u"Post-processed '%s' as '%s" %
                             (original_path, processed_path), level=1)
                    self.post_processed_files.append(original_path)
                else:
                    self.log(u"Skipped post-processing '%s'" % original_path)

        return {
            'modified': self.copied_files + self.symlinked_files,
            'unmodified': self.unmodified_files,
            'post_processed': self.post_processed_files,
        }

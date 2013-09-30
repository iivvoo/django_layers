import os
import py.test
from django.template.base import TemplateDoesNotExist

from layers.loader import LayerLoader

class TestOldstyleLoader(object):
    """ layers can also be in <pkg>/templates/<layer> """
    def test_simpelmatch(self):
        """ Simple case, direct match """
        loader = LayerLoader()
        f = lambda x: 'test'

        import pkg1
        path = os.path.join(os.path.dirname(pkg1.__file__ ), 'templates')

        tpl, tplpath = loader.load_template_source("oldstyle.html",
                                                   templates_dirs=[path], 
                                                   layers_funcs=[f])
        assert tplpath == os.path.join(path, "test", "oldstyle.html")

class TestLoader(object):
    def test_nothing(self):
        """ no templates hence DoesNotExist """
        loader = LayerLoader()
        py.test.raises(TemplateDoesNotExist,
                       loader.load_template_source, "foo.html")

    def test_simpelmatch(self):
        """ Simple case, direct match """
        loader = LayerLoader()
        f = lambda x: 'test'

        import pkg1
        path = os.path.join(os.path.dirname(pkg1.__file__ ), 'layers')

        tpl, tplpath = loader.load_template_source("test.html",
                                                   layers_dirs=[path], 
                                                   layers_funcs=[f])
        assert tplpath == os.path.join(path, "test", "templates", "test.html")

    def test_complexmatch(self):
        """ two failing layer funcs followed by success """
        loader = LayerLoader()
        match = lambda x: 'test'
        nomatch = lambda x: None
        notexist = lambda x: 'bar'

        import pkg1
        path = os.path.join(os.path.dirname(pkg1.__file__ ), 'layers')

        tpl, tplpath = loader.load_template_source("test.html",
                                                   layers_dirs=[path], 
                                                   layers_funcs=[notexist,
                                                                 nomatch, match])
        assert tplpath == os.path.join(path, "test", "templates", "test.html")

    def test_order(self):
        """ multiple matching paths """
        loader = LayerLoader()
        match = lambda x: 'test'

        import pkg1, pkg2
        path1 = os.path.join(os.path.dirname(pkg1.__file__ ), 'layers')
        path2 = os.path.join(os.path.dirname(pkg2.__file__ ), 'layers')

        tpl, tplpath = loader.load_template_source("test.html",
                                                   layers_dirs=[path1, path2], 
                                                   layers_funcs=[match])
        assert tplpath == os.path.join(path1, "test", "templates", "test.html")

    def test_order2(self):
        """ multiple matching paths, first fails """
        loader = LayerLoader()
        match = lambda x: 'test'

        import pkg1, pkg2
        path1 = os.path.join(os.path.dirname(pkg1.__file__ ), 'layers')
        path2 = os.path.join(os.path.dirname(pkg2.__file__ ), 'layers')

        tpl, tplpath = loader.load_template_source("test2.html",
                                                   layers_dirs=[path1, path2], 
                                                   layers_funcs=[match])
        assert tplpath == os.path.join(path2, "test", "templates", "test2.html")

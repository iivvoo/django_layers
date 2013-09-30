from ..finders import AppLayerFinder

class TestFinder(object):
    def test_trivial_find(self):
        finder = AppLayerFinder(apps=["layers.tests.pkg1", "layers.tests.pkg2"])
        assert finder.find("file.x", layer="test").endswith("pkg1/layers/test/static/file.x")

    def test_find_second(self):
        finder = AppLayerFinder(apps=["layers.tests.pkg1", "layers.tests.pkg2"])
        assert finder.find("file.x", layer="test2").endswith("pkg1/layers/test2/static/file.x")


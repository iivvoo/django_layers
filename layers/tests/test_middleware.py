from layers.middleware import LayerLoaderMiddleware, get_current_request
from layers.middleware import store_conf_from_module, layer_confs
from layers.middleware import get_active_layer

class TestMiddleware(object):
    def test_roundtrip(self):
        req = {}
        LayerLoaderMiddleware().process_request(req)

        assert get_current_request() is req

    def test_conf(self):
        class DummyMod(object):
            def get_config(self):
                return dict(layer1=dict(a=1, b=2),
                            layer2=dict(a=2, c=3))

        store_conf_from_module(DummyMod())
        assert 'layer1' in layer_confs
        assert 'layer2' in layer_confs
        assert layer_confs['layer1']['a'] == 1
        assert 'c' not in layer_confs['layer1']

        assert layer_confs['layer2']['a'] == 2
        assert layer_confs['layer2']['c'] == 3

    def test_active_layer_trivial(self):
        assert get_active_layer({}, [lambda x: 'layer2']) == 'layer2'

    def test_active_layer_second(self):
        assert get_active_layer({}, [lambda x: None, lambda x: 'layer2']) == 'layer2'
    def test_active_layer_none(self):
        assert get_active_layer({}, [lambda x: None]) is None

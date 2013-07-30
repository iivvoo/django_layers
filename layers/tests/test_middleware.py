from layers.middleware import LayerLoaderMiddleware, get_current_request

class TestMiddleware(object):
    def test_roundtrip(self):
        req = {}
        LayerLoaderMiddleware().process_request(req)

        assert get_current_request() is req


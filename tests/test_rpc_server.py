import json
from neopython_ext_rpc_server.ExtRpcTestCase import ExtendedJsonRpcApiTestCase, mock_get_request, mock_post_request
from klein.test.test_resource import requestMock

"""
Special thanks to @jseagrave21 for writing most of the original tests
"""


class TestServer(ExtendedJsonRpcApiTestCase):
    def setUp(self):
        super().setUp()

    def test_HTTP_OPTIONS_request(self):
        mock_req = mock_get_request(b'/?test', b"OPTIONS")
        res = json.loads(self.app.home(mock_req))

        self.assertTrue("GET" in res['supported HTTP methods'])
        self.assertTrue("POST" in res['supported HTTP methods'])
        self.assertTrue("extended-rpc" in res['JSON-RPC server type'])

    def test_invalid_request_method(self):
        # test HEAD method
        mock_req = mock_get_request(b'/?test', b"HEAD")
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32600)
        self.assertEqual(res["error"]["message"], 'HEAD is not a supported HTTP method')

    def test_invalid_json_payload(self):
        # test POST requests
        mock_req = mock_post_request(b"{ invalid")
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32700)

        mock_req = mock_post_request(json.dumps({"some": "stuff"}).encode("utf-8"))
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32600)

        # test GET requests
        mock_req = mock_get_request(b"/?%20invalid")  # equivalent to "/? invalid"
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32600)

        mock_req = mock_get_request(b"/?some=stuff")
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32600)

    def test_missing_fields(self):
        # test POST requests
        req = self._gen_post_rpc_req("foo")
        del req["jsonrpc"]
        mock_req = mock_post_request(json.dumps(req).encode("utf-8"))
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32600)
        self.assertEqual(res["error"]["message"], "Invalid value for 'jsonrpc'")

        req = self._gen_post_rpc_req("foo")
        del req["id"]
        mock_req = mock_post_request(json.dumps(req).encode("utf-8"))
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32600)
        self.assertEqual(res["error"]["message"], "Field 'id' is missing")

        req = self._gen_post_rpc_req("foo")
        del req["method"]
        mock_req = mock_post_request(json.dumps(req).encode("utf-8"))
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32600)
        self.assertEqual(res["error"]["message"], "Field 'method' is missing")

        # test GET requests
        mock_req = mock_get_request(b"/?method=foo&id=2")
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32600)
        self.assertEqual(res["error"]["message"], "Invalid value for 'jsonrpc'")

        mock_req = mock_get_request(b"/?jsonrpc=2.0&method=foo")
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32600)
        self.assertEqual(res["error"]["message"], "Field 'id' is missing")

        mock_req = mock_get_request(b"/?jsonrpc=2.0&id=2")
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32600)
        self.assertEqual(res["error"]["message"], "Field 'method' is missing")

    def test_invalid_method(self):
        # test POST requests
        req = self._gen_post_rpc_req("invalid", request_id="42")
        mock_req = mock_post_request(json.dumps(req).encode("utf-8"))
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["id"], "42")
        self.assertEqual(res["error"]["code"], -32601)
        self.assertEqual(res["error"]["message"], "Method not found")

        # test GET requests
        req = self._gen_get_rpc_req("invalid")
        mock_req = mock_get_request(req)
        res = json.loads(self.app.home(mock_req))
        self.assertEqual(res["error"]["code"], -32601)
        self.assertEqual(res["error"]["message"], "Method not found")

    def test_gzip_compression(self):
        req = self._gen_post_rpc_req("getblock", params=['307ed2cf8b8935dd38c534b10dceac55fcd0f60c68bf409627f6c155f8143b31', 1])
        body = json.dumps(req).encode("utf-8")

        # first validate that we get a gzip response if we accept gzip encoding
        mock_req = requestMock(path=b'/', method=b"POST", body=body, headers={'Accept-Encoding': ['deflate', 'gzip;q=1.0', '*;q=0.5']})
        res = self.app.home(mock_req)

        GZIP_MAGIC = b'\x1f\x8b'
        self.assertIsInstance(res, bytes)
        self.assertTrue(res.startswith(GZIP_MAGIC))

        # then validate that we don't get a gzip response if we don't accept gzip encoding
        mock_req = requestMock(path=b'/', method=b"POST", body=body, headers={})
        res = self.app.home(mock_req)

        self.assertIsInstance(res, str)

        try:
            json.loads(res)
            valid_json = True
        except ValueError:
            valid_json = False
        self.assertTrue(valid_json)

import os.path
import nose
from nose.tools import assert_raises
from wurfl_cloud.cache.memcache_cache import MemcacheCache
from wurfl_cloud.cache.file_cache import FileCache


class TCache(object):
    def setup(self):
        self.cache = None
        self.cache_class = None

    def test_get_device(self):
        self.cache = self.cache_class(self.good_config)
        assert self.cache.get_device(u"test1") == {}

    def test_get_device_from_id(self):
        self.cache = self.cache_class(self.good_config)
        assert self.cache.get_device_from_id(u"htc_android_g1_ver1_5_subua") == {}

    def test_set_device(self):
        self.cache = self.cache_class(self.good_config)
        self.cache.set_device(u"test1", self.dev1)
        dev = self.cache.get_device(u"test1")
        assert dev[u"id"] == u"htc_android_g1_ver1_5_subua"
        assert dev[u"errors"] == {}

    def test_set_device_from_id(self):
        self.cache = self.cache_class(self.good_config)
        self.cache.set_device_from_id(u'htc_android_g1_ver1_5_subua', self.dev1)
        dev = self.cache.get_device_from_id(u"htc_android_g1_ver1_5_subua")
        assert dev[u"id"] == u"htc_android_g1_ver1_5_subua"
        assert dev[u"errors"] == {}

    def test_device_updates(self):
        self.cache = self.cache_class(self.good_config)
        self.cache.set_device_from_id(u'htc_android_g1_ver1_5_subua', self.dev1)
        self.cache.set_device_from_id(u'htc_android_g1_ver1_5_subua', self.dev2)
        self.cache.set_device(u"test1", self.dev1)
        self.cache.set_device(u"test1", self.dev2)
        dev1 = self.cache.get_device_from_id(u"htc_android_g1_ver1_5_subua")
        dev2 = self.cache.get_device(u"test1")
        assert dev1[u"capabilities"]["model_name"]
        assert dev1[u"capabilities"]["model_name2"]
        assert dev1[u"capabilities"]["pointing_method"]
        assert dev1[u"capabilities"]["pointing_method2"]
        assert dev2[u"capabilities"]["model_name"]
        assert dev2[u"capabilities"]["model_name2"]
        assert dev2[u"capabilities"]["pointing_method"]
        assert dev2[u"capabilities"]["pointing_method2"]

    def test_increments_and_stats(self):
        self.cache = self.cache_class(self.good_config)
        assert self.cache.stats["hit"] == 0
        assert self.cache.stats["miss"] == 0
        assert self.cache.stats["error"] == 0

        self.cache.add_hit()
        self.cache.add_miss()
        self.cache.add_error()
        assert self.cache.stats["hit"] == 1
        assert self.cache.stats["miss"] == 1
        assert self.cache.stats["error"] == 1

        self.cache.add_hit()
        assert self.cache.stats["hit"] == 2
        assert self.cache.stats["miss"] == 1
        assert self.cache.stats["error"] == 1

        self.cache.reset_stats()
        assert self.cache.stats["hit"] == 0
        assert self.cache.stats["miss"] == 0
        assert self.cache.stats["error"] == 0

    def test_cache(self):
        self.cache = self.cache_class(self.good_config)
        assert self.cache



class TestMemCache(TCache):
    def setup(self):
        TCache.setup(self)
        self.good_config = {
            u"cache": {
               u"type": u"memcached",
               u"servers": [u"127.0.0.1:11211"],
               u"expiration": 86400,
               u"binary": True,
               u"compression": True
            },
            u"misc": {
                u"report_interval": 60
            }
        }

        self.dev1 = {u'apiVersion': u'WurflCloud 1.3.2',
                     u'capabilities': {u'model_name': u'G1',
                                       u'pointing_method': u'touchscreen'},
                     u'errors': {},
                     u'id': u'htc_android_g1_ver1_5_subua',
                     u'mtime': 1331919851}

        self.dev2 = {u'apiVersion': u'WurflCloud 1.3.2',
                     u'capabilities': {u'model_name2': u'G1',
                                       u'pointing_method2': u'touchscreen'},
                     u'errors': {},
                     u'id': u'htc_android_g1_ver1_5_subua',
                     u'mtime': 1331919851}
        self.cache = None
        self.cache_class = MemcacheCache

    def teardown(self):
        if self.cache:
            self.cache.mc.flush_all()

class TestFileCache(TCache):
    def setup(self):
        TCache.setup(self)
        self.good_config = {
            u"cache": {
               u"type": u"file",
               u"file": u"_test_cloud_cache.db",
               u"expiration": 86400
            },
            u"misc": {
                u"report_interval": 60
            }
        }

        self.dev1 = {u'apiVersion': u'WurflCloud 1.3.2',
                     u'capabilities': {u'model_name': u'G1',
                                       u'pointing_method': u'touchscreen'},
                     u'errors': {},
                     u'id': u'htc_android_g1_ver1_5_subua',
                     u'mtime': 1331919851}

        self.dev2 = {u'apiVersion': u'WurflCloud 1.3.2',
                     u'capabilities': {u'model_name2': u'G1',
                                       u'pointing_method2': u'touchscreen'},
                     u'errors': {},
                     u'id': u'htc_android_g1_ver1_5_subua',
                     u'mtime': 1331919851}
        self.cache = None
        self.cache_class = FileCache

    def teardown(self):
        if self.cache:
            self.cache.db.close()
            if os.path.exists("_test_cloud_cache.db"):
                os.remove("_test_cloud_cache.db")

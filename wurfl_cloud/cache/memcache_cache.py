import time
import pylibmc

from wurfl_cloud.cache.interface import CacheInterface

__license__ = """
 Copyright (c) 2015 ScientiaMobile Inc.
 
 The WURFL Cloud Client is intended to be used in both open-source and
 commercial environments. To allow its use in as many situations as possible,
 the WURFL Cloud Client is dual-licensed. You may choose to use the WURFL
 Cloud Client under either the GNU GENERAL PUBLIC LICENSE, Version 2.0, or
 the MIT License.
 
 Refer to the COPYING.txt file distributed with this package.

"""

class MemcacheCache(CacheInterface):
    def __init__(self, config):
        CacheInterface.__init__(self, config)
        self.expiration = self.config[u"cache"].get(u"expiration", 86400)
        self.compression = self.config[u"cache"].get(u"compression", 0)
        servers = self.config[u"cache"][u"servers"]
        binary_mode = self.config[u"cache"][u"binary"]
        self.mc = pylibmc.Client(servers, binary=binary_mode)
        self.mc.behaviors["hash"] = "md5"
        compression_mode = 1 if self.compression else 0
        self._set_kwargs = {"time": self.expiration,
                            "min_compress_len": compression_mode}

        pool_size = self.config[u"cache"].get(u"pool_size", 4)
        self.pool = pylibmc.ClientPool()
        self.pool.fill(self.mc, pool_size)
        self._init_memcache()

    def _init_memcache(self):
        with self.pool.reserve() as mc:
            mc.add("wurfl_cloud_hit", "0")
            mc.add("wurfl_cloud_miss", "0")
            mc.add("wurfl_cloud_error", "0")
        self.set_mtime(str(time.time()))

    def get(self, key):
        with self.pool.reserve() as mc:
            val = mc.get(key)
            if val is None:
                raise KeyError()
            return val

    def set(self, key, val):
        with self.pool.reserve() as mc:
            mc.set(key, val, **self._set_kwargs)


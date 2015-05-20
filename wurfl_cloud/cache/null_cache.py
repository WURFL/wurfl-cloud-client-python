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


class NullCache(CacheInterface):

    def __init__(self, *args, **kwargs):
        pass

    def get(self, key):
        raise KeyError("cache key expired")

    def set(self, key, val):
        pass

    @property
    def stats(self):
        return {"hits": 0, "misses": 0, "errors": 0, "age": -1}

    @property
    def age(self):
        return -1

    def reset_stats(self):
        return

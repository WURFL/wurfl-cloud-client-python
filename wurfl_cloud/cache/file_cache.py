import atexit
import time
import logging

from sqlitedict import SqliteDict

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

logger = logging.getLogger("wurfl_cloud.cache.file")


class FileCache(CacheInterface):
    def __init__(self, config):
        CacheInterface.__init__(self, config)
        self.db = SqliteDict(self.config[u"cache"][u"file"], autocommit=True)
        self.expiration = self.config[u"cache"].get(u"expiration", 86400)
        def closer():
            try:
                self.db.close()
            except Exception:
                logger.exception("Exception closing file cache")
        atexit.register(closer)

    def get(self, key):
        if int(self.db[key + "_expiration"]) - time.time() <= 0:
            raise KeyError("cache key expired")
        return self.db[key]

    def set(self, key, val):
        self.db[key] = val
        self.db[key + "_expiration"] = str(int(time.time()) + self.expiration)

import json
from functools import wraps

__license__ = """
 Copyright (c) 2015 ScientiaMobile Inc.
 
 The WURFL Cloud Client is intended to be used in both open-source and
 commercial environments. To allow its use in as many situations as possible,
 the WURFL Cloud Client is dual-licensed. You may choose to use the WURFL
 Cloud Client under either the GNU GENERAL PUBLIC LICENSE, Version 2.0, or
 the MIT License.
 
 Refer to the COPYING.txt file distributed with this package.

"""

def load_config(filename):
    return json.loads(open(filename).read())


def get_cache(config):
    if config[u"cache"][u"type"] == u"memcached":
        from wurfl_cloud.cache.memcache_cache import MemcacheCache
        cache = MemcacheCache(config)
    elif config[u"cache"][u"type"] == u"file":
        from wurfl_cloud.cache.file_cache import FileCache
        cache = FileCache(config)
    else:
        from wurfl_cloud.cache.null_cache import NullCache
        cache = NullCache()
    return cache


def from_unicode(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        new_args = []
        for arg in args:
            if isinstance(arg, unicode):
                new_args.append(arg.encode("utf8", "replace"))
            else:
                new_args.append(arg)
        return func(*new_args, **kwargs)
    return wrapper


def to_unicode(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                new_args.append(arg.decode("utf8", "replace"))
            else:
                new_args.append(arg)
        return func(*new_args, **kwargs)
    return wrapper

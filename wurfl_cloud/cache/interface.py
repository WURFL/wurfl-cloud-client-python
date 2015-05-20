import json
import time

from wurfl_cloud import update_device

__license__ = """
 Copyright (c) 2015 ScientiaMobile Inc.
 
 The WURFL Cloud Client is intended to be used in both open-source and
 commercial environments. To allow its use in as many situations as possible,
 the WURFL Cloud Client is dual-licensed. You may choose to use the WURFL
 Cloud Client under either the GNU GENERAL PUBLIC LICENSE, Version 2.0, or
 the MIT License.
 
 Refer to the COPYING.txt file distributed with this package.

"""

class CacheInterface(object):
    def __init__(self, config):
        self.config = config

    def _from_backend(self, key):
        key = key.encode("utf8")
        try:
            data = self.get(key).decode("utf8")
            try:
                data = json.loads(data)
            except ValueError:
                pass
        except KeyError:
            data = {}
        return data

    def get(self, key):
        raise NotImplementedError()

    def set(self, key, val):
        raise NotImplementedError()

    def get_device(self, user_agent, do_stats=True):
        device_id = self._from_backend(user_agent)
        return self.get_device_from_id(device_id, do_stats)

    def get_device_from_id(self, device_id, do_stats=True):
        device = {}
        if device_id:
            device = self._from_backend(device_id)
        if do_stats:
            if device:
                self.add_hit()
            else:
                self.add_miss()
        return device

    def set_device(self, user_agent, device):
        user_agent = user_agent.encode("utf8")
        device = device.copy()
        device["errors"] = {}
        old_device = self.get_device(user_agent, do_stats=False)
        if old_device:
            device = update_device(old_device, device)
        wurfl_id = device[u"id"].encode("utf8")
        self.set(user_agent, wurfl_id)
        self.set(wurfl_id, json.dumps(device))
        self.set_mtime(device['mtime'])

    def set_device_from_id(self, wurfl_id, device):
        device = device.copy()
        device["errors"] = {}
        wurfl_id = wurfl_id.encode("utf8")
        old_device = self.get_device_from_id(wurfl_id, do_stats=False)
        if old_device:
            device = update_device(old_device, device)
        self.set(wurfl_id, json.dumps(device))

    def _incr(self, val):
        try:
            num = int(self.get(val))
        except KeyError:
            num = 0
        num += 1
        self.set(val, str(num))

    def add_hit(self):
        self._incr("wurfl_cloud_hit")

    def add_miss(self):
        self._incr("wurfl_cloud_miss")

    def add_error(self):
        self._incr("wurfl_cloud_error")

    def get_mtime(self):
        try:
            mtime = int(self.get("wurfl_cloud_mtime"))
        except (KeyError, ValueError) as exc:
            mtime = int(time.time())
            self.set_mtime(mtime)
        return mtime

    def set_mtime(self, val):
        if not isinstance(val, basestring):
            val = str(val)
        self.set("wurfl_cloud_mtime", val.encode("utf8"))

    @property
    def age(self):
        return int(time.time() - self.get_mtime())

    @property
    def stats(self):
        ret = {}
        for item in ("wurfl_cloud_hit", "wurfl_cloud_miss",
                     "wurfl_cloud_error"):
            name = item.split("_")[-1]
            try:
                ret[name] = int(self.get(item))
            except KeyError:
                ret[name] = 0
        ret["age"] = self.age
        return ret

    def reset_stats(self):
        self.set("wurfl_cloud_hit", "0")
        self.set("wurfl_cloud_miss", "0")
        self.set("wurfl_cloud_error", "0")


import sys
import json
import logging

import requests
from requests.exceptions import RequestException


__license__ = """
 Copyright (c) 2015 ScientiaMobile Inc.
 
 The WURFL Cloud Client is intended to be used in both open-source and
 commercial environments. To allow its use in as many situations as possible,
 the WURFL Cloud Client is dual-licensed. You may choose to use the WURFL
 Cloud Client under either the GNU GENERAL PUBLIC LICENSE, Version 2.0, or
 the MIT License.
 
 Refer to the COPYING.txt file distributed with this package.

"""

__version__ = "1.1.0"
__client_version__ = "WurflCloud_Client/Python_%s" % __version__


logger = logging.getLogger("wurfl_cloud")


class Cloud(object):
    """
    WURFL cloud interface class
    """
    user_agent_headers = [u'HTTP_X_DEVICE_USER_AGENT',
                          u'HTTP_X_ORIGINAL_USER_AGENT',
                          u'HTTP_X_OPERAMINI_PHONE_UA',
                          u'HTTP_X_SKYFIRE_PHONE',
                          u'HTTP_X_BOLT_PHONE_UA',
                          u'HTTP_USER_AGENT']

    def __init__(self, config, cache):
        """
        @param config: A configuration object
        @type config: dict
        @param cache: An cache object
        @type cache: wurfl_cloud.cache.CacheInterface instance
        """
        self.config = config
        self.cache = cache
        self.username, self.password = self.config[u"api"][u"key"].split(":", 1)

    def __call__(self, ua=None, headers=None, capabilities=None):
        """
        Get a device from the WURFL cloud

        @param ua: A unicode object representing a user agent
        @type ua: unicode
        @param headers: An object representing the headers of a request
        @type headers: dict
        @param capabilities: A list of capabilities to request from the cloud
        @type capabilities: list
        @raise LookupError: If there is a network error or the device cannot be
                            found, then a LookupError will be raised.

        """
        user_agent = self._get_ua(ua, headers)
        device = self._get_device(user_agent, headers, capabilities)
        device[u"user_agent"] = user_agent
        return device

    def _get_ua(self, ua, headers):
        user_agent = None
        if ua is not None:
            user_agent = ua
        elif headers is not None:
            user_agent = self._get_user_agent(headers)

        if not user_agent:
            raise LookupError("user agent and/or headers are invalid")

        logger.info("processing user agent: %s", user_agent)

        return user_agent[:255]

    def _get_user_agent(self, headers):
        """
        Find the user agent from the headers provided
        @param headers: An object representing the headers of a request
        @type headers: dict
        """
        for header in self.user_agent_headers:
            if header in headers:
                return headers[header]

    def _get_device(self, user_agent, headers, capabilities):
        """
        Find and return a device based on the given user agent and/or headers.
        If the device cannot be found in the cache, find it in the cloud.

        @param user_agent: A unicode object representing a user agent
        @type user_agent: unicode
        @param headers: An object representing the headers of a request
        @type headers: dict
        """
        device = self.cache.get_device(user_agent)
        if device:
            logger.info("found device in cache")
            device_caps = device["capabilities"].keys()
            missing_caps = set(capabilities) - set(device_caps)
            if missing_caps:
                logger.info("searching cloud for missing capabilities")
                new_device = self._call_cloud(user_agent, headers,
                                              list(missing_caps))
                # AJL Mon Apr 23 15:16:24 EDT 2012
                # If the device was present in the cache but did not have all
                # the requested capabilities, we update the cached device with
                # the capabilities from the cloud.
                return update_device(device, new_device)
            else:
                return device
        else:
            return self._call_cloud(user_agent, headers, capabilities)

    def _call_cloud(self, user_agent, headers, capabilities):
        """
        Find a device and request a list of capabilities from the cloud

        @param user_agent: A unicode object representing a user agent
        @type user_agent: unicode
        @param headers: An object representing the headers of a request
        @type headers: dict
        @param capabilities: A list of capabilities to request from the cloud
        @type capabilities: list
        """
        headers = self._get_headers(user_agent, headers)
        path = self._get_path(capabilities)
        uri = u"http://" + self.config["api"]["server"] + path
        try:
            logger.info("looking for device in cloud")
            cloud_data = requests.get(uri, headers=headers,
                                      auth=(self.username, self.password))
        except RequestException as exc:
            if 'X-Cloud-Counters' in headers:
                # AJL Mon Apr  9 13:32:15 EDT 2012
                # We restore the stats in case something went wrong
                for cloud_stat in headers['X-Cloud-Counters'].split(","):
                    k, v = cloud_stat.split(":")
                    self.cache.set("wurfl_cloud_%s" % k, v)
            trace = sys.exc_info()[2]
            raise LookupError(exc.args), None, trace

        if cloud_data.status_code != 200:
            raise LookupError(cloud_data.content, cloud_data.status_code)
        logger.info("parsing cloud data")
        return self._parse_cloud_data(user_agent, cloud_data)

    def _parse_cloud_data(self, user_agent, cloud_data):
        """
        Parse the return value from a successful call to the cloud

        @param user_agent: A unicode object representing a user agent
        @type user_agent: unicode
        @param cloud_data: The raw return value from the cloud server
        @type cloud_data: JSON
        """
        device = json.loads(cloud_data.content)
        self.cache.set_device(user_agent, device)
        return device

    def _get_headers(self, user_agent, headers):
        """
        Generate the headers for the cloud API

        @param user_agent: A unicode object representing a user agent
        @type user_agent: unicode
        @param headers: An object representing the headers of a request
        @type headers: dict
        """
        headers = {'User-Agent': user_agent,
                   'X-Cloud-Client': __client_version__}
        #report_interval = self.config[u"misc"][u"report_interval"]
        report_interval = 60
        if report_interval > 0 and self.cache.age >= report_interval:
            counter_data = []
            for k, v in self.cache.stats.iteritems():
                counter_data.append("%s:%s" % (k, v))
            headers['X-Cloud-Counters'] = ','.join(counter_data)
            self.cache.reset_stats()
        return headers

    def _get_path(self, capabilities):
        """
        Generate the URI to the cloud for a specific list of capabilities

        @param capabilities: A list of capabilities to request from the cloud
        @type capabilities: list
        """
        version = "/" + self.config["api"]["version"]
        if capabilities:
            return version + "/json/search:(" + ','.join(capabilities) + ")"
        return version + "/json/"


def update_device(old_device, new_device):
    upd_device = old_device.copy()
    upd_device["capabilities"].update(new_device["capabilities"])
    upd_caps = upd_device["capabilities"]
    upd_device.update(new_device)
    upd_device["capabilities"] = upd_caps
    return upd_device

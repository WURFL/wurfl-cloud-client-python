# ScientiaMobile WURFL Cloud Client for Python

The WURFL Cloud Service by ScientiaMobile, Inc., is a cloud-based
mobile device detection service that can quickly and accurately
detect over 500 capabilities of visiting devices.  It can differentiate
between portable mobile devices, desktop devices, SmartTVs and any 
other types of devices that have a web browser.

This is the Python Client for accessing the WURFL Cloud Service, and
it requires a free or paid WURFL Cloud account from ScientiaMobile:
http://www.scientiamobile.com/cloud 

## Minimum Requirements
---------------
* requests
* pylibmc


## Installation
---------------

### Install Library:

**Via PIP:**

    $ pip install wurflcloud

**Via Source:**

[Download the source code](https://github.com/WURFL/wurfl-cloud-client-python/zipball/master)

    $ pip install -r requirements.txt
    $ python setup.py build
    $ python setup.py install


### Creating a configuration file:

The configuration file for the cloud client is a file that contains
one JSON object. You must define 4 name/value pairs that represent
your configuration. The names that must be defined are `api`, `http`,
and `cache`.


## Configuration Options:

- `["api"]["version"]`
  The cloud API version. At this momement the only valid value is "v1"

- `["api"]["key"]`
  Your API key from Scientiamobile

- `["api"]["server"]`
  The URI to the cloud server without the trailing slash. At this moment the
  only valid value is "api.wurflcloud.com".

- `["http"]["timeout"]`
  How long the library should wait for the cloud to respond before timing out.
  Time in miliseconds.

- `["http"]["compression"]`
  A boolean that determines whether or not the client tries to use compression
  when contacting the cloud server.

- `["cache"]["type"]`
  The type of cache that you wish to use. There are only three valid values
  "null", "memcached", and "file".

- `["cache"]["expiration"]`
  When the cache should expire. Specify in seconds

- `["cache"]["file"]`
  File cache only.
  Specifies which file to use as a cache.

- `["cache"]["servers"]`
  Memcached only.
  A list of memcached servers to use. For example ["127.0.0.1:11211"]

- `["cache"]["binary"]`
  Memcached only.
  A boolean that specifies whether or not you want to use the binary protocol
  for memcached.

- `["cache"]["compression"]`
  Memcached only.
  A boolean that specifies whether or not you want to use compression when using
  memcached.


### Here's a memcached example:

    {
        "api": {
            "version": "v1",
            "key": "your wurfl cloud api key here",
            "server": "api.wurflcloud.com"
        },
        "http": {
            "timeout": 1000,
            "compression": true
        },
        "cache": {
                   "type": u"memcached",
                   "servers": [u"127.0.0.1:11211"],
                   "expiration": 86400,
                   "binary": True,
                   "compression": True
                }
    }

### Here's a file cache example configuration:

    {
        "api": {
            "version": "v1",
            "key": "your wurfl cloud api key here",
            "server": "api.wurflcloud.com"
        },
        "http": {
            "timeout": 1000,
            "compression": true
        },
        "cache": {
           "type": "file",
           "file": "cloud_cache.db",
           "expiration": 86400
        }
    }


## Example code

Before running the example code, please make sure that WURFL
Client Library is properly installed.

### Command line demo

    $ cd examples/
    $ python example_command.py [config_file]


Replace `[config_file]` with a config file (e.g. `filecache_config.conf`)
to run the example.

### Web browser demo

    $ python example_web.py


Now that the server's running, visit `http://localhost:8000/` with
your web browser.


## A concrete example

```python
import sys

from wurfl_cloud import Cloud
from wurfl_cloud import utils

if len(sys.argv) != 2:
    print "usage:  python example_1.py [config file]"
    sys.exit(1)

# user agent provided manually

ua =  ur'''Mozilla/5.0 (Linux; U; Android 1.5; en-gb; T-Mobile G1
Build/CRB17) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile
Safari/525.20.1'''

# get your configuration somehow, in this case from the command line
# load_config is just a helper function, the resulting config is just a
# python dictionary

config = utils.load_config(sys.argv[1])

# load the cache from the config, get_cache is another helper function

cache = utils.get_cache(config)

# we've got a configuration object and a cache object, let's create an
# object that can query the cloud

cloud = Cloud(config, cache)

try:
    # you can call cloud a couple of ways, below we call the cloud
    # trying an agent, if you only had headers, you'd call it like
    # this:  cloud(headers=headers_dict, capabilities=[....])

    dev1 = cloud(ua, capabilities=["model_name", "pointing_method"])

    # Hopefully, there were no LookupErrors (socket errors, etc...),
    # if there were, the LookupError should contain a helpful message.
    # dev1 is an object (python dict), that contains the data we're
    # looking for, if the cloud gave us errors, we return it, if the
    # error wasn't "total", we'd get a partially complete object for
    # our application, say we misspelled, "model_name" in our query,
    # then "errors" will have a message about it, but we'd still get
    #  info on "pointing_method".
    if not dev1["errors"]: print "dev1"
        print "===="
        print "'%s': %s" % ("model_name",
dev1["capabilities"]["model_name"])
        print "'%s': %s" % ("pointing_method",
            dev1["capabilities"]["pointing_method"])
    else:
        print "dev1"
        print dev1["errors"]
except LookupError as e:
    print "dev1", "==>", e
print

try:
    dev2 = cloud(ua, capabilities=["model_named", "pointing_methodd"])
    if not dev2["errors"]:
        # Will never get here those capabilities do not exist
        print "dev2"
        print "===="
        print "model_named", dev2["capabilities"]["model_named"]
        print "pointing_methodd", dev2["capabilities"]["pointing_methodd"]
    else:
        print "dev2 error"
        print "=========="
        for x, y in dev2['errors'].items():
            print "'%s': %s" % (x, y)
except LookupError as e:
    print "dev2", "==>", e
```


**2015 ScientiaMobile Incorporated**

**All Rights Reserved.**

**NOTICE**:  All information contained herein is, and remains the property of
ScientiaMobile Incorporated and its suppliers, if any.  The intellectual
and technical concepts contained herein are proprietary to ScientiaMobile
Incorporated and its suppliers and may be covered by U.S. and Foreign
Patents, patents in process, and are protected by trade secret or copyright
law. Dissemination of this information or reproduction of this material is
strictly forbidden unless prior written permission is obtained from 
ScientiaMobile Incorporated.

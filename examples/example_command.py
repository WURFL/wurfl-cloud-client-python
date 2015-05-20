import sys

from wurfl_cloud import Cloud
from wurfl_cloud import utils


if len(sys.argv) != 2:
    print "usage:  python example_command.py [config file]"
    sys.exit(1)

ua =  ur'''Mozilla/5.0 (Linux; U; Android 1.5; en-gb; T-Mobile G1 Build/CRB17) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1'''

config = utils.load_config(sys.argv[1])
cache = utils.get_cache(config)
cloud = Cloud(config, cache)

try:
    dev1 = cloud(ua, capabilities=["model_name", "pointing_method"])
    if not dev1["errors"]:
        print "dev1"
        print "===="
        print "'%s': %s" % ("model_name", dev1["capabilities"]["model_name"])
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
        # Will never get here, those capabilities do not exist"
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

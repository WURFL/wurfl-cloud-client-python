import re

from wsgiref.simple_server import make_server
from wurfl_cloud import Cloud
from wurfl_cloud import utils


class WurflCheckMiddleware(object):
    # Example WSGI Middleware library to detect visitor device
    # and load its capablities in the local WSGI environment
    def __init__(self, wrap_app):
        self.wrap_app = wrap_app
        # Create a Wurfl Cloud Config
        config = utils.load_config('filecache_config.conf')
        # Create a WURFL Cache Loader
        cache = utils.get_cache(config)
        # Create a WURFL Cloud Client
        self.Client = Cloud(config, cache)

    def __call__(self, environ, start_response):
        # Detect the visitor's device
        try:
            device = self.Client(environ.get('HTTP_USER_AGENT'), \
                capabilities=["ux_full_desktop", "model_name", "brand_name"])
            if device["errors"]:
                # Error
                print "Error: ", device["errors"]
            else:
                environ['myapp.device_capabilities'] = device["capabilities"]
        except LookupError as e:
            print "Error: ", e
        return self.wrap_app(environ, start_response)


def index(environ, start_response):
    # This function will be exected on "/"
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''<h2>Python's WURFLCloud Examples:</h2>
    <ul>
        <li><a href="detect">Desktop or Mobile Device?</a></li>
        <li><a href="show_capabilities">Show all capabilities</a></li>
    </ul>
    ''']


# Detect User-Agent as Desktop or Mobile devices
def detect(environ, start_response):
    ua = environ['HTTP_USER_AGENT']
    # Get Device Capabilities
    if not environ.get('myapp.device_capabilities'):
        capabilities = {"error": True}
    else:
        capabilities = environ['myapp.device_capabilities']
    if not "error" in capabilities:
        # Is Desktop or Mobile?
        if capabilities["ux_full_desktop"]:
            result = '<h1>This is a desktop browser.</h1>'
        else:
            result = '<h1>This is a mobile device.</h1>'
            result += '<p><b>Device:</b> %(brand)s %(model)s</p>' % \
                {'brand': capabilities["brand_name"], \
                'model': capabilities["model_name"]}
    else:
        return not_found(environ, start_response)
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''%(result)s<p><b>User-Agent:</b> %(ua)s</p>''' % \
        {'result': str(result), 'ua': str(ua)}]


# List Device's Capabilities
def show_capabilities(environ, start_response):
    # Get Device Capabilities
    if not environ.get('myapp.device_capabilities'):
        capabilities = {"error": 'empty'}
    else:
        capabilities = environ['myapp.device_capabilities']
    result = '<ul>'
    # Show all the capabilities returned by the WURFL Cloud Service
    for capability in capabilities:
        result += '<li><strong>%(key)s</strong>: %(value)s</li>' % \
            {"key": capability, "value": capabilities[capability]}
    result += '</ul>'
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''
    <h2>Device Capabilities:</h2><p>%(data)s</p>
    <h2>WSGI environment for a request:</h2><p>%(env)s</p>
    ''' % {'data': str(result), 'env': str(environ)}]


def not_found(environ, start_response):
    # Called if no URL matches.
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']


# map urls to functions
urls = [
    (r'^$', index),
    (r'detect/?$', detect),
    (r'show_capabilities/?$', show_capabilities),
]


def application(environ, start_response):
    # The main WSGI application. Dispatch the current request to
    # the functions from above and store the regular expression
    # captures in the WSGI environment as  `myapp.url_args` so that
    # the functions from above can access the url placeholders.
    #
    # If nothing matches call the `not_found` function.
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            environ['myapp.url_args'] = match.groups()
            return callback(environ, start_response)
    return not_found(environ, start_response)


wurfl_check_wrapper = WurflCheckMiddleware(application)
httpd = make_server('', 8000, wurfl_check_wrapper)
print "Serving WURFL demo on port 8000..."
httpd.serve_forever()

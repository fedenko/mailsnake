import urllib2
import urllib
try:
    import simplejson as json
except ImportError:
    import json

class MailSnake(object):

    dc = 'us1'
    base_api_url = 'https://%(dc)s.api.mailchimp.com/1.3/?method=%(method)s'

    def __init__(self, apikey = '', extra_params = {}):
        """
            Cache API key and address.
        """
        self.apikey = apikey

        self.default_params = {'apikey':apikey}
        self.default_params.update(extra_params)

        if '-' in self.apikey:
            self.dc = self.apikey.split('-')[1]
            

    def call(self, method, params = {}):
        url = self.base_api_url%{'dc': self.dc, 'method': method}
        params.update(self.default_params)

        post_data = urllib2.quote(json.dumps(params))
        headers={'Content-Type': 'application/json'}
        request = urllib2.Request(url, post_data, headers)
        response = urllib2.urlopen(request)

        return json.loads(response.read())

    def __getattr__(self, method_name):

        def get(self, *args, **kwargs):
            params = dict((i,j) for (i,j) in enumerate(args))
            params.update(kwargs)
            return self.call(method_name, params)

        return get.__get__(self)

class MailSnakeSTS(MailSnake):
    base_api_url = 'http://%(dc)s.sts.mailchimp.com/1.0/%(method)s'
#    base_api_url = 'http://127.0.0.1:6666/1.0/%(dc)s/%(method)s'
    
    def http_build_query(self, params, key=None):
        """
            Stolen from pychimp
            https://code.google.com/p/pychimp/
        """ 
        ret = {}

        for name, val in params.items():
            name = name

            if key is not None and not isinstance(key, int):
                name = "%s[%s]" % (key, name)
            if isinstance(val, dict):
                ret.update(self.http_build_query(val, name))
            elif isinstance(val, list):
                ret.update(self.http_build_query(dict(enumerate(val)), name))
            elif isinstance(val, unicode):
                ret[name] = val.encode('utf8')
            elif val is not None:
                ret[name] = val

        return ret

    def call(self, method, params={}, headers = {}):
        url = self.base_api_url%{'dc': self.dc, 'method': method}
        params.update(self.default_params)

        post_data = urllib.urlencode(self.http_build_query(params))
        request = urllib2.Request(url, post_data, headers)
        try:
            response = urllib2.urlopen(request)
            result = response.read()
        except urllib2.HTTPError, e:
            result = e.read()
            if not 'http_code' in result:
                raise

        return json.loads(result)



import codecs
import optparse
import re
import sys
import time
import types
import urllib
import urllib2
from os.path import join


class EZIDClient():
    def __init__(self, server, username, password, scheme, shoulder):
        authHandler = urllib2.HTTPBasicAuthHandler()
        authHandler.add_password("EZID", server, username, password)

        self.opener = urllib2.build_opener(authHandler)
        self.scheme = scheme
        self.shoulder = shoulder
        self.server = server

    def make_anvl(self, metadata):
        def escape(s):
            return re.sub("[%:\r\n]", lambda c: "%%%02X" % ord(c.group(0)), s)

        anvl = "\n".join("%s: %s" % (escape(name), escape(value)) for name,
            value in metadata.items()).encode("UTF-8")

        return anvl

    def mint_identifier(self, data):
        print(data)
        data = self.make_anvl(data)
        print(data)
        method = lambda : "POST"
        response = self.make_request("shoulder/%s%s" % (self.scheme, self.shoulder), method, data)
        return self.parse_response(response)

    def update_identifier(self, identifier, data):
        data = self.make_anvl(data)
        method = lambda : "POST"
        response = self.make_request("id/"+identifier, method, data)
        print(response)

    def make_request(self, path, method, data):
        request = urllib2.Request(join(self.server, path))
        request.get_method = method
        request.add_header("Content-Type", "text/plain; charset=UTF-8")
        request.add_data(data)
        try:
            response = self.opener.open(request).read()
        except urllib2.HTTPError as e:
            print(e)
            response = e.read()
        return response

    def parse_response(self, response):
        record = {}
        parts = response.split('\n')
        identifier = parts[0].split(': ')[1]
        return {'identifier' : identifier}


'''
Tightens up response content by removed superflous line breaks and whitespace.
By Doug Van Horn

---- CHANGES ----
v1.1 - 31st May 2011
Cal Leeming [Simplicity Media Ltd]
Modified regex to strip leading/trailing white space from every line, not just those with blank \n.

---- TODO ----
* Ensure whitespace isn't stripped from within <pre> or <code> or <textarea> tags.

Shamelessly stolen code from:
https://code.djangoproject.com/wiki/StripWhitespaceMiddleware
'''

import re
from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION[:2] >= (1, 5):
    from django.http.response import HttpResponseNotModified
else:
    from django.http import HttpResponseNotModified


class StripWhitespaceMiddleware(object):
    """
    Strips leading and trailing whitespace from response content.
    """

    def __init__(self):
        self.whitespace = re.compile('^\s*\n', re.MULTILINE)
        self.whitespace_lead = re.compile('^\s+', re.MULTILINE)
        self.whitespace_trail = re.compile('\s+$', re.MULTILINE)

    def process_response(self, request, response):
        # HttpResponseNotModified does not have a Content-Type header.
        # See https://code.djangoproject.com/ticket/11340
        if isinstance(response, HttpResponseNotModified):
            return response
        if 'text/plain' in response['Content-Type']:
            # We need to convert to str to use regex in python3
            # Note we assume here the encoding is going to be utf8
            c = response.content.decode('utf8')
            if hasattr(self, 'whitespace_lead'):
                c = self.whitespace_lead.sub('', c)
            if hasattr(self, 'whitespace_trail'):
                c = self.whitespace_trail.sub('\n', c)
            # Uncomment the next line to remove empty lines
            if hasattr(self, 'whitespace'):
                c = self.whitespace.sub('', c)
            # And back to a bytes object
            c = c.encode('utf8')
            response.content = c
            return response
        else:
            return response

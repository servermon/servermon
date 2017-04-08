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
            if hasattr(self, 'whitespace_lead'):
                response.content = self.whitespace_lead.sub('', response.content)
            if hasattr(self, 'whitespace_trail'):
                response.content = self.whitespace_trail.sub('\n', response.content)
            # Uncomment the next line to remove empty lines
            if hasattr(self, 'whitespace'):
                response.content = self.whitespace.sub('', response.content)
            return response
        else:
            return response

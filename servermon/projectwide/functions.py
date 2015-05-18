# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHORS DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.

'''
Module contains various helper functions

get_search_terms(text) is a function tokenizing a text and return a Set
of tokens for use by any function accepting iterables(q).
canonicalize_mac(key) is a function taken as MAC address as a string and
returning it in the proper format (aka aa:bb:cc:dd:ff:ee)
'''

from django.db.models import Q
from whoosh.analysis import SpaceSeparatedTokenizer, StopFilter
from django.utils.translation import ugettext as _
import re

def canonicalize_mac(key):
    '''
    Accepts a MAC in various formats and returns at form aa:bb:cc:dd:ee:ff

    @type  key: string
    @param key: the MAC to canonicalize

    @rtype: string
    @return: The MAC address in canonical format
    '''

    string = key.lower().replace(':','').replace('-','').replace('.','')
    result = ''

    count = 0
    for s in string:
        if (count / 2) > 0 and (count % 2) == 0:
            result += ':'
        result += s
        count += 1
    return result

def get_search_terms(text):
    '''
    Splits up a text in tokens, drops non-usefull ones and returns a Set of tokens

    @type   text: String
    @param  text: A unicode string to split up in tokens

    @rtype: Set of strings
    @return: A Set of usefull unique tokens appearing the text
    '''

    stoplist = ['and', 'is', 'it', 'an', 'as', 'at', 'have', 'in', 'yet', 'if',
            'from', 'for', 'when', 'by', 'to', 'you', 'be', 'we', 'that', 'may',
            'not', 'with', 'tbd', 'a', 'on', 'your', 'this', 'of', 'us', 'will',
            'can', 'the', 'or', 'are', 'up', 'down', 'ip',]

    analyzer = SpaceSeparatedTokenizer() | StopFilter(stoplist=stoplist)

    tokens = set([x.text for x in analyzer(text)])

    # TODO: When we go to whoosh 2.x we can drop the following and use a whoosh
    # SubstitutionFilter to the analyzer above
    tokens = set([re.sub('[\(\)/]','',x) for x in tokens])

    return tokens

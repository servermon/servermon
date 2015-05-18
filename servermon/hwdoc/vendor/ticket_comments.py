# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2014 Alexandros Kosiaris
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
Module containing implementations of ticketing based on comments
It works by looking at settings.COMMENTS_TICKETING_URL and matches strings based on
that.
'''

from hwdoc.models import Ticket
from django.conf import settings
import re

def get_tickets(equipment, closed):
    '''
    Populate tickets for equipment
    '''
    m = re.search('((?:%s[0-9]+)\s*)+' % settings.COMMENTS_TICKETING_URL,
            str(equipment.comments), re.DOTALL)
    if m:
        tickets = m.group(0).split()
        equipment.ticket_set.exclude(name__in=tickets).delete()
        for ticket in tickets:
            name = re.sub(settings.COMMENTS_TICKETING_URL, '', ticket)
            try:
                t = Ticket.objects.get(name=name)
            except Ticket.DoesNotExist:
                t = Ticket( state='open', # NOTE: Yeap hardcoded.
                            url=ticket,
                            name=name)
                t.save()
            equipment.ticket_set.add(t)
    return equipment

'''
Module containing interface to ticketing in Jira

It queries Jira's REST API.
'''

from hwdoc.models import Ticket
from django.conf import settings
from jira.client import JIRA

options = {
    'server': settings.JIRA_TICKETING['url']
}
if settings.JIRA_TICKETING['auth']['type'] == 'oauth':
    key_cert_data = None
    with open(settings.JIRA_TICKETING['auth']['key_cert'], 'r') as key_cert_file:
        key_cert_data = key_cert_file.read()
    options.update(oauth={
        'access_token': settings.JIRA_TICKETING['auth']['access_token'],
        'access_token_secret': settings.JIRA_TICKETING['auth']['access_token_secret'],
        'consumer_key': settings.JIRA_TICKETING['auth']['consumer_key'],
        'key_cert': key_cert_data
    })
elif settings.JIRA_TICKETING['auth']['type'] == 'basic':
    options.update(basic_auth=(
        settings.JIRA_TICKETING['auth']['user'],
        settings.JIRA_TICKETING['auth']['password'],
    ))

jira = JIRA(options)

def get_tickets(equipment, closed):
    '''
    Populate tickets for equipment
    '''
    search_string = 'text ~ "' + str(equipment.serial) + '"'
    if settings.JIRA_TICKETING['projects']:
        search_string += ' AND project IN (' + settings.JIRA_TICKETING['projects'] + ')'
    if not closed:
        search_string += ' AND status != closed'
    issues = list(jira.search_issues(search_string))
    for issue in issues:
        name = issue.key
        if str(issue.fields.status) == "closed":
            status = 'closed'
        else:
            status = 'open'
        t, created = Ticket.objects.update_or_create(
            name=name,
            defaults={
                'state': status,
                'url': settings.JIRA_TICKETING['url']+name,
            },
        )
        equipment.ticket_set.add(t)
    return equipment

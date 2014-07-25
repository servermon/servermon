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
        'key_cert': key_cert_data,
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
    _projects = settings.JIRA_TICKETING['projects']
    _projects_defaults = settings.JIRA_TICKETING['projects_defaults']
    if _projects:
        projects = [project.key for project in jira.projects() if project.key in _projects.keys()]
    else:
        projects = []
    # construct entire search string so we don't hammer the server repeatedly
    search_string = 'text ~ "%s"' % equipment.serial
    if projects:
        _first = True
        search_string += ' AND ('
        for project in projects:
            if _first:
                search_string += ' ( '
                _first = False
            else:
                search_string += ' ) OR ( '
            search_string += 'project = "%s"' % project
            if not closed:
                try:
                    _closed_string = _projects[project]['closed_string'] or _projects_defaults['closed_string']
                except KeyError:
                    _closed_string = _projects_defaults['closed_string']
                search_string += ' AND status != "%s"' % _closed_string
        search_string += ' ) )'
    else:
        if not closed:
            search_string += ' AND status != "%s"' % _projects_defaults['closed_string']
    issues = list(jira.search_issues(search_string))
    for issue in issues:
        name = issue.key
        try:
            _closed_string = _projects[issue.fields.project.key]['closed_string'] or _projects_defaults['closed_string']
        except KeyError:
            _closed_string = _projects_defaults['closed_string']
        if issue.fields.status.name == _closed_string.capitalize():
            status = 'closed'
        else:
            status = 'open'
        t, created = Ticket.objects.update_or_create(
            name=name,
            defaults={
                'state': status,
                'url': issue.permalink(),
            },
        )
        equipment.ticket_set.add(t)
    return equipment

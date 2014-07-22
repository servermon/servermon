'''
Module containing interface to ticketing in Jira

It queries Jira's REST API.
'''

from hwdoc.models import Ticket
from django.conf import settings
from jira.client import JIRA

options = {
    'server': settings.JIRA_TICKETING_URL
}
jira = JIRA(options)

def get_tickets(equipment, closed):
    '''
    Populate tickets for equipment
    '''
    if closed:
        issues = [issue for issue in jira.search_issues('text ~ "' + str(equipment.serial) + '"')]
    else:
        issues = [issue for issue in jira.search_issues('text ~ "' + str(equipment.serial) + '" and status != closed')]
    for issue in issues:
        name = issue.key
        if str(issue.fields.status) == "closed":
            status = 'closed'
        else:
            status = 'open'
        t = Ticket(state=status,
                   url=settings.JIRA_TICKETING_URL+name,
                   name=name)
        t.save()
        equipment.ticket_set.add(t)
    return equipment

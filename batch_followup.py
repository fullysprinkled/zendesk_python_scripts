#!/usr/bin/env python
"""
created Date: 2020-07-09
author: anthony2owaru@gmail.com
description: This script creates followup tickets in Zendesk given a list of ticket IDs
to do:
1) add proper rate limiting flow
2) additional_tags can't be added in same endpoint so we'll need to chunk ticket IDs through update_many API as an afterstep if we need to add tags to the followup ticket
"""
import requests
import json
from datetime import datetime

# initialize keys, auth session, need to secure this
zd_user = YOUR_LOGIN+"/token"
zd_apikey = YOUR_API_KEY
session = requests.Session() #initialize session
session.auth = (zd_user, zd_apikey) #auth session

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Followup Bot 1.0'
}

"""Creates a followup ticket for every ticket id in `ticket_ids`, sends `copy` to `form_id`"""
def post_followup_tickets(form_id, copy, ticket_ids):
    for ticket_id in ticket_ids:
        ##custom fields are like so:  "custom_fields": [{"id": 123, "value": "value"}, ...], replace the "{}" fields in the dict below
        data = {"ticket": {"via_followup_source_id": ticket_id, "subject": "YOUR_SUBJECT_HERE", "comment": {"body": copy}, "assignee_id":{YOUR_ASSIGNEE_ID},"ticket_form_id": form_id, "status":"pending", "custom_fields":[{"id":{YOUR_CUSTOM_FIELD_ID},"value":"{YOUR_VALUE}"}]}}
        print(data) #for debugging
        data=json.dumps(data)
        response = session.post('https://{YOUR_ORG}.zendesk.com/api/v2/tickets.json', headers=headers, data=data)
        print(response,"\n",response.text) #for debugging

def main():
    file_path = 'zendesk_ids.txt' #ensure a txt file of this name is located in the current working directory for this script
    with open(file_path) as f:
        target_ticket_ids = [line.rstrip() for line in f]
    print(target_ticket_ids)
    followup_form_id = "YOUR_TICKET_FORM_ID" # the form ID you'll assign every ticket to
    #use markdown, this is will appear as a public comment for the followup ticket
    followup_copy = "YOUR_COPY_HERE, SYNTAX EXAMPLE: Hey {{ticket.requester.first_name}}​, \n\n {{current_user.first_name}}​ here from the team! :wave: \n\n Here is a pretty picture below: \n ![Text to display if image does not load! :( ](YOUR_IMAGE_URL) \n\n Sincerely, \n\n {{current_user.first_name}}"
    post_followup_tickets(followup_form_id,followup_copy,target_ticket_ids)

if __name__ == "__main__":
    main()

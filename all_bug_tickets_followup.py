#!/usr/bin/env python
"""
created Date: 2020-06-12
author: anthony2owaru@gmail.com
description: This script creates followup tickets for all tickets linked to a jira issue key via Zendesk's Jira app integration (https://www.zendesk.com/apps/support/jira/)
Every ticket linked to a given jira issue key receives a followup ticket.

to do: 
1) add proper rate limiting flow
2) additional_tags can't be added in same endpoint so we'll need to chunk ticket IDs through update_many API as an afterstep if we need to add tags to the followup ticket

"""
import requests
import json
from datetime import datetime
import pandas as pd


# initialize keys, auth session, need to secure this
zd_user = YOUR_LOGIN+"/token"
zd_apikey = YOUR_API_KEY
session = requests.Session() #initialize session
session.auth = (zd_user, zd_apikey) #auth session

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Bug Bot 1.0'
}

"""Pulls every instance of a zendesk ticket that's been linked to jira via the integration"""
def pull_all_zd_jira_links(links_response_json):
    output={"created_at":[],"id":[],"ticket_id":[],"issue_id":[],"issue_key":[]}
    counter=1
    while len(links_response_json) > 0:
        print(len(links_response_json),"\n",links_response_json[-1],"\n page",counter)
        for links in links_response_json:
            for key in output.keys(): #loops through each dict key
                output[key].append(str(links[key]))
        since_id=links_response_json[-1]["id"]
        url="https://animoto.zendesk.com/api/services/jira/links?since_id="+str(since_id)
        links_response_json=session.get(url)
        links_response_json = links_response_json.json()["links"]
        counter+=1
    return output

"""Creates a followup ticket for every ticket id in `ticket_ids`, sends `copy` to `form_id`"""
def post_followup_tickets(form_id, copy, subject, ticket_ids):
    for ticket_id in ticket_ids:
        data = {"ticket": {"via_followup_source_id": ticket_id, "subject": subject, "comment": {"body": copy}, "ticket_form_id": form_id, "status":"pending"}}
        print(data) #for debugging
        data=json.dumps(data)
        response = session.post('https://animoto.zendesk.com/api/v2/tickets.json', headers=headers, data=data)
        print(response,"\n",response.text) #for debugging

def main():
    links_url="https://animoto.zendesk.com/api/services/jira/links?since_id=0"
    response=session.get(url)
    print(response.json()["links"][0]) #prints start page info
    data = pull_all_zd_jira_links(response.json()["links"])
    links_df=pd.DataFrame(data)
    links_df['created_at'] = pd.to_datetime(links_df['created_at']) #sets data type 
    target_jira = YOUR_JIRA_ISSUE_KEY # this is where you can place your issue key as a string. Every ticket linked to the issue key will receive a followup  see: https://support.atlassian.com/jira-software-cloud/docs/what-is-an-issue/
    target_ticket_ids = tuple(links_df.iloc[(links_df['issue_key'] == target_jira).values].ticket_id) #tuple of all ticket ids where issue_key = target jira
    print(target_ticket_ids)
    followup_form_id = YOUR_FOLLOWUP_FORM_ID # the form ID you'll assign every ticket to
    followup_copy = YOUR_FOLLOWUP_COPY_HERE #use \n for paragraphs, this will appear as a public comment for the followup ticket
    subject_copy = YOUR_SUBJECT_COPY_HERE #this is will appear as the subject line in the followup ticket
    post_followup_tickets(followup_form_id,followup_copy,subject_copy,target_ticket_ids)

if __name__ == "__main__":
    main()

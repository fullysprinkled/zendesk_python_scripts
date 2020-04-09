#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created 2020-03-16
anthony2owaru@gmail.com
"""
import requests
import json
import csv
import os
from datetime import datetime

# initialize keys, auth session, need to secure this
zd_user = 'YOUR_ZENDESK_EMAIL_LOGIN/token'
zd_apikey = 'YOUR_KEY'
session = requests.Session() #initialize session
session.auth = (zd_user, zd_apikey) #auth session

"""
Function parse_links paginates through all linked tickets
Moves data to one output dict
"""
def parse_links(link_page):
    output={"created_at":[],"issue_key":[],"ticket_id":[]} ##left side of later join, column names identical to corresponding json key names
    counter=1
    while len(link_page) > 0: #loop through link list of dicts, paginate while > 0 links
        print(len(link_page),"\n", link_page[-1],"\n page",counter)
        for link in link_page: #
            for column in output.keys(): #make construction of output dict pull from a control
                output[column].append(str(link[column]))# identical naming means "column" can reference both the JSON and the dict output we're loading to
        response = session.get("https://animoto.zendesk.com/api/services/jira/links?since_id="+str(link_page[-1]["id"]))
        link_page = response.json()["links"]
        counter+=1
    return output

"""
chunk tickets into lists of 100 and pull the ticket data from the show-many API.
all into one list of dictionaries

function will take a list of ticket ids and output a columns of ticket data
use Main() to pull id list from previous function
"""
def chunk_ids_to_api_result(id_list):
    ticket_fields=("assignee_id","created_at","id","requester_id","updated_at")
    chunks = [id_list[x:x+100] for x in range(0, len(id_list), 100)] #breaks into 100 row slices for api limitation
    show_many_url = "https://animoto.zendesk.com/api/v2/tickets/show_many?ids="
    all_ticket_data= []
    chunk_count=1
    for chunk in chunks:
        ticket_data=session.get(show_many_url +",".join(chunk))
        all_ticket_data += ticket_data.json()["tickets"]
        print("response status: {} \n chunks done:{} ({}%)".format(ticket_data,chunk_count,round((chunk_count/len(chunks))*100,2)))
        chunk_count+=1
    return {field: [str(ticket[field]) for ticket in all_ticket_data] for field in ticket_fields}

"""Function exports the two dictionaries as a csv. Dictionaries are merged in main()"""
def dict_to_csv(merged_dict):
    out_path = str(os.getcwd())+"/"+str(datetime.now())+"_palv2_output.csv"
    csv_out = zip(*merged_dict.values())
    with open(out_path, 'w') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(merged_dict.keys())
        writer.writerows(csv_out)
    print("exported to {}".format(out_path))


def main():
    since_id = 0 #set start point for pagination
    url = "https://animoto.zendesk.com/api/services/jira/links?since_id="+str(since_id)
    response = session.get(url)
    links = response.json()["links"] #is a list of dictionaries with bug link data
    parsed_links = parse_links(response.json()["links"]) #loads data into dict
    all_ticket_data = chunk_ids_to_api_result(parsed_links.get('ticket_id')) #takes the ticket_ids and gets more ticket data from ZD showmany api
    parsed_links.update(all_ticket_data) #merges both dicts together
    dict_to_csv(parsed_links) #exports all to csv in cwd

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Time Taken: {:.6f}s".format(end-start))

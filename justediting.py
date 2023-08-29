import requests
from requests.auth import HTTPBasicAuth
import json
#authenticating jira 
JIRA_API_URL = "https://tanishqa.atlassian.net/rest/api/3/search"
JIRA_AUTH_TOKEN = "ATATT3xFfGF0uv4JQP9KWk4MmyohyWAQ79CjuyyW4cEsFaF2khn5r10Io6suchDRtIUIsAMhHoGt5lAKUGH8DYW92ADro8fyknA4iNls0Th8B-sfweUSwUUAJMq6Yk0WPErsle_TGfCPfB1y7NWDZSixqdcORAIrcx56126OeFvu1H4CXa3GGnY=5825A7C5"
headers = {
  "Accept": "application/json",
  "content-Type":"application/json"
}
query={
     "jql":"project=KAN AND reporter=tanishqa"

}

response = requests.get(
   JIRA_API_URL,
   headers=headers,
   params=query,
    auth=("tanishqagargdevi@gmail.com", JIRA_AUTH_TOKEN)
)
data=response.json()
issue=data["issues"]                  
jira_data=[]
for  i in issue:
    #collecting data from jira project
    jira_data.append({
        "TicketId":i["key"],
       "Title": i["fields"]["summary"],
        "status": i["fields"]["status"]["name"],
        "assignee": i['fields']['assignee']['displayName'] if 'assignee' in i['fields'] and i['fields']['assignee'] else "Unknown",
        "reporter":i['fields']['reporter']['displayName']  if 'reporter' in i['fields'] and i['fields']['reporter'] else "Unknown",
        "qa" : i['fields']['customfield_10034']['displayName'] if 'customfield_10034' in i['fields'] and i['fields']['customfield_10034'] else "Unknown",
        "duedate" :i['fields']['duedate'] if 'duedate' in i['fields'] and i['fields']['duedate'] else "",
        "created date" :i["fields"]["created"]
    })

# Notion API and authentication details
NOTION_AUTH_TOKEN="secret_KkECYe0VpFyAyGZhrg6IG2NG6CSCmtDYjxmL0mVoEtI"
NOTION_DATABASE_ID="d3597fe2c9fd4db59cce22df4956fa17"
url=f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

# Send data to Notion
notion_headers = {
    "Authorization": f"Bearer {NOTION_AUTH_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
existing_data = {}
search_response = requests.post(url, headers=notion_headers, json={})
search_data = search_response.json()

for result in search_data.get("results", []):
   #collecting notion data
    title_property=result.get("properties", {}).get("Title ", {}).get("title", [])
    status_property = result.get("properties", {}).get("status", {}).get("multi_select", [])
    qa_property = result.get("properties", {}).get("QA", {}).get("rich_text", [])
    assignee_property = result.get("properties", {}).get("Assignee", {}).get("rich_text", [])
    reporter_property = result.get("properties", {}).get("Reporter", {}).get("rich_text", [])
    Ticket_property = result.get("properties", {}).get("Ticket Id", {}).get("rich_text", [])
    duedate_property = result.get("properties", {}).get("Due Date", {}).get("rich_text", [])

    if title_property and status_property :
        title_text = title_property[0].get("text", {}).get("content")
        qa_text = qa_property[0].get("text", {}).get("content") if qa_property else None
        assignee_text = assignee_property[0].get("text", {}).get("content")  if assignee_property else ""
        reporter_text = reporter_property[0].get("text", {}).get("content")  if reporter_property else ""
        Ticket_text = Ticket_property[0].get("text", {}).get("content")  if Ticket_property else ""
        duedate_text = duedate_property[0].get("text", {}).get("content")  if duedate_property else ""
        status_text = status_property[0].get("name")  
        page_id = result.get("id")
        if title_text and status_text :
              #collecting them in the dictionary 
              existing_data[title_text] = {
                "status": status_text,
                "page_id": page_id,
                "qa":qa_text,
                "ticket":Ticket_text,
                "duedate":duedate_text,
                "assignee":assignee_text,
                "reporter":reporter_text}
def create_notion_payload(JIRA, NOTION):
    notion_payload = {
        "properties": {}
    }
    
    if JIRA["status"] != NOTION["status"]:
        notion_payload["properties"]["status"] = {
            "multi_select": [{"name": JIRA["status"]}]
        }
    
    if JIRA["assignee"] != NOTION["assignee"]:
        notion_payload["properties"]["Assignee"] = {
            "rich_text": [{"text": {"content": JIRA["assignee"]}}]
        }
    if  JIRA["reporter"] != NOTION["reporter"]:
         notion_payload["properties"]["reporter"]={
                    "rich_text": [{"text": {"content":JIRA["reporter"]}}]
                }
    if  JIRA["TicketId"] != NOTION["ticket"]:
         notion_payload["properties"]["Ticket Id"]={
                    "rich_text": [{"text": {"content":JIRA["TicketId"]}}]
                }
    if  JIRA["duedate"] != NOTION["duedate"]:
         notion_payload["properties"]["Due Date"]={
                    "rich_text": [{"text": {"content":JIRA["duedate"]}}]
                }
    if  JIRA["qa"] != NOTION["qa"]:
         notion_payload["properties"]["QA"]={
                    "rich_text": [{"text": {"content":JIRA["qa"]}}]
                }
         
             
    return notion_payload
for data_entry in jira_data:
    jira_title = data_entry["Title"]
    jira_status = data_entry["status"]
    jira_assignee=data_entry['assignee'] or ""
    jira_reporter=data_entry['reporter']or ""
    jira_duedate=data_entry['duedate']or ""
    jira_TicketId=data_entry['TicketId']or ""
    jira_qa=data_entry['qa']or ""
    jira_createdDate=data_entry["created date"]
    
     
    existing_entry = existing_data.get(jira_title)
    
    if existing_entry:
        existing_status = existing_entry["status"]
        existing_page_id = existing_entry["page_id"]

        if (jira_status != existing_status or jira_assignee != existing_entry["assignee"] or
        jira_reporter != existing_entry["reporter"] or
        jira_duedate != existing_entry["duedate"] or
        jira_TicketId != existing_entry["ticket"] or
        jira_qa != existing_entry["qa"]):
            print("status not matching "if jira_status != existing_status  else "matching")
            print(f"{jira_assignee}assignee not matchings{existing_entry['assignee']}"if jira_assignee != existing_entry["assignee"]  else "matching")
            print("reporter  not matching "if jira_reporter != existing_entry["reporter"]  else "matching")
            print(f"{jira_duedate}duedate not matching{existing_entry['duedate']}"if jira_duedate != existing_entry["duedate"]  else "matching")
            print("ticket not matching "if jira_TicketId != existing_entry["ticket"]  else "matching")

            # Update value in Notion
            notion_payload = create_notion_payload(data_entry, existing_entry)
            if notion_payload:
                response = requests.patch(f"https://api.notion.com/v1/pages/{existing_page_id}", headers=notion_headers, json=notion_payload)
                if response.status_code == 200:
                    print(f"Updated status for '{jira_title}' in Notion.")
                else:
                    print("Error updating status in Notion:", response.status_code)
                    print(response.json())
    else:
        notion_data_payload = {
                "parent": { "database_id": NOTION_DATABASE_ID },
                "properties": {
                    "Title ": {
                        "title": [
                            {
                                "text": {
                                    "content":jira_title  ,
                                    # "link": {"url": f"hhttps://tanishqa.atlassian.net/jira/software/projects/KAN/boards/1?selectedIssue={jira_TicketId}"}

                                }
                            }
                        ]
                    },
                    "status": {
                        "multi_select": [
                            {
                            "name": jira_status
                        }
                    ]
                    },
                "Assignee": {"rich_text": [{"text": {"content": jira_assignee}}]
                },
                "Reporter": {
                    "rich_text": [{"text": {"content": jira_reporter}}]
                },
                "Due Date": {
                    "rich_text": [{"text": {"content": jira_duedate}}]
                },
                "Ticket Id": {
                    "rich_text": [{"text": {"content": jira_TicketId}}]
                },
                "QA": {
                    "rich_text": [{"text": {"content": jira_qa}}]
                    } ,
                "Created Date":{
                    "date":{"start":jira_createdDate}
        }}}
        
        response = requests.post("https://api.notion.com/v1/pages", headers=notion_headers, json=notion_data_payload)
        if response.status_code == 200:
            print("Data inserted into Notion successfully!")
        else:
            print("Error interacting with Notion:", response.status_code)
            print(response.json())


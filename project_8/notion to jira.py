import requests
from requests.auth import HTTPBasicAuth
import json
import re
#jira authentication
JIRA_EMAIL="tanishqagargdevi@gmail.com"
JIRA_BASE_URL = "https://tanishqa.atlassian.net/rest/api/3/search"
JIRA_AUTH_TOKEN = "ATATT3xFfGF0uv4JQP9KWk4MmyohyWAQ79CjuyyW4cEsFaF2khn5r10Io6suchDRtIUIsAMhHoGt5lAKUGH8DYW92ADro8fyknA4iNls0Th8B-sfweUSwUUAJMq6Yk0WPErsle_TGfCPfB1y7NWDZSixqdcORAIrcx56126OeFvu1H4CXa3GGnY=5825A7C5"

headers = {
  "Accept": "application/json",
  "content-Type":"application/json"
}
query={
    "jql":"project=KAN AND reporter=tanishqa"
}
response = requests.get(
   JIRA_BASE_URL,
   headers=headers,
   params=query,
   auth=("tanishqagargdevi@gmail.com", JIRA_AUTH_TOKEN)
)
data=response.json()
issue=data["issues"]
jira_data = []

for  i in issue:
    jira_data.append({
        "TicketId":i["key"],
       "Title": i["fields"]["summary"],
        "duedate": i["fields"]["duedate"]
    })

#notion authentication
NOTION_AUTH_TOKEN="secret_uLN6nORurOs4SuddHzkzIL44T6lDo4SWU5iqIstYPRc"
NOTION_DATABASE_ID="d3597fe2c9fd4db59cce22df4956fa17"
url=f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

notion_headers = {
    "Authorization": f"Bearer {NOTION_AUTH_TOKEN}",

    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
search_response = requests.post(url, headers=notion_headers, json={})
search_data = search_response.json()
with open('db.json', 'w', encoding='utf8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


existing_data={}
for result in search_data.get("results", []):
    title_property=result.get("properties", {}).get("Title ", {}).get("title", [])
    title_text = title_property[0].get("text", {}).get("content")
    duedate_property=result.get("properties", {}).get("Due Date", {}).get("rich_text", [])
    duedate=duedate_property[0].get("text", {}).get("content")  if duedate_property else None
    Ticket_property = result.get("properties", {}).get("Ticket Id", {}).get("rich_text", [])
    Ticket_text = Ticket_property[0].get("text", {}).get("content")  if Ticket_property else ""
    
    existing_data[title_text] = {
                "duedate": duedate,
                "jira_issue_key": Ticket_text}
    # Update JIRA issue fields based on Notion data
for jira_entry in jira_data:
    jira_title = jira_entry["Title"]
    jira_duedate = jira_entry["duedate"]

    existing_entry = existing_data.get(jira_title)
    
    if existing_entry:
       
        if existing_entry["duedate"] != jira_duedate:
            # Update JIRA issue with new due date
            jira_issue_key = existing_entry["jira_issue_key"]  # Assuming you have the issue key in existing_data
            jira_issue_url = f"https://tanishqa.atlassian.net/rest/api/3/issue/{jira_issue_key}"
            jira_issue_payload = {
                "fields": {
                    "duedate": existing_entry["duedate"]
                }
            }
            response = requests.put(
                jira_issue_url,
                headers=headers,
                json=jira_issue_payload,
                auth=("tanishqagargdevi@gmail.com", JIRA_AUTH_TOKEN)
            )
            if response.status_code == 204:
                print(f"Updated due date for '{jira_title}' in JIRA.")
            else:
                print("Error updating due date in JIRA:", response.status_code)
                print(response.json())
    else:
        print(f"Title '{jira_title}' not found in existing Notion data.")
            


from __future__ import print_function
import httplib2
import urllib2
import urllib
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Terminal Calendar'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_calendars(service):
    page_token = None
    result = []
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        # print(calendar_list_entry['summary'])
        result.append(calendar_list_entry)
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break
    return result

def get_events(service, calendar):
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events for ', calendar['summary'])
    eventsResult = service.events().list(
        calendarId=calendar['id'], timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        # print(event)
        start = event['start'].get('dateTime', event['start'].get('date'))
        if 'summary' in event:
            print(start, event['summary'])

def add_event(service, quicktext):
    created_event = service.events().quickAdd(
    calendarId='primary',
    text=quicktext).execute()

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    driver = webdriver.Firefox()
    driver.get("https://finalexams.rutgers.edu/")
    assert "Final Exam Schedules" in driver.title
    driver.find_element_by_link_text('Login').click()
    elem = driver.find_element_by_name("username")
    username = raw_input("What is your netid?")
    elem.send_keys(username)
    username = raw_input("What is your password?")
    elem = driver.find_element_by_name("password")
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)
    # assert "No results found." not in driver.page_source
    assert "Final Exam Schedules" in driver.title

    table = driver.find_elements_by_css_selector('table>tbody>tr')
    for row in table:
        cells = row.find_elements_by_css_selector('table>tbody>tr>td')
        print(cells[3].text, ' ', cells[5].text)
        quicktext = str(cells[3].text) + ' FINAL ' + str(cells[5].text)
        add_event(service, quicktext)

    driver.close()

    # calendars = get_calendars(service)
    # for calendar in calendars:
    #     events = get_events(service, calendar)
    #     # break

if __name__ == '__main__':
    main()

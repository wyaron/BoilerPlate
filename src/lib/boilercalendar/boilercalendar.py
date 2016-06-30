## --------------------------------------------------------------------
## boiler controller
##
## Authors   : Yaron Weinsberg and Meir Tsvi
## License   : GPL Version 3
## --------------------------------------------------------------------
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## --------------------------------------------------------------------

from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import uuid
from googleapiclient import channel

import logging

import os
CREDENTIAL_FILE_PATH=os.path.dirname(os.path.realpath(__file__)) + "/../../config/credentials.json"

from config import CALENDAR_SCOPES, CALENDAR_ID

# set up out specific calendar
scopes = CALENDAR_SCOPES

# few globals we should initialize
service = None
http_auth = None
calendar = None

def init():
    global service
    global http_auth
    global calendar

    service = None
    http_auth = None
    calendar = None

def authenticate():
    global service
    global http_auth
    global calendar
    
    try:
        # read credentials
    	credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE_PATH, scopes)

	# authorize and get the calendar service
	http_auth = credentials.authorize(Http())
	service = discovery.build('calendar', 'v3', http=http_auth)
	calendar = service.calendars().get(calendarId=CALENDAR_ID).execute()
    except:
	logging.getLogger('BoilerLogger').error('failed to authenticate to google calendar service, will retry...')
	init()


# get calendar events in a window sorted by start time
def get_calendar_events(start_utc_time, end_utc_time, maxEvents=5):
  global service
  
  if service is None:
     init()
     authenticate()
     
  # did it work ? if not, the client of this class should retry
  if service is None:
     raise Exception('can not connect to google calendar')
     
  logging.getLogger('BoilerLogger').debug("Getting calendar events from: %s to %s" % (start_utc_time, end_utc_time))
  events = service.events().list(calendarId=CALENDAR_ID, orderBy="startTime",
                                 singleEvents=True, timeMin=start_utc_time, timeMax=end_utc_time, maxResults=maxEvents).execute()				 
  return events['items']






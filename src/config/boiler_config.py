# -*- coding: utf-8-*-

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

# logging
import glob
import logging
import logging.handlers

###################################################################################
####################### MANDATORY CONFIGURATION (YOUR SECRETS) ###################
###################################################################################

# calendar id to use (for setting up boiler events)
CALENDAR_ID='XXX@gmail.com,'
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# email account to use for sending emails regarding boiler events
GMAIL_USER = 'XXX@gmail.com'
GMAIL_PASSWORD = 'XXXXXXXX'

# the list of recipients that will get the boiler events (via the account above)
EMAIL_TO = ['meir.tsvi@live.com']
EMAIL_SUBJECT = 'Boiler controller event'

# API key used by GCM (to send notification to the mobile app)
PUSH_NOTIFICATION_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX";

###################################################################################
################# GENERAL CONFIGURATION (YOU CAN USE THE DEFAULT ##################*
###################################################################################

# types of boiler summary strings (in the calendar)
boiler_summary_tags = ['boiler', 'dud', 'דוד', 'בוילר']

# how often to poll google calendar for boiler events
POLL_BOILER_EVENT_MINS = 10

# how often to dump boiler activity statistics
POLL_STATISTICS_SECS = 6*3600

# max hours we allow the boiler to be on per day
MAX_BOILER_TIME_PER_DAY_HOURS = 6

# log filename
import os
LOG_FILENAME=os.path.dirname(os.path.realpath(__file__)) + "/../../log/log_boiler.out"

# logging level
BOILER_LOG_LEVEL = logging.DEBUG
BOILER_CONSOLE_LOG_LEVEL = logging.DEBUG  # for less spew set logging.INFO

###################################################################################
## Setting up logging...
###################################################################################
# Set up a specific logger with our desired output level
boilog = logging.getLogger('BoilerLogger')
boilog.setLevel(BOILER_LOG_LEVEL)

# add the file handler to the logger
file_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=4*1024*1024, backupCount=5)
boilog.addHandler(file_handler)

# create a console handler 
console_handler = logging.StreamHandler()
console_handler.setLevel(BOILER_CONSOLE_LOG_LEVEL)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
boilog.addHandler(console_handler)

def get_logfile_names():
    try:
        lst = glob.glob('%s*' % LOG_FILENAME)
    except:
        lst = []    
    return lst

def get_list_as_string(list_or_iterator):
    return "[" + ", ".join( x.decode("utf-8") for x in list_or_iterator) + "]"
       
def log_config_string():
    cfg = '\n\n'
    cfg += 'Boiler Configuration\n'
    cfg += '========================\n'
    cfg += ('boiler_calendar_tags: %s\n' % get_list_as_string(boiler_summary_tags))
    cfg += ('email_to: %s\n' % EMAIL_TO)
    cfg += ('email_subject: %s\n' % EMAIL_SUBJECT)
    cfg += ('POLL_BOILER_EVENT_MINS: %s\n' % POLL_BOILER_EVENT_MINS)
    cfg += ('POLL_STATISTICS_SECS: %s\n' % POLL_STATISTICS_SECS)
    cfg += ('MAX_BOILER_TIME_PER_DAY_HOURS: %s\n' % MAX_BOILER_TIME_PER_DAY_HOURS)
    cfg += ('log file names: %s\n' % get_list_as_string(get_logfile_names()))
    cfg += '\n\n'
    return cfg

def log_config():
    boilog.debug(log_config_string())

       
       
#!/usr/bin/python
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

import os, sys, pprint
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

# configuration path
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

# get all configuration parameters
from config import *

# email support
from send_email import *

# get the relay functionality
from relay import *

# get the sms push notification functionality
from notify import *

# get google calendar functionality
from boilercalendar import *

from datetime import *
from dateutil.parser import parse
from dateutil.tz import *
from tzlocal import get_localzone

import threading
from collections import defaultdict

# the next boiler calendar event
# this is the event we rely on for turning the relay on/off
next_boiler_event = None

# check if we should turn on the boiler or turn it off
def should_turn_on(time_now, event_start_time, event_end_time):
    return time_now >= event_start_time and time_now < event_end_time


# check if we got a boiler event that matches the one we already have (args can be None)
def is_same_boiler_event(boiler_event1, boiler_event2):
    return cmp(boiler_event1, boiler_event2) == 0


# create a boiler event from a calendar event
def make_boiler_event(event):
    if 'start' not in event.keys():
        return None
    if 'end' not in event.keys():
        return None
    if 'dateTime' not in event['start'].keys():
        return None
    if 'dateTime' not in event['end'].keys():
        return None
    if 'attendees' in event:
        # this is an invite that we should skip (no boiler event invitation are currently supported)
	boilog.debug("Skip event with multiple participants.")
        return None

    
    # we have a valid event (with proper start and end dateTime)
    event_start = event['start']['dateTime']
    event_end = event['end']['dateTime']
    summary = event['summary'].encode("utf-8", "replace")
    if summary.lower() in boiler_summary_tags:
        try:
            event_start_utc = parse(event_start)
            event_end_utc = parse(event_end)
        except:
            boilog.error("Error while processing boiler evnt - ignoring event...")
            return None
        else:
            return {'summary': summary, 'startTime': event_start_utc, 'endTime': event_end_utc}


# set up a timer to trigger our logic every POLL_BOILER_EVENT_MINS minutes
# the logic could be changed to utilize push notifications
# but at this point google require to use a web service to receive the
# event via a channel.

next_poll_time = datetime.now(tzutc())

# a dictionary of boiler operation time
boiler_activity = defaultdict(int)

# keep boiler on time and off time for statistics
boiler_on_time = None
boiler_off_time = None

def stop_and_exit():
    relay.stop_relay()
    relay.cleanup()
    # send all log files via email for debugging...
    sys.exit(1)

def start_boiler(time_now_utc):    
    global boiler_on_time
    global boiler_off_time
    boilog.debug("about to start boiler...")

    # sanity check
    boiler_is_on = relay.is_output_high()  # read from relay (HW)
    if boiler_is_on:
        # this is bad may indicate a serious bug
	notify_phone.send_push_mesage('potential bug: relay is on when start_boiler is called', datetime.now())
	stop_and_exit()	

    relay.start_relay()
    notify_phone.send_push_mesage('boiler is ON', datetime.now())
    send_email(EMAIL_TO, EMAIL_SUBJECT, 'Boiler is turned ON! \n\n time: %s\n\n' %  str(datetime.now()))
    boiler_on_time = time_now_utc
    boiler_off_time = None

def stop_boiler(time_now_utc):
    global boiler_on_time
    global boiler_off_time
    boilog.debug("about to stop boiler...")

    # sanity check
    boiler_is_on = relay.is_output_high()  # read from relay (HW)
    if not boiler_is_on:
        # this is bad may indicate a serious bug
	notify_phone.send_push_mesage('potential bug: relay is off when stop_boiler is called', datetime.now())
	stop_and_exit()	

    relay.stop_relay()
    boiler_off_time = time_now_utc
    on_time = (boiler_off_time - boiler_on_time).total_seconds()
    notify_phone.send_push_mesage('boiler is OFF [%d min]' % (on_time / 60), datetime.now())
    send_email(EMAIL_TO, EMAIL_SUBJECT, 'Boiler is turned OFF! \n\n time: %s\n\n' %  str(datetime.now()))

    # update daily statistics
    boiler_activity[str(date.today())] += on_time
    boiler_on_time = None
    boiler_off_time = None
    
def check_boiler_event_wrapper():
    try:
        check_boiler_event()
    except Exception as e:
        boilog.error('unrecoverable exception in check_boiler_event, exit boiler controller !!!\n\n' + str(e))	
	notify_phone.send_push_mesage('boiler controller CRASHED [exiting]', datetime.now())
	boiler_is_on = relay.is_output_high()  # read from relay (HW)
        if boiler_is_on:
	    boilog.debug('check_boiler_event_wrapper crashed while boiler was ON, turn it off and exit')
	    send_email(EMAIL_TO, EMAIL_SUBJECT,
	               'Unrecoverable exception in check_boiler_event, exit boiler controller !!!\n\n Boiler was <ON> while it happened\n\n' + str(e),
		       get_logfile_names())		    
	    stop_and_exit()
 	else:
	   boilog.debug('check_boiler_event_wrapper crashed  while boiler was OFF, turn it off and exit')
           send_email(EMAIL_TO, EMAIL_SUBJECT,
	              'Unrecoverable exception in check_boiler_event, exit boiler controller !!!\n\n Boiler was <OFF> while it happened\n\n' + str(e),
		      get_logfile_names())

def check_boiler_event():
    global next_boiler_event
    global next_poll_time
    global boiler_on_time
    global boiler_off_time
    global MAX_BOILER_TIME_PER_DAY_HOURS

    # time window in which to look for boiler events
    BOILER_EVENT_TIME_WINDOW_HOURS = 4

    # do our periodic work
    now_utc = datetime.utcnow()
    now_plus_window = now_utc + timedelta(hours=BOILER_EVENT_TIME_WINDOW_HOURS)
    now = now_utc.isoformat() + 'Z'  # 'Z' indicates UTC time
    later = now_plus_window.isoformat() + 'Z'  # 'Z' indicates UTC time

    boilog.debug('====> check_boiler_event START time: %s' % next_poll_time.astimezone(get_localzone()))

    # get calendar events and find the first relevant one
    try:
        events = boilercalendar.get_calendar_events(now, later, 5)
    except:
        # we could not read any calendar events, so we will try the next time
        boilog.error('can not read boiler events...will retry in several minutes...')
	send_email(EMAIL_TO, EMAIL_SUBJECT, 'Can not read boiler events...will retry in several minutes...!!!\n\n')
    else:
	# we only want the first boiler event (they are sorted by start time)
        for event in events:
            boiler_event = make_boiler_event(event)
            if boiler_event is None:
                continue
		
	    # we found the first boiler event
	    if is_same_boiler_event(next_boiler_event, boiler_event):
                boilog.debug('we already know about the received boiler event...ignoring.')
                break
            else:
                boilog.debug('we got an updated or new boiler event, using it.')
                next_boiler_event = boiler_event
		break
	else:
	    boilog.debug('could not find any boiler events any time soon...')
	    if next_boiler_event is not None:
	       # this case indicates that we no longer have a boiler event. it can happen
	       # if we poll right after the event ended or if the  user
	       # have cancled or removed it. as we still have a valid next_boiler_event
	       # it means that the boiler may be on, so if this is the case, we must
	       # turn it off and set the next_boiler_event to None.

	       # check the hardware if the boiler is currently on
	       boiler_is_on = relay.is_output_high()
      	       boilog.debug('next_boiler_event is about to be CANCLED, boiler_is_on ? %s' % boiler_is_on)
	       if not boiler_is_on:
	           # we have nothing to do as the next_boiler_event has not activated the boiler yet
		   boilog.debug('next_boiler_event is cancled (boiler was off)')
	       else:
	           # the boiler is on so we must turn it off		   
		   stop_boiler(datetime.now(tzutc()))
		   boilog.debug('next_boiler_event is cancled (boiler was on / event may be over when we polled)')

	       # make sure to disable it
	       next_boiler_event = None	       	       
    finally:        
	boilog.debug('inside main processing boiler loop...')
	
	# if we have a valid boiler event, process it
        if next_boiler_event is not None:	    
            boilog.debug("Processing our next boiler event:  %s" % next_boiler_event['summary'])
            boilog.debug(" + start boiler at: %s" % next_boiler_event['startTime'])
            boilog.debug(" + stop boiler at: %s" % next_boiler_event['endTime'])
            ontime = next_boiler_event['endTime'] - next_boiler_event['startTime']
            boilog.debug(" + duration: %s" % str(ontime))
            time_now_utc = datetime.now(tzutc())
	    if next_boiler_event['startTime'] >= time_now_utc:	    
	       time_to_on = next_boiler_event['startTime'] - time_now_utc
	       boilog.debug(" + time to switch on (in the future): %s" % time_to_on)
	    else: 
               time_to_on = time_now_utc - next_boiler_event['startTime']
	       boilog.debug(" + time to switch on has passed already: %s" % time_to_on)

            # check whether we need to turn the boiler on or off
            # note that we only turn it off if it was on before
            boiler_is_on = relay.is_output_high()  # read from relay (HW)
            now_in_boiler_event = should_turn_on(time_now_utc, next_boiler_event['startTime'], next_boiler_event['endTime'])
            max_boiler_time_per_day_sec = timedelta(hours=MAX_BOILER_TIME_PER_DAY_HOURS).total_seconds()
	    if boiler_is_on:
	        on_time_daily = (time_now_utc - boiler_on_time).total_seconds() + boiler_activity[str(date.today())]
	        boiler_quota_reached = on_time_daily >= max_boiler_time_per_day_sec
	    else:
	        boiler_quota_reached = boiler_activity[str(date.today())] >= max_boiler_time_per_day_sec

            boilog.debug(" + boiler is on ? %s" % boiler_is_on)
            boilog.debug(" + now in boiler event ? %s" % now_in_boiler_event)
            boilog.debug(" + boiler quota reached ? %s" % boiler_quota_reached)

	    # logic for turning the boiler on / off
	    msg_time_now = datetime.now()
            if now_in_boiler_event and not boiler_is_on:
	       if  not boiler_quota_reached:
                   start_boiler(time_now_utc)
	       else:	           
	           notify_phone.send_push_mesage('boiler quota reached, will not start boiler !', msg_time_now)
		   send_email(EMAIL_TO, EMAIL_SUBJECT, 'Boiler quota reached, will not start the boiler !%s\n\n' % str(msg_time_now))
            elif now_in_boiler_event and boiler_is_on and boiler_quota_reached:
	        stop_boiler(time_now_utc)
	        notify_phone.send_push_mesage('boiler quota reached, stopping boiler now !', msg_time_now)				
		send_email(EMAIL_TO, EMAIL_SUBJECT, 'Boiler quota reached, stopping the boiler now !%s\n\n' % str(msg_time_now))
            elif not now_in_boiler_event and boiler_is_on:
                stop_boiler(time_now_utc)            
        else:
            boilog.debug('we have no pending boiler event, will keep polling...')

    # calculate how much to wait so that we run every poll_time_delta
    global POLL_BOILER_EVENT_MINS
    poll_time_delta = timedelta(minutes=POLL_BOILER_EVENT_MINS)
    time_now_utc = datetime.now(tzutc())
    
    # if we are waiting for a boiler event to start before the poll time, shorten the poll interval
    if next_boiler_event is not None and next_boiler_event['startTime'] > time_now_utc:
        diff = (next_boiler_event['startTime'] - time_now_utc).total_seconds()
	diff += 30   # add 30 seconds so we won't wake up eariler than expected (will also work)
        deltatime_to_on = timedelta(seconds=diff)
    elif next_boiler_event is not None and next_boiler_event['endTime'] > time_now_utc:
        diff = (next_boiler_event['endTime'] - time_now_utc).total_seconds()
	diff += 30   # add 30 seconds
	deltatime_to_on = timedelta(seconds=diff)
    else:
        deltatime_to_on = poll_time_delta

    # wait till the minimum of the two
    poll_time_delta = min(deltatime_to_on, poll_time_delta)
    next_poll_time = next_poll_time + poll_time_delta
    next_poll_delta = next_poll_time - time_now_utc

    boilog.debug('Next time to check for boiler events: %s' % next_poll_time.astimezone(get_localzone()))
    boilog.debug('====> Time to wait till next poll time: %s' % (next_poll_delta / 60))
    threading.Timer(next_poll_delta.total_seconds(), check_boiler_event_wrapper).start()


def process_statistics():

    # print statistics
    daily_stats = pprint.pformat(boiler_activity)
    boilog.info(daily_stats)
    send_email(EMAIL_TO, EMAIL_SUBJECT, 'Boiler statistics summary:%s\n\n' % daily_stats)

    global POLL_STATISTICS_SECS
    stat_thread = threading.Timer(POLL_STATISTICS_SECS, process_statistics)
    stat_thread.setDaemon(True)
    stat_thread.start()

if __name__ == '__main__':    
    boilog.info('*' * 40)
    boilog.info('boiler controller started...')
    boilog.info('created by: Yaron Weinsberg')
    boilog.info('*' * 40)

    # dump configuration
    log_config()

    import lan
    controller_ip = lan.get_lan_ip()
    start_time = datetime.now()
    notify_phone.send_push_mesage('boiler controller service started on: %s' % controller_ip, start_time)
    send_email(EMAIL_TO, EMAIL_SUBJECT, 'Boiler service started at: %s on host: %s\n\n%s' %
               (str(start_time), controller_ip, log_config_string().encode("utf-8", "replace")))
    
    # make sure we start in a clean HW state
    relay.stop_relay()

    # start the action
    check_boiler_event_wrapper()
    process_statistics()


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

from gcm import GCM
import logging
from config import PUSH_NOTIFICATION_API_KEY

# Topic Messaging

def send_push_mesage(msg, the_time):
   logging.getLogger('BoilerLogger').debug('sending boiler sms message: %s' % msg)
   gcm = GCM(PUSH_NOTIFICATION_API_KEY)
   data = {'message': msg, 'time': str(the_time)}
   topic = 'global'
   try:
     gcm.send_topic_message(topic=topic, data=data)
   except:
     logging.getLogger('BoilerLogger').debug('can not send push message, ignore.')


# BoilerPlate - a template for making your water heater (boiler) smarter...

In Israel the use of **solar** water heating systems is very common. More that 40% of homes use it daily and save lots of money. However, we do have some cold days... Winter in Israel starts in October-November and ends in March. For most Western Europeans, the winter will not look too serious...but still we all miss the sun and there is not enough of it for heating the water for us to shower. Thus we are forced to use an **electric** water heating system. Ask any Israeli about a bad winter day and he will tell you a story about a cold shower since he forgot to turn on the boiler...

Well.. it happens to me too several times and worse than that, it happened to my wife since I forgot to turn it on when she had asked...  I figured, with all the hype around smart homes, it should be very easy to find and purchase a nice looking gadget, with wifi capabilities and a mobile application to control my boiler. Indeed, there are several products that achieve this goal, however, some requires an online service subsription with monthly fees, some are *very* expensive and all of them are closed systems that must be trusted by the users. It is not that I don't trust them, its just that since it messes with my home electriciry - I want to be in full control. I want to know *exactly* how it operates and I want to be able to customize it for my specific needs. I want an open sourced controller, one that cab be extended and improved by the community. In addition, I don't really need a fancy user interface. I would like to use my good old google calendar to set up the events for turning on/off my boiler. So the idea is to simply set up **boiler** events in my calendar that will be read and executed by the boiler controller application. Some people will argue that a dedicated mobile application is a must. I won't argue, by all means, fee free to add it to the repository. 

Before we start with the details so you can easily replicate the application for your own needs, few words of caustion. This is electricity we are playing with. I take no responsibility for the code, for the products that I've used to implement the controller, etc. You need to be sure you undertand what you are doing or consult with a professional in case you really want to use the controller in your home. 

Lets start...

# Hardware 
You need to purchase some hardware. Here is the inventory list I've used for my prototype:
  - Raspberry Pi 2 Model B - around 35$ ![pi 2](https://raw.githubusercontent.com/wyaron/BoilerPlate/master/pi2.png "Pi 2 Image") (Note that you can also get the Pi 3 at a similiar price) 
  - A 20/30A relay such as: [Seeedstudio ACT05161P Grove SPDT 30A](http://www.dx.com/p/seeedstudio-act05161p-grove-spdt-30a-single-pole-double-throw-relay-module-blue-green-343494#.V3OdWLt97RZ) ![relay module](https://raw.githubusercontent.com/wyaron/BoilerPlate/master/relay30A.jpg "Relay Image")

# Raspberry Pi 2 Setup

You'll need to follow one of the 9many) online tutorials on how to install Raspbian on your raspberry pi. Start with [noobs](https://www.raspberrypi.org/help/noobs-setup/) or use a ready made image. Once you have Raspbian, make sure you have Python 2.7 installed. 

# Installation & Configuration

Next step is to clone the git repository and configure the app so it can use your calendar, send event notification (via push notifications and email), service credentials, etc. 

```sh
$ echo "clone the git repository"
$ git clone https://github.com/wyaron/BoilerPlate.git
$ cd BoilerPlate/src/config
```

Once the git repository is cloned, we need to set it up. The boiler application is using Google Calendar API in order to interact with your calendar. In order to do that, we must create a google project with calendar APIs enabled and allow it to read **your** calendar events. Sharing your calendar events is rather simple, in your google calendar settings you can choose to share your calendar with peers by providing their email addresses. 
The google project we are about to create will have a unique project id emails assigned to it. We will use share our calendar with the email thus allowing it to read our calendar. In order to issue a REST request to this project, the clients will need a json file that we generate (credentials.json). This file is your *secret* so please do not distribute. 

## Create a Google project to access our Calendar
Lets start with creating a google project for the controller to use. 

[Meir ?]

## Generate the credentials for our project
We need to generate the credentials so that we can access the calendar APIs ir provides. The generated credentials should be placed at the config directory of our source tree. 

## Share your calendar with the Google project
OK, now that we have such a project, grab its email address. Lets assume the email address is: "myboilerservice@appspot.gserviceaccount.com". Go to your gmail calendar web site and click on *settings*. In the Calendar settings page, there are 3 tabs indicated by: "General", "Calendars" and "Labs" as shown in the following  figure:

![pi 2](https://raw.githubusercontent.com/wyaron/BoilerPlate/master/calendar-setup.PNG "Calendar Tab"). 

In this page, look for the sharing link under "SHARING":

![pi 2](https://raw.githubusercontent.com/wyaron/BoilerPlate/master/sharing-tab.png "sharing").

Once you click on it, you'll see a list of people with whom you would like to share your calendar. Go ahead and give our project (identified by its emails: "myboilerservice@appspot.gserviceaccount.com") an access to see all event details. 

## Configure Controller properties

Under the config directory in our repository, the file "boiler_config.py" holds the rest of the configuration attributes for our controller. This following table provides the attribute and its purpose. You must go over all the properties and make sure they are properly set. 

| Attributte        | Purpose                            | Default                      |
| ----------------- | ---------------------------------- | ---------------------------- |
| attr1             |oal 1                            | 100                             |
| attr1             |oal 1                            | 100                             |
| attr1             |oal 1                            | 100                             |
| attr1             |oal 1                            | 100                             |
| attr1             |oal 1                            | 100                             |
| attr1             |oal 1                            | 100                             |
| attr1             |oal 1                            | 100                             |

# Controller Operational Overview
This sections briefly explains how the controller operates. If you feel you can improve it or make the code simpler, feel free to do so. 






# Future Work
Some friends already requested some features that we have not implemented yet. Some of the features are:
1. Add an andorid/iOs application
2. Add support for an electric valve - some boilers (in rather old apartments) require to close a water valve before turning on the boiler. If we can automate it as part of turning on the boiler it will be great.
3. Add display to the controller - provide notifications and even maybe a way to manually create events
4. more ?



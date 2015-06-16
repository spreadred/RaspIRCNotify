# RaspIRCNotify

Uses Raspberry Pi as IRC notification device

Creator: Rohn Adams - rohn.adams@gmail.com

This software is made freely available to everyone under the MIT License. http://opensource.org/licenses/MIT

"Do as thou wilt, shall be the whole of the law"

A simple project I created to help myself learn to work with a Raspberry Pi and GPIO. In essence, the software uses a Python IRC
library found at https://bitbucket.org/jaraco/irc to create a bot which connects to the specified IRC server and joins the 
channel specified in the script. Once in the channel, the bot will monitor incoming chat messages, as well as incoming queries/messages directed at the user. 

Based upon the type/target of the incoming message, the bot uses the Rpi.GPIO library https://pypi.python.org/pypi/RPi.GPIO to set the state of three different LEDs (red, yellow, and green). The red LED is illuminated upon an error, such as no connection to the server, the green LED is illuminated when the bot receives a PRIVMSG (query), the yellow light is illuminated when a new message is seen in the channel, as long as the nick/source of that message is not in the ignore list. In addition, there is a button located on the breadboard that allows the user to acknowledge the notification, and turn the LEDs off (rather silly and pointless at the moment).

Obviously the script can be customized by changing certain variables and/or parameters passed to the different functions. The most important of these would be changing the pin numbers associated with the LEDs and button as well as changing the server, port, nick and channel for IRC.

In the future, the script will probably head more in the direction of being more of "IRC voicemail" device. As (or if) the project becomes more complicated, breadboard configuration/images should be made available on this project's GitHub page.






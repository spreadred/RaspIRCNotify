# Raspberry Pi IRC Notificadtion Device
#
# This script enables a Raspberry Pi with a properly set up breadboard to act
# as a simple notification device for channel messages. It could easily be expanded
# to be more functional.
# 
# Created 5/16/15 by Rohn Adams
import RPi.GPIO as GPIO
import irc.bot
import irc.client

# Component pin numbers, change to suit needs
GREEN_LED = 18
RED_LED = 23
YELLOW_LED = 16
BUTTON = 19

# small class to represent an LED
class LED():
    def __init__(self, pin):
        self.pin = pin
        self.on = False
        
        # we must set the LED up with GPIO
        GPIO.setup(pin, GPIO.OUT, initial=False)
        
    def turn_on(self):
        GPIO.output(self.pin, True)
        self.on = True
        
    def turn_off(self):
        GPIO.output(self.pin, False)
        self.on = False
        
# IRC Notification bot class
class IRCNotifier(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, button, red, yellow, green, nick_ignore,  port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

        # set the correct GPIO number scheme
        GPIO.setmode(GPIO.BCM)
        # set up the reset notifications button    
        GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # create our LED objects
        self.led_green = LED(green)
        self.led_red = LED(red)
        self.led_yellow = LED(yellow)
        
        self.button = button
        self.nick_ignore = nick_ignore # used to ignore messages from a nick 
     
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")
            
    def on_privmsg(self, c, e):
        if not self.led_green.on:
            self.led_green.turn_on()
            
    def on_pubmsg(self, c, e):
        nick = e.source.split("!")[0]
        
        # enforce our nick ignore
        if not self.led_yellow.on and nick != self.nick_ignore:
            self.led_yellow.turn_on()

    def on_welcome(self, connection, event):
        if self.led_red.on:
            self.led_red.turn_off()
        
        # check to make sure channel exists    
        if irc.client.is_channel(self.channel):
            connection.join(self.channel)
  
    # check if the reset button has been pressed, turn off lights if so          
    def check_button(self):
        if not GPIO.input(self.button):
            self.led_green.turn_off()
            self.led_red.turn_off()
            self.led_yellow.turn_off() 

while 1:
    try:
        bot = IRCNotifier("#pibot", "raspBot", "108.59.11.230", BUTTON, RED_LED, YELLOW_LED, GREEN_LED, "kptkommie")
        
        # set timer for button state checking
        bot.reactor.execute_every(.2, bot.check_button)
        
        # start the main bot loop
        bot.start()
        
    finally:
        bot.disconnect("RasPi IRC Notifier 0.1")
        GPIO.cleanup()
        bot.die()

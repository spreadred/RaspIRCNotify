import RPi.GPIO as GPIO
import irc.bot
import irc.client


GREEN_LED = 18
RED_LED = 23
YELLOW_LED = 16
BUTTON = 19

class LED():
    def __init__(self, pin):
        self.pin = pin
        self.on = False
        
        GPIO.setup(pin, GPIO.OUT, initial=False)
        
    def turn_on(self):
        GPIO.output(self.pin, True)
        self.on = True
        
    def turn_off(self):
        GPIO.output(self.pin, False)
        self.on = False
        

class IRCNotifier(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, button, red, yellow, green, nick_ignore,  port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

        GPIO.setmode(GPIO.BCM)    
        GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.led_green = LED(green)
        self.led_red = LED(red)
        self.led_yellow = LED(yellow)
        self.button = button
        self.nick_ignore = nick_ignore
     
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")
            
    def on_privmsg(self, c, e):
        if not self.led_green.on:
            self.led_green.turn_on()
            
    def on_pubmsg(self, c, e):
        print e.source

        if not self.led_yellow.on and not self.nick_ignore in e.source:
            self.led_yellow.turn_on()

    def on_welcome(self, connection, event):
        if self.led_red.on:
            self.led_red.turn_off()
            
        if irc.client.is_channel(self.channel):
            connection.join(self.channel)
            
    def check_button(self):
        if not GPIO.input(self.button):
            self.led_green.turn_off()
            self.led_red.turn_off()
            self.led_yellow.turn_off() 

while 1:
    try:
        bot = IRCNotifier("#pibot", "raspBot", "108.59.11.230", BUTTON, RED_LED, YELLOW_LED, GREEN_LED, "kptkommie")
        bot.reactor.execute_every(.2, bot.check_button)
        bot.start()
        
    finally:
        bot.disconnect("RasPi IRC Notifier 0.1")
        GPIO.cleanup()
        bot.die()

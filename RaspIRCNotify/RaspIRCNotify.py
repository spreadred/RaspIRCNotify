#
# Raspberry Pi IRC Notification Device
#
# This script enables a Raspberry Pi with a properly set up breadboard to act
# as a simple notification device for channel messages. It could easily be expanded
# to be more functional.
#
# 
# 
# Created 5/16/15 by Rohn Adams (KaptainKommie)
import RPi.GPIO as GPIO
import irc.bot
import irc.client
import pyttsx

# Component pin numbers, change to suit needs
GREEN_LED = 18
RED_LED = 23
YELLOW_LED = 16
BUTTON = 19
TXT2SPEECH = True

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
    def __init__(self, channel, nickname, server, button, red, yellow, green, nick_ignore, speech, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        
        # set channel to join and create var for txt2speech engine
        self.channel = channel
        self.engine = None
        
        # set the correct GPIO number scheme
        GPIO.setmode(GPIO.BCM)
        # set up the reset notifications button    
        GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # create our LED objects
        self.led_green = LED(green)
        self.led_red = LED(red)
        self.led_yellow = LED(yellow)
        
        # button setup
        self.button = button
        
        # used to ignore messages from a nick
        self.nick_ignore = nick_ignore
        
        # text to speech setup
        self.speech = speech
        
        # try to init txt2speech (pyttsx library)
        if self.speech == True: 
            try:
                self.engine = pyttsx.init(debug=True)
                self.engine.connect('finished-utterance', self.on_speech_end)
                self.engine.connect('error', self.on_speech_error)
                self.engine.setProperty("rate", 150)
             
            # ImportError or RuntimeError exception can be thrown
            except Exception as e:
                # disable txt2speech
                print e.msg, e.args
                self.speech = False
            
            
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")
            
    # Private message (query) callback
    def on_privmsg(self, c, e):
        if not self.led_green.on:
            self.led_green.turn_on()
        # txt2speech
        if self.speech:
            self.txt2speech(e.arguments)
            
    # Channel message callback
    def on_pubmsg(self, c, e):
        nick = e.source.split("!")[0]
        
        # enforce our nick ignore
        if not self.led_yellow.on and nick != self.nick_ignore:
            self.led_yellow.turn_on()
            
        # txt2speech
        if self.speech:
            self.txt2speech(e.arguments)

    # on IRC server connect callback
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
            
    # process txt2speech
    def txt2speech(self, text):
        # TODO: probably need better checking here
        # TODO: strip out some bullshit characters and character codes?
        # TODO: learn more about proper handling of differently encoded chars
        # TODO: find out why pyttsx crashes on certain utf-8 characters
        try:
            parsed_text = text[0].encode("ascii", errors="ignore")

            self.engine.say(parsed_text)
            self.engine.iterate()
        except Exception as e:
            print e.message, e.args
            
    # handle when a txt2speech "say" command complete
    def on_speech_end(self, name, completed):
        # since we're not using the built pyttsx loop, we need this
        self.engine.iterate()
    
    # handle text-to-speech errors    
    def on_speech_error(self, name, exception):
        print exception.msg, exception.args
while 1:
    # TODO: this is crap, we need better try/excepts
    try:
        bot = IRCNotifier("#pibot", "raspBot", "108.59.11.230", BUTTON, RED_LED, YELLOW_LED, GREEN_LED, "kptkommie", TXT2SPEECH)
        
        # set timer for button state checking
        bot.reactor.execute_every(.2, bot.check_button)
        
        # "start" the txt2speech loop
        bot.engine.startLoop(False)
        
        # start the main bot loop
        bot.start()
        
           
    finally:
        bot.disconnect("RasPi IRC Notifier 0.1")
        bot.engine.endLoop()
        GPIO.cleanup()
        bot.die()

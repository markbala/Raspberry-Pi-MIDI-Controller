#!/usr/bin/python

#MIT License

#Copyright (c) 2020 Mark Balakrishnan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

##############################################################################
#### Mark Balakrishnan's MIDI Footswitch Controller      #####################
#### Created : June 2020                                 #####################
#### mark@bala.sg                                        #####################
##############################################################################

# Add file to rc.local to auto start on boot
# Insert "sudo python '/home/pi/<directory path>/<filename>" above "exit 0"
# Use pip / apt-get to install the brilliant "mido" library by Ole Martin Bjorndalen

###### General setup and initialisation ######################################
import mido, time, sys, RPi.GPIO as GPIO
from tendo import singleton

me = singleton.SingleInstance() # Ensures a single instance is running only

# Maps LED and Footswitch to respective GPIO pins
# (Refer to Pi pinout and fill in respective GPIO BCM numbers)
bot_left_led = 6
bot_right_led = 19
top_left_led = 26
top_right_led = 21

list_of_leds = [top_left_led, top_right_led, bot_right_led, bot_left_led]

bot_left_switch = 5
bot_right_switch = 13
top_left_switch = 20
top_right_switch = 16

# Adopts GPIO numbering instead of board numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Sets LEDs as GPIO outputs and switches as inputs
GPIO.setup(bot_left_led,GPIO.OUT)
GPIO.setup(bot_right_led,GPIO.OUT)
GPIO.setup(top_left_led,GPIO.OUT)
GPIO.setup(top_right_led,GPIO.OUT)
GPIO.setup(bot_left_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bot_right_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(top_left_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(top_right_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
##############################################################################

###### Define LED on/off or blink patterns ###################################
# Blink all LEDs where arg is number of blinks
def blink_all(no_of_blinks):
    for i in range(0,no_of_blinks):
        GPIO.output(top_left_led,GPIO.HIGH)
        GPIO.output(top_right_led,GPIO.HIGH)
        GPIO.output(bot_left_led,GPIO.HIGH)
        GPIO.output(bot_right_led,GPIO.HIGH)
        time.sleep (0.2)
        GPIO.output(top_left_led,GPIO.LOW)
        GPIO.output(top_right_led,GPIO.LOW)
        GPIO.output(bot_left_led,GPIO.LOW)
        GPIO.output(bot_right_led,GPIO.LOW)
        time.sleep(0.2)

# Blink specific LED, args to select LED and number of blinks
def blink_led(led_name,no_of_blinks):
    for i in range(0,no_of_blinks):
        GPIO.output(led_name, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(led_name, GPIO.LOW)
        time.sleep(0.2)

# LED on, arg to select LED
def led_on(led_name):
    GPIO.output(led_name, GPIO.HIGH)
#    ledstate(led_name) = True

#LED off, arg to select LED
def led_off(led_name):
    GPIO.output(led_name, GPIO.LOW)

# Pairing sequence, LEDs enter an on-off rotation
def pairing_sequence():
    for i in range(0,4):
        for i in list_of_leds:
            blink_led(i,1)

# Error sequence, right side LEDs flash continuously
def error_sequence():
    blink_led(bot_right_led,1)
    blink_led(top_right_led,1)

# Toggle LED status, arg to select LED
def led_toggle(led_name):
    print("cc message sent")
    led_state = GPIO.input(led_name)
    if led_state == GPIO.LOW:
        led_on(led_name)
    else:
        led_off(led_name)
##############################################################################

###### Main ##################################################################
def main():
    # Bottom left LED glows for 3 secs to signal start of script
    led_on(bot_left_led)
    time.sleep(3)
    led_off(bot_left_led)
    time.sleep(1)

    # Pairing sequence
    while True:
        discovered_devices = None
        discovered_devices = mido.get_output_names()
        discovered_devices = [x.encode("utf-8") for x in discovered_devices]
        discovered_devices = [x.split(":",1)[1] for x in discovered_devices]
        discovered_devices = [x.rsplit(" ", 1)[0] for x in discovered_devices]

        # USB MIDI is always detected as the first device
        # Program starts when a second (presumably your) MIDI device is detected
        # Defaults to the second MIDI device in the list for operation
        # if using USB MIDI, change to "> 0" and  "discovered_devices[0]" below
        print(discovered_devices)
        if len(discovered_devices) > 1:
              port = mido.open_output(discovered_devices[1])
              print("Success! Connected to ", port)
              blink_all(5)
              break
        else:
              print("not in list")
              pairing_sequence()

    # Operating sequence
    while True:
        if GPIO.input(top_left_switch) == GPIO.LOW:
            print("Top left button pressed!")
            port.send(mido.Message("control_change", control=6, value=127))
            led_toggle(top_left_led)
            time.sleep(0.3)
        elif GPIO.input(top_right_switch) == GPIO.LOW:
            print("Top right button pressed!")
            port.send(mido.Message("control_change", control=7, value=127))
            led_toggle(top_right_led)
            time.sleep(0.3)
        elif GPIO.input(bot_left_switch) == GPIO.LOW:
            print("Bot left button pressed!")
            port.send(mido.Message("control_change", control=8, value=127))
            led_toggle(bot_left_led)
            time.sleep(0.3)
        elif GPIO.input(bot_right_switch) == GPIO.LOW:
            print("Bot right button pressed!")
            port.send(mido.Message("control_change", control=9, value=127))
            led_toggle(bot_right_led)
            time.sleep(0.3)
##############################################################################

##############################################################################
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        for i in range(0,5):
             error_sequence()
        GPIO.cleanup()
        print("No devices were connected. Script exiting and restarting.")
        print("GPIO clean up complete. Exiting...")
        sys.exit(1)
##############################################################################

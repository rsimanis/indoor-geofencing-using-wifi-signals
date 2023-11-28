import os
import json
import time
import machine
import neopixel

def get_config():
    with open('env.json', 'r') as file:
        config_json = file.read()
    config = json.loads(config_json)
    assert_config_valid(config)
    return config

def assert_config_valid(config):
    assert 'mode' in config and config['mode'] in ['active', 'passive']
    assert 'collecting_inside_data' in config and config['collecting_inside_data'] in [True, False]

def does_dir_exist(filename):
    try:
        return (os.stat(filename)[0] & 0x4000) != 0
    except OSError:
        return False
        
def does_file_exist(filename):
    try:
        return (os.stat(filename)[0] & 0x4000) == 0
    except OSError:
        return False
    
def is_button_pressed(debounce_delay=0.1):
    button = get_button()
    if button.value() == 0:
        time.sleep(debounce_delay)
        if button.value() == 0:
            return True
    return False

def get_button():
    return machine.Pin(41, machine.Pin.IN, machine.Pin.PULL_UP)

def get_led_strip():
    return neopixel.NeoPixel(machine.Pin(35), 1)

def set_led_color(r, g, b):
    strip = get_led_strip()
    strip[0] = (r, g, b)
    strip.write()

    

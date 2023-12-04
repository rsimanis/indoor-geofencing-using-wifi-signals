import os
import json
import time
import machine
import neopixel
import network
import binascii

_config = None
nic = network.WLAN(network.STA_IF)
nic.active(True)

def get_config():
    global _config
    if _config is None:
        with open('env.json', 'r') as file:
            config_json = file.read()
        config = json.loads(config_json)
        assert_config_valid(config)
        _config = config
    assert _config is not None
    return _config

def assert_config_valid(config):
    assert 'mode' in config and config['mode'] in ['active', 'passive']
    assert 'collecting_inside_data' in config and config['collecting_inside_data'] in [True, False]
    
def is_button_pressed(debounce_delay=0.05):
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
    
def set_led_color_by_state(state):
    if state == 'active':
        set_led_color(0, 255, 0)
    elif state == 'inactive':
        set_led_color(255, 0, 0)
        
def get_sta_nic():
    return network.WLAN(network.STA_IF)

def get_ap_nic():
    return network.WLAN(network.AP_IF)
        
def scan_networks():
    nic = get_sta_nic()
    nic.active(True)
    networks = list(map(lambda network: {
        'ssid': network[0].decode('ascii'),
        'bssid': binascii.hexlify(network[1]).decode('ascii'),
        'rssi': network[3],
    }, nic.scan()))
    nic.active(False)
    return networks

    

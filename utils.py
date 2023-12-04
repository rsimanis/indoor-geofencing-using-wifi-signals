import os
import json
import time
import machine
import neopixel
import network
import binascii

NETWORKS_FILENAME = 'networks.csv'
CONFIG_FILENAME = 'config.json'

_config = None
nic = network.WLAN(network.STA_IF)
nic.active(True)

def get_config():
    global _config
    if _config is None:
        with open(CONFIG_FILENAME, 'r') as file:
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
        
def does_file_exist(filename):
    return filename in os.listdir()

def parse_csv_file(filename):
    with open(filename, 'r') as file:
        file_content = file.read()
    lines = file_content.split('\n')
    assert len(lines) >= 2
    lines.pop() # remove empty line at the end
    header_line = lines.pop(0)
    headers = header_line.split(',')
    parsed_file = []
    for line in lines:
        fields = line.split(',')
        assert(len(fields) == len(headers))
        parsed_line = {}
        for i in range(0, len(fields)):
            parsed_line[headers[i]] = fields[i]
        parsed_file.append(parsed_line)
    return parsed_file

def get_saved_networks():
    return list(map(lambda network: {
        'id': int(network['id']),
        'inside': network['inside'] == 'True',
        'ssid': network['ssid'],
        'bssid': network['bssid'],
        'rssi': int(network['rssi']),
    }, parse_csv_file(NETWORKS_FILENAME)))

def get_saved_inside_networks():
    return list(filter(lambda network: network['inside'], get_saved_networks()))

def get_saved_outside_networks():
    return list(filter(lambda network: not network['inside'], get_saved_networks()))

def create_networks_file():
    with open(NETWORKS_FILENAME, 'w') as file:
        file.write('id,inside,ssid,bssid,rssi\n')

def save_networks(networks):
    if does_file_exist(NETWORKS_FILENAME):
        saved_networks = get_saved_networks()
        if len(saved_networks) == 0:
            id = 1
        else:
            id = saved_networks[-1]['id'] + 1
    else:
        create_networks_file()
        id = 1
    assert does_file_exist(NETWORKS_FILENAME)
    config = get_config()
    with open(NETWORKS_FILENAME, 'a') as file:
        for network in networks:
            network['ssid'] = network['ssid'].replace(',', '')
            file.write(f'{id},{config["collecting_inside_data"]},{network["ssid"]},{network["bssid"]},{network["rssi"]}\n')
            
    
    

    

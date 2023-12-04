import os
import json
import time
import machine
import neopixel
import network
import binascii
import math

NETWORKS_FILENAME = 'networks.csv'
CONFIG_FILENAME = 'config.json'

_config = None
_id = None

def get_config():
    global _config
    if _config is None:
        config = parse_config()
        validate_config(config)
        _config = config
    assert _config is not None
    return _config

def parse_config():
    with open(CONFIG_FILENAME, 'r') as file:
        config_json = file.read()
    config = json.loads(config_json)
    return config

def validate_config(config):
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
    
def set_led_color_for_passive_mode(state):
    if state == 'active':
        set_led_color(0, 255, 0)
    elif state == 'inactive':
        set_led_color(255, 0, 0)
        
def set_led_color_for_active_mode(state, is_inside = None, is_outside = None):
    if state == 'active':
        assert is_inside is not None and is_outside is not None
        if is_inside and not is_outside:
            set_led_color(0, 255, 0)
        elif not is_inside and is_outside:
            set_led_color(255, 0, 0)
        else:
            set_led_color(0, 0, 255)
    elif state == 'inactive':
        set_led_color(255, 255, 255)
          
def get_sta_nic():
    return network.WLAN(network.STA_IF)

def get_ap_nic():
    return network.WLAN(network.AP_IF)
        
def scan_networks():
    print('Scanning networks...')
    nic = get_sta_nic()
    nic.active(True)
    networks = list(map(lambda network: {
        'ssid': network[0].decode('ascii'),
        'bssid': binascii.hexlify(network[1]).decode('ascii'),
        'rssi': network[3],
    }, nic.scan()))
    nic.active(False)
    print('Scanned networks')
    return networks
        
def does_file_exist(filename):
    return filename in os.listdir()

def parse_csv_file(filename):
    print(f'Parsing CSV file [{filename}]...')
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
    print(f'Parsed CSV file [{filename}]')
    return parsed_file

def get_saved_networks():
    print('Getting saved networks...')
    saved_networks = list(map(lambda network: {
        'id': int(network['id']),
        'inside': network['inside'] == 'True',
        'ssid': network['ssid'],
        'bssid': network['bssid'],
        'rssi': int(network['rssi']),
    }, parse_csv_file(NETWORKS_FILENAME)))
    print('Got saved networks')
    return saved_networks

def get_saved_inside_networks():
    print('Getting saved inside networks...')
    saved_inside_networks = list(filter(lambda network: network['inside'], get_saved_networks()))
    print('Got saved inside networks')
    return saved_inside_networks

def get_saved_outside_networks():
    print('Getting saved outside networks...')
    saved_outside_networks = list(filter(lambda network: not network['inside'], get_saved_networks()))
    print('Got saved outside networks')
    return saved_outside_networks

def create_networks_file():
    print('Creating networks file...')
    with open(NETWORKS_FILENAME, 'w') as file:
        file.write('id,inside,ssid,bssid,rssi\n')
    print('Created networks file')

def save_networks(networks):
    print('Saving networks...')
    global _id
    if does_file_exist(NETWORKS_FILENAME):
        if _id is None:
            saved_networks = get_saved_networks()
            if len(saved_networks) == 0:
                id = 1
            else:
                id = saved_networks[-1]['id'] + 1
        else:
            id = _id
    else:
        create_networks_file()
        id = 1
    config = get_config()
    with open(NETWORKS_FILENAME, 'a') as file:
        for network in networks:
            network['ssid'] = network['ssid'].replace(',', '')
            file.write(f'{id},{config["collecting_inside_data"]},{network["ssid"]},{network["bssid"]},{network["rssi"]}\n')
    _id = id + 1
    print('Saved networks')
    
def do_networks_match_using_naive_algorithm(current_networks, saved_networks_by_id):
    print('Matching networks using naive algorithm...')
    config = get_config()
    required_network_matches = config['algorithms']['naive']['required_network_matches']
    rssi_match_epsilon = config['algorithms']['naive']['rssi_match_epsilon']
    for saved_networks in saved_networks_by_id.values():
        network_matches = 0
        for saved_network in saved_networks:
            for current_network in current_networks:
                if current_network['bssid'] == saved_network['bssid'] and math.fabs(current_network['rssi'] - saved_network['rssi']) <= rssi_match_epsilon:
                    network_matches += 1
        if network_matches >= required_network_matches:
            print('Matched networks using naive algorithm [True]')
            return True
    print('Matched networks using naive algorithm [False]')
    return False
            
def partition_networks_by_id(networks):
    res = {}
    for network in networks:
        id = network['id']
        if id in res:
            res[id].append(network)
        else:
            res[id] = [network]
    return res

def get_saved_inside_networks_by_id():
    return partition_networks_by_id(get_saved_inside_networks())

def get_saved_outside_networks_by_id():
    return partition_networks_by_id(get_saved_outside_networks())
    
    

    

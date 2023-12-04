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
_saved_networks = None

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
        if is_inside is None and is_outside is None:
            set_led_color(0, 0, 0)
        elif is_inside and not is_outside:
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
    networks = list(map(lambda network: [
        binascii.hexlify(network[1]).decode('ascii'), # bssid
        network[3], # rssi
    ], nic.scan()))
    nic.active(False)
    print('Scanned networks')
    return networks

def get_scanned_network_bssid(network):
    return network[0]

def set_scanned_network_bssid(network, bssid):
    network[0] = bssid

def get_scanned_network_rssi(network):
    return network[1]

def set_scanned_network_rssi(network, rssi):
    network[1] = rssi

def get_saved_network_id(network):
    return network[0]

def set_saved_network_id(network, id):
    network[0] = id

def get_saved_network_inside(network):
    return network[1]

def set_saved_network_inside(network, inside):
    network[1] = inside

def get_saved_network_bssid(network):
    return network[2]

def set_saved_network_bssid(network, bssid):
    network[2] = bssid

def get_saved_network_rssi(network):
    return network[3]

def set_saved_network_rssi(network, rssi):
    network[3] = rssi
        
def does_file_exist(filename):
    return filename in os.listdir()

def parse_csv_file_as_dicts(filename):
    return parse_csv_file(filename, 'dict')

def parse_csv_file_as_lists(filename):
    return parse_csv_file(filename, 'list')

def parse_csv_file_as_tuples(filename):
    return parse_csv_file(filename, 'tuple')

def parse_csv_file(filename, line_type):
    print(f'Parsing CSV file [{filename}] as {line_type}s...')
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
        if line_type == 'list':
            parsed_line = fields
        elif line_type == 'tuple':
            parsed_line = tuple(fields)
        elif line_type == 'dict':
            parsed_line = {}
            for i in range(0, len(fields)):
                parsed_line[headers[i]] = fields[i]
        else:
            assert(False, 'Invalid line type')
        parsed_file.append(parsed_line)
    print(f'Parsed CSV file [{filename}] as {line_type}s')
    return parsed_file

def get_saved_inside_networks_by_id(cache = False):
    return partition_saved_networks_by_id(get_saved_inside_networks(cache))

def get_saved_outside_networks_by_id(cache = False):
    return partition_saved_networks_by_id(get_saved_outside_networks(cache))

def get_saved_inside_networks(cache = False):
    print('Getting saved inside networks...')
    saved_inside_networks = list(filter(lambda network: get_saved_network_inside(network), get_saved_networks(cache)))
    print('Got saved inside networks')
    return saved_inside_networks

def get_saved_outside_networks(cache = False):
    print('Getting saved outside networks...')
    saved_outside_networks = list(filter(lambda network: not get_saved_network_inside(network), get_saved_networks(cache)))
    print('Got saved outside networks')
    return saved_outside_networks

def get_saved_networks(cache = False):
    print('Getting saved networks...')
    global _saved_networks
    if cache and _saved_networks is not None:
        print('Got saved networks')
        return _saved_networks
    saved_networks = list(map(lambda network: [
        int(get_saved_network_id(network)),
        get_saved_network_inside(network) == 'True',
        get_saved_network_bssid(network),
        int(get_saved_network_rssi(network)),
    ], parse_csv_file_as_lists(NETWORKS_FILENAME)))
    if cache:
        _saved_networks = saved_networks
    print('Got saved networks')
    return saved_networks

def partition_saved_networks_by_id(networks):
    res = {}
    for network in networks:
        id = get_saved_network_id(network)
        if id in res:
            res[id].append(network)
        else:
            res[id] = [network]
    return res

def create_networks_file():
    print('Creating networks file...')
    with open(NETWORKS_FILENAME, 'w') as file:
        file.write('id,inside,bssid,rssi\n')
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
                id = get_saved_network_id(saved_networks[-1]) + 1
        else:
            id = _id
    else:
        create_networks_file()
        id = 1
    config = get_config()
    with open(NETWORKS_FILENAME, 'a') as file:
        for network in networks:
            inside = config["collecting_inside_data"]
            bssid = get_scanned_network_bssid(network)
            rssi = get_scanned_network_rssi(network)
            file.write(f'{id},{inside},{bssid},{rssi}\n')
    _id = id + 1
    print(f'Saved networks (id = {id})')
    
def get_network_matching_data_using_naive_algorithm(current_networks, saved_networks_by_id, inside):
    matched = False
    adjective = 'inside' if inside else 'outside'
    print(f'Matching {adjective} networks using naive algorithm...')
    config = get_config()
    required_network_matches = config['algorithms']['naive']['required_network_matches']
    rssi_match_epsilon = config['algorithms']['naive']['rssi_match_epsilon']
    total_matches = 0
    for saved_networks in saved_networks_by_id.values():
        network_matches = 0
        for saved_network in saved_networks:
            for current_network in current_networks:
                if get_scanned_network_bssid(current_network) == get_saved_network_bssid(saved_network) and math.fabs(get_scanned_network_rssi(current_network) - get_saved_network_rssi(saved_network)) <= rssi_match_epsilon:
                    network_matches += 1
        if network_matches >= required_network_matches:
            total_matches += 1
            matched = True
    print(f'Matched {adjective} networks using naive algorithm [matched={matched}, total_matches={total_matches}]')
    return {
        "matched": matched,
        "total_matches": total_matches,
    }
    
    

    

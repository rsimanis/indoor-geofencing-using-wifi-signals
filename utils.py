import os
import json
import time
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
        prepare_config(config)
        _config = config
    assert _config is not None
    return _config

def parse_config():
    with open(CONFIG_FILENAME, 'r') as file:
        config_json = file.read()
    config = json.loads(config_json)
    return config

def prepare_config(config):
    if 'results_filename_suffix' not in config:
        config['results_filename_suffix'] = None
        
    if '_id' not in config:
        config['_id'] = None

    if 'log' not in config:
        config['log'] = True
    
def is_button_pressed(debounce_delay=0.05):
    button = get_button()
    if button.value() == 0:
        time.sleep(debounce_delay)
        if button.value() == 0:
            return True
    return False

def get_button():
    import machine
    return machine.Pin(41, machine.Pin.IN, machine.Pin.PULL_UP)

def get_led_strip():
    import machine
    import neopixel
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

def set_led_color_for_test_mode(state):
    if state == 'active':
        set_led_color(0, 255, 0)
    elif state == 'inactive':
        set_led_color(255, 0, 0)

def set_led_color_by_mode_and_state(mode, state):
    if mode == 'passive':
        set_led_color_for_passive_mode(state)
    elif mode == 'active':
        set_led_color_for_active_mode(state)
    elif mode == 'test':
        set_led_color_for_test_mode(state)
        
def scan_networks():
    log('Scanning networks...')
    import network
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    networks = list_map(nic.scan(), lambda network: [
        binascii.hexlify(network[1]).decode('ascii'), # bssid
        network[3], # rssi
    ])
    nic.active(False)
    return networks

def convert_saved_to_scanned_network(saved_network):
    scanned_network = [None, None]
    set_scanned_network_bssid(scanned_network, get_saved_network_bssid(saved_network))
    set_scanned_network_rssi(scanned_network, get_saved_network_rssi(saved_network))
    return scanned_network

def get_scanned_network_bssid(network):
    return network[get_scanned_network_bssid_index()]

def set_scanned_network_bssid(network, bssid):
    network[get_scanned_network_bssid_index()] = bssid

def get_scanned_network_rssi(network):
    return network[get_scanned_network_rssi_index()]

def set_scanned_network_rssi(network, rssi):
    network[get_scanned_network_rssi_index()] = rssi

def get_scanned_network_bssid_index():
    return 0

def get_scanned_network_rssi_index():
    return 1

def get_saved_network_id(network):
    return network[get_saved_network_id_index()]

def set_saved_network_id(network, id):
    network[get_saved_network_id_index()] = id

def get_saved_network_inside(network):
    return network[get_saved_network_inside_index()]

def set_saved_network_inside(network, inside):
    network[get_saved_network_inside_index()] = inside

def get_saved_network_quadrant(network):
    return network[get_saved_network_quadrant_index()]

def set_saved_network_quadrant(network, quadrant):
    network[get_saved_network_quadrant_index()] = quadrant

def get_saved_network_bssid(network):
    return network[get_saved_network_bssid_index()]

def set_saved_network_bssid(network, bssid):
    network[get_saved_network_bssid_index()] = bssid

def get_saved_network_rssi(network):
    return network[get_saved_network_rssi_index()]

def set_saved_network_rssi(network, rssi):
    network[get_saved_network_rssi_index()] = rssi

def get_saved_network_id_index():
    return 0

def get_saved_network_inside_index():
    return 1

def get_saved_network_quadrant_index():
    return 2

def get_saved_network_bssid_index():
    return 3

def get_saved_network_rssi_index():
    return 4
        
def does_file_exist(filename):
    return filename in os.listdir()

def parse_csv_file_as_dicts(filename):
    return parse_csv_file(filename, 'dict')

def parse_csv_file_as_lists(filename):
    return parse_csv_file(filename, 'list')

def parse_csv_file_as_tuples(filename):
    return parse_csv_file(filename, 'tuple')

def parse_csv_file(filename, line_type):
    log(f'Parsing CSV file [{filename}] as {line_type}s...')
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
        assert len(fields) == len(headers)
        if line_type == 'list':
            parsed_line = fields
        elif line_type == 'tuple':
            parsed_line = tuple(fields)
        elif line_type == 'dict':
            parsed_line = {}
            for i in range(0, len(fields)):
                parsed_line[headers[i]] = fields[i]
        else:
            assert False, 'Invalid line type'
        parsed_file.append(parsed_line)
    return parsed_file

def get_saved_networks(filename):
    log('Getting saved networks...')
    networks = list_map(parse_csv_file_as_lists(filename), lambda network: [
        int(get_saved_network_id(network)),
        get_saved_network_inside(network) == 'True',
        int(get_saved_network_quadrant(network)),
        get_saved_network_bssid(network),
        int(get_saved_network_rssi(network)),
    ])
    return networks

def save_networks(networks):
    log('Saving networks...')
    global _id
    if does_file_exist(NETWORKS_FILENAME):
        if _id is None:
            saved_networks = get_saved_networks(NETWORKS_FILENAME)
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
            inside = config["collecting_inside"]
            quadrant = config["collecting_quadrant"]
            bssid = get_scanned_network_bssid(network)
            rssi = get_scanned_network_rssi(network)
            file.write(f'{id},{inside},{quadrant},{bssid},{rssi}\n')
    _id = id + 1
    log(f'Saved networks (id = {id})')

def create_networks_file():
    log('Creating networks file...')
    with open(NETWORKS_FILENAME, 'w') as file:
        file.write('id,inside,quadrant,bssid,rssi\n')

def save_test_data(is_inside, is_outside):
    log('Saving test data...')
    if not does_file_exist(get_results_filename()):
        create_results_file()
    config = get_config()
    expected_is_inside = config['testing_inside']
    with open(get_results_filename(), 'a') as file:
        file.write(f'{is_inside},{is_outside},{expected_is_inside}\n')

def create_results_file():
    log('Creating results file...')
    with open(get_results_filename(), 'w') as file:
        file.write('is_inside,is_outside,expected_is_inside\n')

def get_results_filename():
    config = get_config()
    suffix = config['results_filename_suffix']
    filename = 'results'
    if suffix is not None:
        filename += f'-{suffix}'
    filename += '.csv'
    return filename

def match_using_naive_algorithm(current_networks, saved_networks, config = {}):
    if 'required_network_matches' not in config:
        config['required_network_matches'] = get_config()['algorithms']['naive']['required_network_matches']
    if 'rssi_match_epsilon' not in config:
        config['rssi_match_epsilon'] = get_config()['algorithms']['naive']['rssi_match_epsilon']

    required_network_matches = config['required_network_matches']
    rssi_match_epsilon = config['rssi_match_epsilon']

    inside_network_matches_by_id = {}
    outside_network_matches_by_id = {}

    for saved_network in saved_networks:
        matching_current_network = list_find(current_networks, lambda current_network: get_scanned_network_bssid(current_network) == get_saved_network_bssid(saved_network) and math.fabs(get_scanned_network_rssi(current_network) - get_saved_network_rssi(saved_network)) <= rssi_match_epsilon)
        if matching_current_network is None:
            continue
        network_matches_by_id = inside_network_matches_by_id if get_saved_network_inside(saved_network) else outside_network_matches_by_id
        if get_saved_network_id(saved_network) in network_matches_by_id:
            network_matches_by_id[get_saved_network_id(saved_network)] += 1
        else:
            network_matches_by_id[get_saved_network_id(saved_network)] = 1

    def count_total_matches(network_matches_by_id):
        total_matches = 0
        for network_matches in network_matches_by_id.values():
            if network_matches >= required_network_matches:
                total_matches += 1
        return total_matches
    
    inside_total_matches = count_total_matches(inside_network_matches_by_id)
    outside_total_matches = count_total_matches(outside_network_matches_by_id)
    log(f'''Matched networks using NAIVE algorithm [inside_total_matches = {inside_total_matches}, outside_total_matches = {outside_total_matches}]''')

    is_inside = is_outside = False
    if inside_total_matches > outside_total_matches:
        is_inside = True
    elif inside_total_matches < outside_total_matches:
        is_outside = True
    
    return [is_inside, is_outside]
    
def list_filter(lst, callback):
    return list(filter(callback, lst))

def list_map(lst, callback):
    return list(map(callback, lst))

def list_find(lst, callback, default=None):
    try:
        return next(filter(callback, lst))
    except StopIteration:
        return default

def match_using_active_algorithm(current_networks, saved_networks):
    active_algorithm = get_config()['active_algorithm']
    return match_using_algorithm(active_algorithm, current_networks, saved_networks)

def match_using_algorithm(algorithm, current_networks, saved_networks):
    if algorithm == 'naive':
        return match_using_naive_algorithm(current_networks, saved_networks)
    else:
        assert False, f'Invalid algorithm [{algorithm}]'

def display_collecting_countdown():
    log('Scanning networks in 3...')
    time.sleep(2)
    log('2...')
    time.sleep(2)
    log('1...')
    time.sleep(2)

def log(message):
    if get_config()['log']:
        print(message)

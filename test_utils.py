import utils
from glob import glob
import os

def get_train_dir():
    return get_path('/train')

def get_test_dir():
    return get_path('/test')

def get_path(path = None):
    res = os.path.dirname(os.path.realpath(__file__))
    if path is not None:
        res += path
    return res

def get_train_networks():
    train_networks = []
    for filepath in glob(f'{get_train_dir()}/*'):
        networks = utils.get_saved_networks(filepath)
        train_networks.extend(networks)
    return train_networks

def get_test_data():
    test_data = {}
    for filepath in glob(f'{get_test_dir()}/*'):
        print(filepath)
        basename = os.path.basename(filepath)
        parsed = parse_networks_basename(basename)
        date = parsed['date']
        networks = utils.get_saved_networks(filepath)
        chunks = {}
        for network in networks:
            id = utils.get_saved_network_id(network)
            if id not in chunks:
                chunks[id] = []
            chunks[id].append(network)
        test_data[date] = chunks
    return test_data

def parse_networks_basename(basename):
    filename = basename.split('.')[0]
    parts = filename.split('_')
    return {
        'basename': basename,
        'filename': filename,
        'date': parts[1],
        'index': int(parts[2]),
    }

def test_algorithm(match):
    train_networks = get_train_networks()
    test_data = get_test_data()
    results = {
        "span": {},
    }
    accuracy_total = 0
    for date, chunks in test_data.items():
        correct = 0
        for test_networks in chunks.values():
            expected_inside = utils.get_saved_network_inside(test_networks[0])
            current_networks = utils.list_map(test_networks, lambda network: utils.convert_saved_to_scanned_network(network))
            [inside, outside] = match(current_networks, train_networks)
            if (inside and not outside and expected_inside) or (outside and not inside and not expected_inside):
                correct += 1
        accuracy = round(correct / len(chunks) * 100, 2)
        accuracy_total += accuracy
        results['span'][date] = accuracy
    results['average'] = round(accuracy_total / len(test_data), 2)
    return results

def match_using_naive_algorithm(current_networks, train_networks):
    config = {
        'required_network_matches': 3,
        'rssi_match_epsilon': 3,
    }
    return utils.match_using_naive_algorithm(current_networks, train_networks, config)

def test_naive_algorithm():
    return test_algorithm(match_using_naive_algorithm)
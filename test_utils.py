import utils
from glob import glob
import os
import math
from pprint import pprint

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
        basename = os.path.basename(filepath)
        parsed = parse_networks_basename(basename)
        date = parsed['date']
        networks = utils.get_saved_networks(filepath)
        chunks = utils.partition_saved_networks_by_id(networks)
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

def test_algorithm(match, match_args = {}):
    train_networks = get_train_networks()
    test_data = get_test_data()
    results = {
        "dates": {},
    }
    accuracy_total = 0
    for date, chunks in test_data.items():
        correct = 0
        for test_networks in chunks.values():
            expected_inside = utils.get_saved_network_inside(test_networks[0])
            current_networks = utils.list_map(test_networks, lambda network: utils.convert_saved_to_scanned_network(network))
            [inside, outside] = match(current_networks, train_networks, match_args)
            if (inside and not outside and expected_inside) or (outside and not inside and not expected_inside):
                correct += 1
        accuracy = round(correct / len(chunks) * 100, 2)
        accuracy_total += accuracy
        results['dates'][date] = accuracy
    results['average'] = round(accuracy_total / len(test_data), 2)
    return results

def match_using_naive_algorithm(current_networks, train_networks, args):
    return utils.match_using_naive_algorithm(current_networks, train_networks, args)

def test_naive_algorithm(required_network_matches, rssi_match_epsilon):
    match_args = {
        'required_network_matches': required_network_matches,
        'rssi_match_epsilon': rssi_match_epsilon,
    }
    return test_algorithm(match_using_naive_algorithm, match_args)

def match_using_knn_algorithm(current_networks, train_networks, args):
    return utils.match_using_knn_algorithm(current_networks, train_networks, args)

def test_knn_algorithm(k, dist_algo):
    match_args = {
        'k': k,
        'dist_algo': dist_algo,
    }
    return test_algorithm(match_using_knn_algorithm, match_args)

def find_best_params_for_naive_algorithm(
    required_network_matches_start = 1, 
    required_network_matches_end = 10, 
    required_network_matches_step = 1, 
    rssi_match_epsilon_start = 0, 
    rssi_match_epsilon_end = 10, 
    rssi_match_epsilon_step = 0.5,
):
    options = []
    required_network_matches = required_network_matches_start
    while required_network_matches <= required_network_matches_end:
        rssi_match_epsilon = rssi_match_epsilon_start
        while rssi_match_epsilon < rssi_match_epsilon_end or math.isclose(rssi_match_epsilon, rssi_match_epsilon_end):
            results = test_naive_algorithm(required_network_matches, rssi_match_epsilon)
            option = {
                'required_network_matches': required_network_matches,
                'rssi_match_epsilon': rssi_match_epsilon,
                'average': results['average'],
            };
            pprint(option)
            options.append(option)
            rssi_match_epsilon += rssi_match_epsilon_step
        required_network_matches += required_network_matches_step
    options_sorted_by_average_desc = sorted(options, key=lambda option: option['average'], reverse=True)
    return options_sorted_by_average_desc[0]

def find_best_params_for_knn_algorithm(
    k_start = 1, 
    k_end = 100, 
    k_step = 2,
):
    options = []
    for dist_algo in ['euclidian', 'manhattan']:
        k = k_start
        while k <= k_end:
            results = test_knn_algorithm(k, dist_algo)
            option = {
                'dist_algo': dist_algo,
                'k': k,
                'average': results['average'],
            };
            pprint(option)
            options.append(option)
            k += k_step
    options_sorted_by_average_desc = sorted(options, key=lambda option: option['average'], reverse=True)
    return options_sorted_by_average_desc[0]

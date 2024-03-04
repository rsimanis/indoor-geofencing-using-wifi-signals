import test_utils
import utils
from pprint import pprint

pprint(test_utils.test_naive_algorithm({
    'required_network_matches': 3,
    'rssi_match_epsilon': 3,
}))
pprint(test_utils.test_knn_algorithm({
    'dist_algo': 'euclidian',
    'k': 3,
}))
pprint(test_utils.test_knn_algorithm({
    'dist_algo': 'manhattan',
    'k': 3,
}))
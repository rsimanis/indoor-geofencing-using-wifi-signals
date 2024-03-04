import test_utils
import utils
from pprint import pprint

pprint(test_utils.test_naive_algorithm())
pprint(test_utils.test_knn_algorithm('euclidian'))
pprint(test_utils.test_knn_algorithm('manhattan'))
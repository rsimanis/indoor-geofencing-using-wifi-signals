import sys
import getopt
import csv

def main(argv):
    filepath = None

    opts, args = getopt.getopt(argv, "hf:")
    for opt, arg in opts:
        if opt == '-h':
            print('analyze.py -f <file>')
            sys.exit()
        elif opt == '-f':
            filepath = arg

    if filepath is None:
        raise Exception('Must provide file with -f')
    
    inside_correct_count = 0
    inside_total_count = 0

    outside_correct_count = 0
    outside_total_count = 0
    
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            is_inside = row[0] == 'True'
            is_outside = row[1] == 'True'
            expected_is_inside = row[2] == 'True'
            if expected_is_inside:
                if is_inside and not is_outside:
                    inside_correct_count += 1
                inside_total_count += 1
            else:
                if is_outside and not is_inside:
                    outside_correct_count += 1
                outside_total_count += 1

    inside_correct_percent = 0 if inside_total_count == 0 else inside_correct_count / inside_total_count
    outside_correct_percent = 0 if outside_total_count == 0 else outside_correct_count / outside_total_count
    average_correct_percent = (inside_correct_percent + outside_correct_percent) / 2 

    print(f'Inside correct: {inside_correct_percent:.0%}')
    print(f'Outside correct: {outside_correct_percent:.0%}')
    print(f'Average correct: {average_correct_percent:.0%}')  

if __name__ == '__main__':
    main(sys.argv[1:])






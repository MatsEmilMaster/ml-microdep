# imports
import gzip

import emil_types
import utils
# End: imports -----------------------------------------------------------------

WINDOW_SIZE = 1000
H_N = 50
T_N = 50
START_GAP_THRESHOLD = 5
END_GAP_THRESHOLD = 5
MILL = 1000000


crude_fred = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/crude-00_00_01.gz'
crude_tekno = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/crude-00_00_02.gz'
crude_ngu = 'C:/Users/twide/my_projects/git/ml-microdep/secret/ngu-mp.ngu.no/2021-02-16/crude-00_00_01.gz'
crude_custom = 'C:/Users/twide/my_projects/git/ml-microdep/scripts/crude_custom.txt'

crude_analyzer = utils.CrudeAnalyzer(window_size=1000, h_limit=5, t_limit=5, start_gap_threshold=2, end_gap_threshold=5)

with gzip.open(filename=crude_ngu, mode='rt') as file:
# with open(file=crude_custom, mode='r') as file:
    # [file.readline() for i in range(4)] # discard headerlines

    for i, line in enumerate(file, 1):
        line = line.strip()
        if i % (1*MILL) == 0:
            print(f"{i}: {line}")

        # print(line)
        if i > 1*MILL:
            break

        key_values = line.split() # list of key-value pairs # ['ID=1', 'RX=15434', ...]

        try:
            record = emil_types.CrudeRecord(
                id = key_values[0].split('=')[1], # ID=1
                seq = key_values[1].split('=')[1],
                src = key_values[2].split('=')[1].split(':')[0], # SRC=ip:port
                dst = key_values[3].split('=')[1].split(':')[0], # DST=ip:port
                tx = key_values[4].split('=')[1],
                rx = key_values[5].split('=')[1],
                size = key_values[6].split('=')[1],
                hoplimit = key_values[7].split('=')[1],
            )
            crude_analyzer.add_record(record)
        except Exception as e:
            print(f"{i}: {line}, [{e}]")


# print(crude_analyzer.__str__(show_records=5))
crude_analyzer.cleanup()
print(crude_analyzer.__str__())

# print( [r.seq for r in crude_analyzer.analyzers[1].unfinished_gaps[0].head] )
# print( [r.seq for r in crude_analyzer.analyzers[1].unfinished_gaps[0].tail] )

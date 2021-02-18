# imports
import gzip

import microdep_types
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

crude_analyzer = utils.CrudeAnalyzer(window_size=1000, h_n=50, t_n=50, start_gap_threshold=2, end_gap_threshold=5)

with gzip.open(filename=crude_ngu, mode='rt') as file:
    [file.readline() for i in range(4)] # discard headerlines

    for i, line in enumerate(file):
        line = line.strip()
        if i % 1000000 == 0:
            print(f"{i}: {line}")

        # print(line)
        if i > 3*MILL:
            break

        key_values = line.split() # list of key-value pairs # ['ID=1', 'RX=15434', ...]

        try:
            record = microdep_types.CrudeRecord(
                id = key_values[0].split('=')[1], # ID=1
                seq = key_values[1].split('=')[1],
                src = key_values[2].split('=')[1].split(':')[0], # SRC=ip:port
                dst = key_values[3].split('=')[1].split(':')[0], # DST=ip:port
                tx = key_values[4].split('=')[1],
                rx = key_values[5].split('=')[1],
                size = key_values[6].split('=')[1],
                hoplimit = key_values[7].split('=')[1],
            )
        except Exception as e:
            print(f"{i}: {line}, [{e}]")

        crude_analyzer.add_record(record)

print(crude_analyzer.__str__(show_records=5))

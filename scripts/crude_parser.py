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
# traceroute = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/traceroute_128.39.19.150.gz'
# tcptraceroute = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/tcptraceroute_128.39.19.150.gz'
# vmstat = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/vmstat.gz'
tekno_crude = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/crude-00_00_02.gz'
# traceroute2 = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/traceroute_128.39.19.150.gz'
# tcptraceroute2 = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/tcptraceroute_128.39.19.150.gz'
# vmstat2 = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/vmstat.gz'
crude_ngu = 'C:/Users/twide/my_projects/git/ml-microdep/secret/ngu-mp.ngu.no/2021-02-16/crude-00_00_01.gz'

# analyzers: dict[str, utils.CrudeStreamAnalyzer] = {}

# def add_record_to_analyzer(record: microdep_types.CrudeRecord) -> None:
#     global analyzers
#     id = record.id
#     if id not in analyzers:
#         analyzers[id] = utils.CrudeStreamAnalyzer(stream_id=id, window_size=1000, h_n=50, t_n=50, start_gap_threshold=5, end_gap_threshold=5)
#     # print(f"[crude_parser3][add_record_to_analyzer] id{id}, analyzer={analyzers[id].stream_id}")
#     analyzers[id].add_record(record)

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

        # add_record_to_analyzer(record)
        # for id, a in analyzers.items():
        #     # print(f"[crude_parser3][analyzer #{id}] {len(a.window)}")
        #     pass

        crude_analyzer.add_record(record)
        # print(f"[crude_parser3] {crude_analyzer.analyzers}")

# for id, analyzer in crude_analyzer.analyzers.items():
#     print(f"[crude_parser3]{analyzer.__str__(show_records=15)}")
#     pass
print(crude_analyzer.__str__(show_records=5))

# print(f"[crude_parser3] {str(analyzers['7'].window)}")
# print(record.__dict__)


# print( crude_analyzer.analyzers['1'].window[-15:])
# print( crude_analyzer.analyzers['7'].window[-15:])

# for id, analyzer in analyzers.items():
#     print(f"[crude_parser3] {id}: {analyzer}")

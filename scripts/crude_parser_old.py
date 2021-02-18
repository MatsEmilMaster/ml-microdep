# imports
import gzip

import microdep_types
import utils
# End: imports -----------------------------------------------------------------


crude_fred = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/crude-00_00_01.gz'
# traceroute = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/traceroute_128.39.19.150.gz'
# tcptraceroute = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/tcptraceroute_128.39.19.150.gz'
# vmstat = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/vmstat.gz'
tekno_crude = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/crude-00_00_02.gz'
# traceroute2 = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/traceroute_128.39.19.150.gz'
# tcptraceroute2 = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/tcptraceroute_128.39.19.150.gz'
# vmstat2 = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/vmstat.gz'

ca = utils.CrudeAnalyzer2(window_size=5)

with gzip.open(filename=crude_fred, mode='rt') as file:
    [file.readline() for i in range(4)] # discard headerlines

    for i, line in enumerate(file):
        line = line.strip()

        if i % 1000000 == 0:
            print(f"{i}: {line}")

        print(line)
        if i > 20:
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
            ca.add_record(record)
            # print(record.__dict__)

        except Exception as e:
            print(f"{i}: {line.strip()}, [{e}]")

print(ca)
print(ca.stats)

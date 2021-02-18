import gzip
# import sys; sys.path.append('')
import sys
import os

import microdep_types as types


crude_fred = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/crude-00_00_01.gz'
traceroute_fred = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/traceroute_128.39.19.150.gz'
tcptraceroute_fred = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/tcptraceroute_128.39.19.150.gz'
vmstat_fred = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/vmstat.gz'

crude_tek = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/crude-00_00_01.gz'
traceroute_tek = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/traceroute_128.39.19.150.gz'
tcptraceroute_tek = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/tcptraceroute_128.39.19.150.gz'
vmstat_tek = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/vmstat.gz'

crude_ngu = 'C:/Users/twide/my_projects/git/ml-microdep/secret/ngu-mp.ngu.no/2021-02-16/crude-00_00_01.gz'


with gzip.open(filename=crude_ngu, mode='rt') as file:

    for i, line in enumerate(file):
        line = line.strip()
        key_values = line.split() # list of key-value pairs # ['ID=1', 'RX=15434', ...]
        # if i > 8624984:
        #     print(line)

        print(f"{i}: {line}")
        if i > 50:
            break

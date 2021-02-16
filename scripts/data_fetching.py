import gzip
# import sys; sys.path.append('')
import sys
import os

import microdep_types as types

# from ../scripts import data_fetching

# url = "https://stat.ripe.net/data/network-info/data.json?resource=" + ip + "&sourceapp=uninett"
# response = urllib.request.urlopen(url)
# data = json.loads(response.read().decode('utf-8'))
#
# url = "https://stat.ripe.net/data/bgp-updates/data.json?resource=" \
#       + all_prefixes + "&endtime=" + stoptime + "&starttime=" + starttime + "&unix_timestamps=true&sourceapp=uninett"
# response = urllib.request.urlopen(url)
# data = json.loads(response.read().decode('utf-8'))

crude = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/crude-00_00_01.gz'
traceroute = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/traceroute_128.39.19.150.gz'
tcptraceroute = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/tcptraceroute_128.39.19.150.gz'
vmstat = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/vmstat.gz'


if __name__ == "__main__":

    headerlines = 4 # how many lines in the file is header
    ca = types.CrudeAnalyzer(window_size=1000)

    with gzip.open(filename=crude, mode='rt') as file:
        [file.readline() for i in range(headerlines)] # discard headerlines

        i = 0
        for line in file:
            i += 1
            key_values = line.split() # list of key-value pairs # ['ID=1', 'RX=15434', ...]
            # if i > 8624984:
            #     print(line)

            # print(line)
            if i > 50:
                break

            try:
                record = types.CrudeRecord(
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
                print(e)
                print(i)
                print(line)

    print(ca)
    # print(ca.get_all_attr_names())
    print(ca.__dict__)

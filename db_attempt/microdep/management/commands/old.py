# imports
import gzip

from django.utils import timezone
from django.core import management
from django.core.management.base import BaseCommand

from microdep import models as microdep_models
# End: imports -----------------------------------------------------------------

# Settings:


class Command(BaseCommand):

    def handle(self, *args, **options):
        print(f"\n== COMMAND: {__file__} ==")


        crude = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/crude-00_00_01.gz'
        traceroute = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/traceroute_128.39.19.150.gz'
        tcptraceroute = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/tcptraceroute_128.39.19.150.gz'
        vmstat = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/vmstat.gz'

        headerlines = 4 # how many lines in the file is header
        # ca = types.CrudeAnalyzer(window_size=1000)

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
                    record = microdep_models.CrudeRecord.objects.create(
                        stream_id = key_values[0].split('=')[1], # ID=1
                        seq = key_values[1].split('=')[1],
                        src = key_values[2].split('=')[1].split(':')[0], # SRC=ip:port
                        dst = key_values[3].split('=')[1].split(':')[0], # DST=ip:port
                        tx = key_values[4].split('=')[1],
                        rx = key_values[5].split('=')[1],
                        size = key_values[6].split('=')[1],
                        hoplimit = key_values[7].split('=')[1],
                    )
                    # ca.add_record(record)
                    # print(record.__dict__)

                except Exception as e:
                    print(e)
                    print(i)
                    print(line)

        # print(ca)
        # print(ca.get_all_attr_names())
        # print(ca.__dict__)
        # End of handle

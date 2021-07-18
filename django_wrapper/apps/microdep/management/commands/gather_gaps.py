# imports
import gzip

from django.utils import timezone
from django.core import management
from django.core.management.base import BaseCommand

from microdep import models as microdep_models
from microdep import utils as microdep_utils
# End: imports -----------------------------------------------------------------

# Settings:


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        # Positional arguments

        # Named (optional) arguments
        parser.add_argument('--root_path', type=str, help='Root directory to search for filepattern')
        parser.add_argument('--pattern', type=str, help='Glob pattern')

    def handle(self, *args, **options):
        print(f"\n== COMMAND: {__file__} ==")

        
        # crude = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/crude-00_00_01.gz'
        # traceroute = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/traceroute_128.39.19.150.gz'
        # tcptraceroute = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/tcptraceroute_128.39.19.150.gz'
        # vmstat = 'C:/Users/twide/my_projects/git/ml-microdep/secret/fredrikstad-mp.hiof.no/2021-02-07/vmstat.gz'
        tekno_crude = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/crude-00_00_02.gz'
        # traceroute2 = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/traceroute_128.39.19.150.gz'
        # tcptraceroute2 = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/tcptraceroute_128.39.19.150.gz'
        # vmstat2 = 'C:/Users/twide/my_projects/git/ml-microdep/secret/teknobyen-mp.uninett.no/2021-02-07/vmstat.gz'


        ca = microdep_utils.CrudeAnalyzer(window_size=1000)

        with gzip.open(filename=tekno_crude, mode='rt') as file:

            for i, line in enumerate(file):
                key_values = line.split() # list of key-value pairs # ['ID=1', 'RX=15434', ...]

                if i % 1000000 == 0:
                    print(f"{i}: {line}")

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
                    ca.add_record(record)
                    # print(record.__dict__)

                except Exception as e:
                    print(e)
                    print(i)
                    print(line)

        print(ca)
        # print(ca.__dict__)
        # End of handle

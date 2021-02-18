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

    def handle(self, *args, **options):
        print(f"\n== COMMAND: {__file__} ==")

        ca = microdep_utils.CrudeAnalyzer2(window_size=1000)

        for record in microdep_models.CrudeRecord.objects.filter(stream_id=1)[:3000]:
            ca.add_record(record)
            # print(record.__dict__)

        print(ca)
        print(ca.stats)
        # print(ca.get_all_attr_names())
        # print(ca.__dict__)
        # End of handle

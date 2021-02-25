# imports
import gzip
import os

from django.db import connections
from django.utils import timezone
from django.core import management
from django.core.management.base import BaseCommand
from django.conf import settings


from microdep import models as microdep_models
# End: imports -----------------------------------------------------------------

# Settings:


class Command(BaseCommand):

    def handle(self, *args, **options):
        print(f"\n== COMMAND: {__file__} ==")
        # https://stackoverflow.com/questions/29840382/single-django-app-to-use-multiple-sqlite3-files-for-database
        # https://stackoverflow.com/questions/56733112/how-to-create-new-database-connection-in-django
        # https://stackoverflow.com/questions/14254315/django-dynamic-database-file
        # print(connections.databases)

        connections.databases['foo'] = connections.databases['default']
        connections.databases['foo']['NAME'] = settings.BASE_DIR / 'bar'
        # print( type(settings.BASE_DIR) )

        microdep_models.CrudeRecord.objects.create()


        for subdir, dirs, files in os.walk(os.environ['SOURCE']):
            # print(files)
            pass
            # for file in files:
            #     print(os.path.join(subdir, file))
                # connections.databases['hehe'] = connections.databases['default']
                # connections.databases['hehe']['NAME'] = subdir

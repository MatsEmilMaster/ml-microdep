# imports
import gzip
import glob
import os
import pathlib

from django.db import connections
from django.utils import timezone
from django.core import management
from django.core.management.base import BaseCommand
from django.conf import settings



from apps.microdep import models as microdep_models
# End: imports -----------------------------------------------------------------

# Settings:


class Command(BaseCommand):

    def handle(self, *args, **options):
        print(f"\n== COMMAND: {__file__} ==")
        # https://stackoverflow.com/questions/29840382/single-django-app-to-use-multiple-sqlite3-files-for-database
        # https://stackoverflow.com/questions/56733112/how-to-create-new-database-connection-in-django
        # https://stackoverflow.com/questions/14254315/django-dynamic-database-file
        # print(connections.databases)

        """
        Create a database for each host in /dynga/data/
        Analyze crude streams and create Gap in db
        """

        crude_pattern = '**/*crude*.gz'

        data_root = pathlib.Path(os.environ['DATA_ROOT']).resolve()

        # finds all crude files
        for path in data_root.rglob(crude_pattern): # /**/<data_root>/<domain>/<host>/<yyyy.mm.dd>/*crude*.gz
            path_tokens = path.as_posix().split('/')
            domain = path_tokens[-4]
            host = path_tokens[-3]
            db_key = f"{domain}_{host}"

            # get or create db
            if not connections.databases.get(db_key, None):
                print(db_key)
                connections.databases[db_key] = dict(connections.databases['default'])
                connections.databases[db_key]['NAME'] = path.parent.parent / f"{db_key}.db"
                # print(connections.databases[db_key])
                

            # analyze file
            # add gaps to db in data_root/domain/host

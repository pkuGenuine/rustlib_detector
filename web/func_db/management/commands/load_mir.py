import os
import logging

from django.core.management.base import BaseCommand

from general_utils.load import load_mir


class Command(BaseCommand):
    help = 'Load function mir info.'

    def add_arguments(self, parser):
        parser.add_argument('data_path', nargs='+')

    def handle(self, *args, **options):
        for p in options['data_path']:
            if os.path.isdir(p):
                for file_name in filter(lambda x: x.endswith('.json'), os.listdir(p)):
                    load_mir(os.path.join(p, file_name))
            elif p.endswith('.json'):
                load_mir(p)
            else:
                logging.error(f'Unexpected path: {p}')
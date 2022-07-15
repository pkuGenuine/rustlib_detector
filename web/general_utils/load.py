import os
import json
import logging
import re

from django.conf import settings
from rust_demangler import demangle

from func_db.models import Crate
from general_utils.parser import parser


def load_mir(file_path: str, re_create: bool=False):
    """_summary_

    :param file_path: _description_
    :type file_path: str
    :param re_create: _description_, defaults to False
    :type re_create: bool, optional
    """
    with open(file_path) as f:
        mir_info_dict = json.load(f)
    crate_name, version = os.path.basename(file_path).rstrip('.json').rsplit('_', maxsplit=1)
    crate, crated = Crate.objects.get_or_create(name=crate_name, version=version)
    if crated or re_create:
        logging.info(f'Load mir info for {crate_name} ({version}).')
        for mir_label, bb_list in mir_info_dict:
            if '{' in mir_label:
                full_name = mir_label[mir_label.find('{')+1:-1]
                try:
                    ast = parser.parse(full_name)
                except:
                    logging.error(f'Failed to parse {full_name}')
            else:
                logging.debug(f'Not function {mir_label}')
    else:
        logging.debug(f'Crate {crate_name} ({version}) already loaded, skip.')


def load_bin(file_path: str, re_create: bool=False):
    with open(file_path) as f:
        bin_info_dict = json.load(f)
    for k, v in bin_info_dict.items():
        try:
            name = demangle(v['func_name'])
            if name.startswith('_R'):
                logging.debug(f'Demangled: {name}')
        except:
            logging.error(f'Failed to demangle {name}')
            continue



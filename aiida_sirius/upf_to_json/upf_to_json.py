import json
import sys
import re
from .upf1_to_json import parse_upf1_from_string
from .upf2_to_json import parse_upf2_from_string

def get_upf_version(upf):
    line = upf.split('\n')[0]
    if "<PP_INFO>" in line:
        return 1
    elif "UPF version" in line:
        return 2
    return 0

def upf_to_json(upf_str, fname):
    version = get_upf_version(upf_str)
    if version == 0:
        return None
    if version == 1:
        pp_dict = parse_upf1_from_string(upf_str)
    if version == 2:
        pp_dict = parse_upf2_from_string(upf_str)

    pp_dict['pseudo_potential']['header']['original_upf_file'] = fname
    return pp_dict

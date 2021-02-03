#!/usr/bin/env python

import yaml

with open("./resources/map.yaml", 'r') as stream:
    try:
        print(yaml.safe_load(stream))
    except yaml.YAMLError as exc:
        print(exc)

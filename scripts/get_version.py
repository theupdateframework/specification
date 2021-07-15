#!/usr/bin/env python3

"""
<Program Name>
  get_version.py

<Author>
  Joshua Lock <jlock@vmware.com>

<Started>
  Feb 2, 2021

<Copyright>
  See LICENSE-MIT for licensing information.

<Purpose>
  Quick and dirty script to get the version number from tuf-spec.md

  Unfortunately GNU grep and BSD grep take different options...
"""

import re
import sys

pattern = re.compile("VERSION (\d+\.\d+\.\d+)")

def get_version():
    out = ''
    spec = 'tuf-spec.md'

    if (len(sys.argv) > 1):
        spec = sys.argv[1]

    with open(spec, 'r') as spec:
        for line in spec:
            for match in re.finditer(pattern, line):
                if match.group():
                    break
        out = match.groups()[0]

    return f'v{out}'

if __name__ == "__main__":
    print(get_version())

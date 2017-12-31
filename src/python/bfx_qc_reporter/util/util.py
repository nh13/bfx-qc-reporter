#!/usr/bin/env python

import sys

def fail(msg):
    """ Writes the message to stderr and exits with code 1. """
    sys.stderr.write(msg + "\n")
    sys.exit(1)

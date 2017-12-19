#!/usr/bin/env python

'''
vAnalyzer Project Description Will Come In Here...
'''


import logging
import sys
import main
from common import (
    display_utils,
    log_utils
)


# Main Application Flow:
if __name__ == '__main__':
    log_utils.update_logging_level(logging.DEBUG)
    display_utils.print_logo()
    main.func_dispatcher(sys.argv)

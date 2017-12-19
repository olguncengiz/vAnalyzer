'''
Includes all the common display functions that need to be imported on the run time.
'''


def print_logo():
    '''
    Prints vAnalyzer logo.

    Args:

    Returns:

    Raises:

    '''

    print "    ______         _               _                    "
    print "   / / / / __   __/_\  _ __   __ _| |_   _ _______ _ __ "
    print "  / / / /  \ \ / //_\\\| '_ \ / _` | | | | |_  / _ \ '__|"
    print " / / / /    \ V /  _  \ | | | (_| | | |_| |/ /  __/ |   "
    print "/_/_/_/      \_/\_/ \_/_| |_|\__,_|_|\__, /___\___|_|   "
    print "                                     |___/              "


def print_usage():
    '''
    Prints vAnalyzer usage hints with parameters.

    Args:

    Returns:

    Raises:

    '''

    print 'boot             - Boot vAnalyzer VM'
    print 'terminate        - Delete vAnalyzer VM'
    print 'trace-start      - Start Trace on Hypervisors'
    print 'trace-end        - End Trace on Hypervisors'
    print 'compare          - Import Traces into Database'
    print 'report           - Compare Traces and Generate Report'

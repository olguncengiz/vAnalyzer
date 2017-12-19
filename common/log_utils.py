'''
Includes all logging functions.
'''


import logging


def update_logging_level(log_level):
    '''
    Updates the logging level on the run.

    Args:
        log_level (integer): The desired log level

    Returns:

    Raises:

    '''

    logging.basicConfig(filename='vAnalyzer.log', format='%(asctime)s - %(levelname)s: %(message)s')
    if log_level == logging.ERROR:
        logging.getLogger().setLevel(logging.ERROR)
    elif log_level == logging.WARNING:
        logging.getLogger().setLevel(logging.WARNING)
    elif log_level == logging.INFO:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.DEBUG)


def display_message(messageType, messageDescription):
    '''
    Displays messages on screen and logs messages into log file.

    Args:
        messageType (integer): Type of message
        messageDescription (string): Text description of message to be written

    Returns:

    Raises:

    '''

    log_level = logging.getLogger().getEffectiveLevel()

    if messageType == logging.ERROR and messageType >= log_level:
        logging.error(messageDescription)
        print 'ERROR:', messageDescription
    elif messageType == logging.WARNING and messageType >= log_level:
        logging.warning(messageDescription)
        print 'WARNING:', messageDescription
    elif messageType == logging.INFO and messageType >= log_level:
        logging.info(messageDescription)
        print 'INFO:', messageDescription
    elif messageType == logging.DEBUG and messageType >= log_level:
        logging.debug(messageDescription)
        print 'DEBUG:', messageDescription
    elif messageType == logging.NOTSET:
        logging.debug(messageDescription)
        print messageDescription


def response_to_question(question, default='yes'):
    '''
    Displays a question on screen and prompts for an answer.

    Args:
        question (string): Question description
        default (string): Default answer to be selected

    Returns:
        boolean: True or False according to answer

    Raises:

    '''

    valid = {'yes': True, 'y': True, 'ye': True,
             'no': False, 'n': False}

    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        prompt = ' [y/n] '

    while True:
        display_message(logging.NOTSET, question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            display_message(logging.NOTSET, 'Answer: %s' % default)
            return valid[default]
        elif choice in valid:
            display_message(logging.NOTSET, 'Answer: %s' % choice)
            return valid[choice]
        else:
            display_message(logging.NOTSET, "Please respond with 'yes', 'y', 'no' or 'n'.")

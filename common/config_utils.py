'''
Includes all functions to read the configuration from a file.
'''


from ConfigParser import SafeConfigParser


CONFIG_FILE = 'config.ini'


def read_configuration():
    '''
    Reads the configuration file and returns the dictionary of sections with options.

    Args:

    Returns:
        dictionary: The key / value pairs of sections and options

    Raises:

    '''

    parser = SafeConfigParser(allow_no_value=True)
    parser.read(CONFIG_FILE)

    params = dict()

    for section_name in parser.sections():
        section = dict()
        for name, value in parser.items(section_name):
            section.update({name: value})
        params.update({section_name: section})

    return params


def get_options(section):
    '''
    Returns all options listed under a section.

    Args:
        section (string): The section where the options are listed

    Returns:
        list: The list of options in a section

    Raises:

    '''

    parser = SafeConfigParser(allow_no_value=True)
    parser.read(CONFIG_FILE)

    options = parser.options(section)

    return options


def get_option_value(section, option):
    '''
    Reads configuration values from configuration file.

    Args:
        section (string): The section where the option is listed
        option (string): The name of the value being searched

    Returns:
        dictionary: The key / value pairs for configuration values

    Raises:

    '''

    parser = SafeConfigParser(allow_no_value=True)
    parser.read(CONFIG_FILE)

    return parser.get(section, option)

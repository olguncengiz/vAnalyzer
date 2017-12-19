'''
Includes all the common system functions that need to be imported on the run time.
'''


import json
import logging
import os
import sys
from common import log_utils


PROTOCOL_FOLDER = 'protocols'


def die():
    '''
    A function to exit program.

    Args:

    Returns:

    Raises:

    '''

    sys.exit()


def is_a_file(filename):
    '''
    To check if a given file name is a file.

    Args:
        filename (string): File name to be checked.

    Returns:
        boolean: Whether the file exists or not.

    Raises:

    '''

    if os.path.isfile(filename) and os.access(filename, os.R_OK):
        return True
    else:
        return False


def are_environment_variables_sourced():
    '''
    To check if a given file name is a file.

    Args:

    Returns:
        boolean: Whether the environment variables are sourced or not.

    Raises:

    '''

    environmentVariables = [
        'OS_USERNAME',
        'OS_PASSWORD',
        'OS_TENANT_NAME',
        'OS_NO_CACHE',
        'OS_AUTH_URL',
        'OS_AUTH_STRATEGY',
        'OS_REGION_NAME']

    for variable in environmentVariables:
        try:
            os.environ[variable]
        except KeyError as e:
            log_utils.display_message(logging.ERROR, 'Missing environment variable! You must provide %s. Please source the credentials file.' % variable)
            return False
    return True


def create_heat_template(params):
    '''
    A function to create Heat YAML file from a template file.

    Args:
        params (dictionary): Dictionary object which holds parameter values for Heat YAML file.

    Returns:

    Raises:

    '''

    # Assign Parameters
    name = params['vAnalyzer']['instance_name']
    image = params['vAnalyzer']['image_name']
    password = params['vAnalyzer']['password']
    flavor = params['vAnalyzer']['flavor_name']
    publicNetId = params['vAnalyzer']['public_net_id']
    privateNetId = params['vAnalyzer']['private_net_id']
    privateSubnetId = params['vAnalyzer']['private_subnet_id']
    volume = params['vAnalyzer']['volume_size']
    logging.debug('vAnalyzer Instance Parameters: %s' % [name, image, password, flavor, publicNetId, privateSubnetId, volume])

    yaml_file = params['Environment']['yaml_file']
    temp_file = params['Environment']['temp_file']

    log_utils.display_message(logging.INFO, 'Creating %s File' % temp_file)

    try:
        with open(yaml_file, 'wt') as fout:
            with open(temp_file, 'rt') as fin:
                for line in fin:
                    new_line = line

                    new_line = new_line.replace('$$$instance_name$$$', name)
                    new_line = new_line.replace('$$$image$$$', image)
                    new_line = new_line.replace('$$$os_password$$$', password)
                    new_line = new_line.replace('$$$flavor$$$', flavor)
                    new_line = new_line.replace('$$$public_net_id$$$', publicNetId)
                    new_line = new_line.replace('$$$private_net_id$$$', privateNetId)
                    new_line = new_line.replace('$$$private_subnet_id$$$', privateSubnetId)
                    new_line = new_line.replace('$$$volume_size$$$', volume)

                    fout.write(new_line)

        log_utils.display_message(logging.INFO, 'File %s Created Successfully' % yaml_file)
    except (IOError, OSError) as e:
        log_utils.display_message(logging.ERROR, '%s - %s' % (e.filename, e.strerror))


def delete_file(filename):
    '''
    A function to delete a file.

    Args:
        filename (string): The file name to delete

    Returns:

    Raises:

    '''

    log_utils.display_message(logging.INFO, 'Deleting %s File' % filename)

    if os.path.exists(filename):
        try:
            os.remove(filename)
            log_utils.display_message(logging.INFO, 'File %s Deleted Successfully' % filename)
        except (IOError, OSError) as e:
            log_utils.display_message(logging.ERROR, '%s - %s' % (e.filename, e.strerror))
    else:
        log_utils.display_message(logging.ERROR, 'File %s not found!' % filename)


def save_as_json(fileName, dictValues):
    '''
    A function to save dictionary as a file.

    Args:
        fileName (string): The file name to save
        dictValues (dictionary): The text to write into file

    Returns:

    Raises:

    '''

    with open(fileName, 'w') as f:
        json.dump(dictValues, f)


def append_file(filename, text_to_append):
    '''
    A function to append to a file.

    Args:
        filename (string): The file name to append
        text_to_append (string): The text to write into file

    Returns:

    Raises:

    '''

    try:
        with open(filename, 'a') as f:
            f.write('%s\n' % text_to_append)
    except (IOError, OSError) as e:
        log_utils.display_message(logging.ERROR, '%s - %s' % (e.filename, e.strerror))


def read_one_line_file(filename):
    '''
    A function to read all lines in a file to a single line.

    Args:
        filename (string): The file name to read

    Returns:
        string: The one-liner text which is read from a file

    Raises:

    '''

    oneline = ''
    try:
        with open(filename, 'r') as f:
            for line in f:
                oneline = oneline + line.strip() + ' '
        oneline = oneline.strip()
    except (IOError, OSError) as e:
        log_utils.display_message(logging.ERROR, '%s - %s' % (e.filename, e.strerror))

    return oneline


def read_file(filename):
    '''
    A function to read all lines in a file to a string .

    Args:
        filename (string): The file name to read

    Returns:
        string: The variable which holds text from a file

    Raises:

    '''

    file_string = ''
    try:
        f = open(filename, 'r')
        file_string = f.read()
    except (IOError, OSError) as e:
        log_utils.display_message(logging.ERROR, '%s - %s' % (e.filename, e.strerror))

    return file_string


def get_subfolders(path):
    '''
    A function to get subdirectories in a path.

    Args:
        path (string): The folder containing folders

    Returns:
        list: The list of files and folders in path

    Raises:

    '''

    folder_list = list()
    for name in os.listdir(path):
        if os.path.isdir(path + '/' + name):
            folder_list.append(name)

    logging.debug('Folder List: %s' % folder_list)
    return folder_list


def get_supported_protocols():
    '''
    A function to get all supported protocols in a path by looking at YAML files.

    Args:

    Returns:
        list: The list of supported protocols

    Raises:

    '''
    protocol_list = get_subfolders(get_current_directory() + '/' + PROTOCOL_FOLDER)
    return protocol_list


def get_protocol_yaml(protocol):
    '''
    A function returns the yaml file path for a given protocol.

    Args:
        protocol (string): Name of the protocol

    Returns:
        string: The path value parameter for the protocol yaml file

    Raises:

    '''

    yaml_file = get_current_directory() + '/' + PROTOCOL_FOLDER + '/' + protocol + '/' + protocol + '.yaml'
    logging.debug('YAML File: %s' % yaml_file)
    return yaml_file


def get_port(protocol):
    '''
    A function returns the port of a given protocol.

    Args:
        protocol (string): Name of the protocol

    Returns:
        string: The port value parameter for the protocol

    Raises:

    '''

    yaml_file = get_protocol_yaml(protocol)

    if is_a_file(yaml_file):
        try:
            with open(yaml_file, 'r') as f:
                for line in f:
                    if 'PROTOCOL PORT:' in line:
                        return line.split(':')[1].strip()
        except (IOError, OSError) as e:
            log_utils.display_message(logging.ERROR, '%s - %s' % (e.filename, e.strerror))
    else:
        return ''


def get_current_directory():
    '''
    A function returns the port of a given protocol.

    Args:

    Returns:
        string: Current working directory path

    Raises:

    '''

    return os.getcwd()

'''
Includes all network functions.
'''


import datetime
import logging
import os
import paramiko
import re
import socket
import time
from common import (
    log_utils,
    sys_utils
)
from common.ssh_connection import SshConnection


def validate(ip):
    '''
    A function to validate if a given IP is valid.

    Args:
        ip (string): IP in XXX.XXX.XXX.XXX format

    Returns:
        boolean: Returns True if IP is valid or False if IP is not valid

    Raises:

    '''

    an_ip = map(int, ip.split('.'))
    valid = True
    if len(an_ip) != 4:
        return False

    ip_a, ip_b, _, _ = an_ip
    if ip_a < 1 or ip_a > 223 or ip_a == 127:
        return False
    if ip_a == 169 and ip_b == 254:
        return False
    for i in xrange(1, 4):
        if not (1 <= an_ip[i] <= 255):
            return False

    return valid


def delete_pcap_files(params):
    '''
    A function to delete PCAP files on Controller, Compute and Fuel nodes.

    Args:
        params (dictionary): The dictionary which has values for parameters

    Returns:

    Raises:

    '''

    username = params['username']
    password = params['password']

    compute_ssh_conn = params['compute_ssh_conn']
    controllerNode = params['controllerNode']
    computeNode = params['computeNode']

    # On Compute Node
    logging.debug('Connected to %s server...' % compute_ssh_conn.get_last_ssh_connection())
    log_utils.display_message(logging.DEBUG, 'Deleting pcap files from Compute node')
    compute_ssh_conn.send('find . -type f -iname \*.pcap -delete')
    compute_ssh_conn.close_last_ssh_connection()

    # On Fuel Node
    logging.debug('Connected to %s server...' % compute_ssh_conn.get_last_ssh_connection())
    log_utils.display_message(logging.DEBUG, 'Deleting pcap files from Fuel node')
    compute_ssh_conn.send('cd /tmp')
    compute_ssh_conn.send('find . -type f -iname \*.pcap -delete')

    # On Controller Node
    log_utils.display_message(logging.DEBUG, 'Deleting pcap files from Controller node')
    compute_ssh_conn.open_ssh_connection(controllerNode, username, password)
    logging.debug('Connected to %s server...' % compute_ssh_conn.get_last_ssh_connection())
    compute_ssh_conn.send('cd /tmp')
    compute_ssh_conn.send('find . -type f -iname \*.pcap -delete')
    compute_ssh_conn.close_last_ssh_connection()

    # On Fuel Node
    logging.debug('Connected to %s server...' % compute_ssh_conn.get_last_ssh_connection())
    compute_ssh_conn.open_ssh_connection(computeNode, username, password)

    # On Compute Node
    logging.debug('Connected to %s server...' % compute_ssh_conn.get_last_ssh_connection())


def get_integrity(sshConn):
    '''
    A function to calculate md5sum values on SSH connection file system.

    Args:
        sshConn (SshConnection): The active connection to the server

    Returns:
        dictionary: The key / value pairs for files and md5sum values

    Raises:

    '''

    md5_list = {}

    # Find all files in directory ended with .pcap
    command = 'for i in `ls | grep .pcap`; do echo ***MD5SUM***=`md5sum $i`; done'
    output = sshConn.send(command)
    logging.debug('md5sum Output: %s' % output)

    # Pattern to read output
    md5_pattern_file = '...MD5SUM...='

    # Search for the pattern in ssh output
    regex = re.compile('(?<=' + md5_pattern_file + ').+')
    md5_file_names = regex.findall(output)
    logging.debug('md5sum Names: %s' % md5_file_names)

    # Remove first line from output, last line and last two unneccesary elements from the output
    string = output.split('\n', 1)[-1]
    string.rsplit('\n', 1)[0]

    # Split from new line and remove last 2 lines which is unrelated
    list_of_lines = string.split('\n')
    list_of_lines = list_of_lines[:-1]

    # Splitting and getting values
    for line in list_of_lines:
        list_of_items_in_line = line.split()
        # Insert to dictionary in format which file name is key and correspondng md5 value is the value
        md5_list[list_of_items_in_line[1]] = list_of_items_in_line[0]

    return md5_list


def get_controller_hostname():
    '''
    A function which returns hostname where vAnalyzer application is run.

    Args:

    Returns:
        string: The name of the host

    Raises:

    '''

    return socket.gethostname()


def check_pcap_file_integrity(params):
    '''
    A function which checks transferred PCAP files integrity.

    Args:
        params (dictionary): The dictionary which has values for parameters

    Returns:
        boolean: Returns True if PCAP file integrities match or False if they don't.

    Raises:

    '''

    # Get SSH Connections
    compute_ssh_conn = params['compute_ssh_conn']
    vanalyzer_ssh_conn = params['vanalyzer_ssh_conn']

    # For analyze engine instance, go to vanalyzer-inbox folder
    vanalyzer_ssh_conn.send('cd vanalyzer-inbox')

    result = True

    md5_list_compute = {}
    md5_list_vAnalyzer = {}

    # Check MD5 sum of each of pcap file in vAnalyzer node and store it in dictionary  md5_list_vAnalyzer={}
    md5_list_vAnalyzer = get_integrity(vanalyzer_ssh_conn)
    logging.debug('md5 sums of files in vAnalyzer node: %s' % md5_list_vAnalyzer)

    # Check MD5 sum of each of pcap file in compute node and store it in dictionary  md5_list_compute={}
    md5_list_compute = get_integrity(compute_ssh_conn)
    logging.debug('md5 sums of files in compute node: %s' % md5_list_compute)

    log_utils.display_message(logging.DEBUG, 'Checking md5 sums of files in Compute node and vAnalyzer node')

    # Compare md5sums
    for key, value in md5_list_compute.iteritems():
        if key not in list(md5_list_vAnalyzer.keys()):
            log_utils.display_message(logging.ERROR, 'There is an error when transferring file: %s , does not exist ' % key)
            result = False
            break
        else:
            if value != md5_list_vAnalyzer[key]:
                log_utils.display_message(logging.ERROR, 'There is an error when transferring file: %s , corrupted .' % key)
                result = False
                break

    return result


def build_trace_command(protocol, trace_list):
    '''
    A function which builds and returns trace start command.

    Args:
        protocol (string): The protocol for which the trace will be started
        traceList (list): The list of tap device IDs

    Returns:
        string: Returns the trace command

    Raises:

    '''

    command = 'nohup tcpdump -nn -w ' + build_pcap_file_name(protocol) + ' ' + sys_utils.get_port(protocol) + ' '

    for tapDeviceId in trace_list:
        command = command + '-i ' + tapDeviceId + ' '

    command = command + '</dev/null &>/dev/null & echo ***PID***=$!'
    logging.debug('Command: %s' % command)

    return command


def build_pcap_file_name(protocol):
    '''
    A function which builds PCAP file name in date time format.

    Args:
        protocol (string): The protocol which the file will be named with

    Returns:
        string: The name of the PCAP file

    Raises:

    '''

    filename = 'trace_' + protocol + '_' + datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S') + '.pcap'
    logging.debug('Filename: %s' % filename)
    return filename


def get_pid_from_output(output):
    '''
    A function which returns PID from SSH connection command output.

    Args:
        output (string): The output which returned from a command execution

    Returns:
        string: The PID to be returned

    Raises:

    '''

    # PIDs are printed as ***PID***= in ssh output
    pid_pattern = '...PID...='
    # Search for the pattern in ssh output
    regex = re.compile('(?<=' + pid_pattern + ').+')
    pid_value = regex.findall(output)
    log_utils.display_message(logging.DEBUG, 'PID Value: %s' % pid_value)
    # Returns every 2nd element of the list
    pid = pid_value[1].strip()

    return pid


def kill_processes(params):
    '''
    A function which kills all PIDs on server.

    Args:
        params (dictionary): The dictionary which has values for parameters

    Returns:

    Raises:

    '''

    pid_file = params['pid_file']
    ssh_conn = params['compute_ssh_conn']

    # Read pid values in the pid file for terminate operation
    command = 'kill -SIGINT ' + sys_utils.read_one_line_file(pid_file)
    logging.debug('Delete Command: %s' % command)
    ssh_conn.send(command)

    # Delete process id file on Controller
    sys_utils.delete_file(pid_file)


def espcap_import_pcaps(params):
    '''
    A function that calls espcap to import pcap files into elasticsearch database.

    Args:
        params (dictionary): The dictionary which has values for parameters

    Returns:

    Raises:

    '''

    ssh_conn = params['vanalyzer_ssh_conn']

    # Import pcap files into Elasticsearch database
    command = 'cd espcap/src/ && ./espcap.py --dir=/home/ubuntu/vanalyzer-inbox --node=localhost:9200'
    logging.debug('espcap Command: %s' % command)
    ssh_conn.send(command)


def move_pcaps_to_archive_folder(params):
    '''
    A function that moves pcap files to archive folder.

    Args:
        params (dictionary): The dictionary which has values for parameters

    Returns:

    Raises:

    '''

    ssh_conn = params['vanalyzer_ssh_conn']

    # Move pcap files into archive folder
    command = 'mv ../../vanalyzer-inbox/* ../../vanalyzer-archive/'
    logging.debug('Move Command: %s' % command)
    ssh_conn.send(command)


def transfer_pcaps_from_compute_to_controller(params):
    '''
    A function which transfers PCAP files from Compute node to Controller node.

    Args:
        params (dictionary): The dictionary which has values for parameters

    Returns:

    Raises:

    '''

    # Assign parameters
    ip = params['ip']
    username = params['username']
    password = params['password']
    instance_name = params['instance_name']
    computeNode = params['computeNode']
    vanalyzer_username = params['vanalyzer_username']
    vAnalyzer_ip = params['vanalyzer_ip']
    ssh_conn = params['compute_ssh_conn']
    controllerNode = params['controllerNode']

    log_utils.display_message(logging.DEBUG, 'Transferring PCAP files from Compute node to Fuel Node')

    command = 'scp trace_*.pcap ' + username + '@' + ip + ':/tmp'

    ssh_conn.send(command, '\'s password: ')
    ssh_conn.send(password)

    # ssh to Fuel Node
    ssh_conn.open_ssh_connection(ip, username, password)

    log_utils.display_message(logging.DEBUG, 'Transferring PCAP files from Fuel node to Controller Node')
    ssh_conn.send('hostname')
    command = 'scp /tmp/trace_*.pcap ' + controllerNode + ':/tmp'
    ssh_conn.send(command, ']# ')

    # Exit to Compute Node
    ssh_conn.close_last_ssh_connection()


def transfer_files_from_controller_to_vanalyzer(params):
    '''
    A function which transfers PCAP files from Controller node to Analyzer Engine.

    Args:
        params (dictionary): The dictionary which has values for parameters

    Returns:

    Raises:

    '''

    log_utils.display_message(logging.DEBUG, 'Transferring PCAP files from Controller node to Analyze Engine')
    md5_list_vAnalyzer = {}

    logging.debug('Transfer files from controller to vAnalyzer parameters: %s' % params)

    # Logging into device
    ip = params['vanalyzer_ip']
    username = params['vanalyzer_username']
    password = params['vanalyzer_password']
    port = 22
    fromFolder = params['from_folder']
    toFolder = params['to_folder']
    extension = params['extension']

    transport = paramiko.Transport((ip, port))

    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    filepath = fromFolder
    localpath = toFolder

    for dirpath, dirnames, filenames in os.walk(filepath):
        remote_path = os.path.join(localpath, dirpath)

        # make remote directory ...
        for filename in filenames:
            if filename.endswith(extension):
                local_path = os.path.join(dirpath, filename)
                remote_filepath = os.path.join(localpath, filename)
                # put file
                sftp.put(local_path, remote_filepath)

    sftp.close()
    transport.close()


def trace_start(params):
    '''
    A function which starts tracing on Compute node.

    Args:
        params (dictionary): The dictionary which has values for parameters

    Returns:

    Raises:

    '''

    # Assign parameters
    ip = params['ip']
    username = params['username']
    password = params['password']
    traceList = params['traceList']
    protocol = params['protocol']
    pid_file = params['pid_file']
    computeNode = params['computeNode']

    # Open an SSH Connection to Fuel Node
    ssh_conn = SshConnection(ip, username, password)

    # Establish an SSH Connection to the compute node
    ssh_conn.open_ssh_connection(computeNode, username, password)

    log_utils.display_message(logging.INFO, 'Running tcpdump With Tap Device ID List %s For %s Protocol.' % (traceList, protocol))

    command = build_trace_command(protocol, traceList)

    # Using nohup to keep tcpdump process running upon ssh connection close
    output = ssh_conn.send(command)
    logging.debug('Output From Compute: %s' % output)

    pid = get_pid_from_output(output)
    log_utils.display_message(logging.DEBUG, 'tcpdump Process ID List For %s Protocol: %s' % (protocol, pid))

    # Record pid value in a file for terminate operation
    sys_utils.append_file(pid_file, pid)


def trace_end(params):
    '''
    A function which ends tracing on Compute node.

    Args:
        params (dictionary): The dictionary which has values for parameters

    Returns:

    Raises:

    '''

    # Assign parameters
    ip = params['ip']
    username = params['username']
    password = params['password']

    # vAnalyzer Instance Parameters
    vanalyzer_ip = params['vanalyzer_ip']
    vanalyzer_username = params['vanalyzer_username']
    vanalyzer_password = params['vanalyzer_password']

    computeNode = params['computeNode']

    # Open an SSH Connection to Fuel Node
    compute_ssh_conn = SshConnection(ip, username, password)

    # Establish an SSH Connection to the compute node
    compute_ssh_conn.open_ssh_connection(computeNode, username, password)

    # Open an SSH Connection to Analyzer Engine
    vanalyzer_ssh_conn = SshConnection(vanalyzer_ip, vanalyzer_username, vanalyzer_password)

    params.update({'compute_ssh_conn': compute_ssh_conn})
    params.update({'vanalyzer_ssh_conn': vanalyzer_ssh_conn})

    # Controller and Compute Nodes
    controllerNode = get_controller_hostname()
    params.update({'controllerNode': controllerNode})
    logging.debug('Controller Node: %s' % controllerNode)

    # Stop tracing and kill processes
    kill_processes(params)

    # Transfer PCAP files from Compute Node to Controller Node
    transfer_pcaps_from_compute_to_controller(params)

    # Transfer PCAP files from Controller node to Analyzer Engine
    params.update({'extension': 'pcap'})
    params.update({'from_folder': '/tmp/'})
    params.update({'to_folder': '/home/ubuntu/vanalyzer-inbox/'})
    transfer_files_from_controller_to_vanalyzer(params)

    # Check file integrity
    res = check_pcap_file_integrity(params)
    logging.debug('Check result for md5sum: %s' % res)

    # If integrities match, delete the files
    if res:
        delete_pcap_files(params)
    # Integrities don't match
    else:
        log_utils.display_message(logging.ERROR, 'Deleting pcap files from controller node failed: md5 check sum is wrong!')


def import_pcaps_to_db_in_vanalyzer(params):
    '''
    A function imports pcaps into Elasticsearch DB.

    Args:
        params (dictionary): The dictionary which has values for parameters

    Returns:

    Raises:

    '''

    # vAnalyzer Instance Parameters
    vanalyzer_ip = params['vanalyzer_ip']
    vanalyzer_username = params['vanalyzer_username']
    vanalyzer_password = params['vanalyzer_password']

    # Open an SSH Connection to Analyzer Engine
    vanalyzer_ssh_conn = SshConnection(vanalyzer_ip, vanalyzer_username, vanalyzer_password)
    params.update({'vanalyzer_ssh_conn': vanalyzer_ssh_conn})
    espcap_import_pcaps(params)

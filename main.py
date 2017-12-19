'''
vAnalyzer - A command line tool for tracing and analyzing network packages.

Sample Usage:

$ vanalyzer trace-start

... ADDITIONAL INFO ...

'''

import logging
import sys
from common import (
    config_utils,
    display_utils,
    log_utils,
    network_utils,
    report_utils,
    sys_utils
)
from common.vOpenstack import vOpenstack


def usage(params={}):
    '''
    A function to print vAnalyzer usage.

    Args:
        params (dictionary): vAnalyzer configurations

    Returns:

    Raises:

    '''

    display_utils.print_usage()


def vanalyzer_boot(params):
    '''
    A function to boot the vAnalyzer instance.

    Args:
        params (dictionary): vAnalyzer configurations

    Returns:

    Raises:

    '''

    log_utils.display_message(logging.INFO, 'vAnalyzer Boot')

    # Create a new vOpenstack instance
    openstack = vOpenstack()

    # Get instance name and YAML template file from parameters dictionary
    instance_name = params['vAnalyzer']['instance_name']
    yaml_file = params['Environment']['yaml_file']

    # Check if an instance or a stack exists with the same name
    if openstack.get_instance_id(instance_name) == '' and openstack.get_stack_id(instance_name) == '':
        # Create Heat YAML file from template
        sys_utils.create_heat_template(params)

        # Create Stack
        openstack.create_stack(instance_name, yaml_file)
        log_utils.display_message(logging.INFO, 'Heat Stack Create In Progress')
    # Instance or stack already exists
    else:
        log_utils.display_message(logging.ERROR, '%s Instance or Stack Already Exists!' % instance_name)
        sys_utils.die()


def vanalyzer_terminate(params):
    '''
    A function to terminate the vAnalyzer instance.

    Args:
        params (dictionary): vAnalyzer configurations

    Returns:

    Raises:

    '''

    log_utils.display_message(logging.INFO, 'vAnalyzer Terminate')

    # Get instance name from parameters dictionary
    instance_name = params['vAnalyzer']['instance_name']

    # Check if there are any running processes
    if sys_utils.is_a_file(params['Environment']['pid_file']):
        log_utils.display_message(logging.ERROR, 'Please stop tracing process and try again')
        sys_utils.die()

    # Ask for approval of deletion
    if log_utils.response_to_question('Do you really want to delete the %s stack? ' % instance_name, default='yes'):
        # Create a new vOpenstack instance
        openstack = vOpenstack()

        # Check if instance or stack with given name exists
        instanceId = openstack.get_instance_id(instance_name)
        stackId = openstack.get_stack_id(instance_name)
        if instanceId != '' and stackId != '':
            # Delete stack
            openstack.delete_stack(instance_name, stackId)
            log_utils.display_message(logging.INFO, 'Heat Stack Deletion In Progress.')

            # Delete YAML file
            sys_utils.delete_file(params['Environment']['yaml_file'])
        # Instance or stack does not exist
        else:
            log_utils.display_message(logging.ERROR, '%s Instance or Stack Does Not Exist!' % instance_name)
            sys_utils.die()
    # Deletion aborted
    else:
        log_utils.display_message(logging.INFO, 'Exiting vAnalyzer.')
        sys_utils.die()


def trace_start(params):
    '''
    A function to start network package trace.

    Args:
        params (dictionary): vAnalyzer configurations

    Returns:

    Raises:

    '''

    log_utils.display_message(logging.INFO, 'vAnalyzer Trace Start')

    # Get instance name from parameters dictionary
    instance_name = params['vAnalyzer']['instance_name']

    # Create a new vOpenstack instance
    openstack = vOpenstack()

    # Check if there are any running processes
    if sys_utils.is_a_file(params['Environment']['pid_file']):
        log_utils.display_message(logging.ERROR, 'Please stop tracing process and try again')
        sys_utils.die()

    # Check if instance or stack with given name exists
    instanceId = openstack.get_instance_id(instance_name)
    stackId = openstack.get_stack_id(instance_name)
    if instanceId != '' and stackId != '':
        # Check Compute Hostname
        computeNode = openstack.get_compute_hostname(instance_name)

        # Ask for confirmation on trace start operation
        if log_utils.response_to_question('Do you want to start the trace on %s ? ' % computeNode, default='yes'):
            # Get list of all virtual machines
            vmList = openstack.get_all_vms()
            log_utils.display_message(logging.DEBUG, 'Available VMs: %s' % vmList)

            # Get list of available protocols
            protocols = sys_utils.get_supported_protocols()
            log_utils.display_message(logging.DEBUG, 'Supported Protocols: %s' % protocols)

            # Get list of tap device ids
            tapDeviceIDList = openstack.get_tap_device_id_list()

            # Get list of trace protocols in config file
            traces = config_utils.get_options('Trace')

            # For each protocol in trace list, start trace on selected tap device ids
            for protocol in traces:
                # Check if this protocol is valid
                if protocol in protocols:
                    # Get VM list for this protocol
                    protocolVms = params['Trace'][protocol].split(',')
                    protocolVms = map(lambda x: x.strip(), protocolVms)

                    # Check if VM list is empty or not
                    if len(protocolVms) != 0:
                        logging.debug('VM List: %s' % protocolVms)

                        traceList = list()
                        for vm in protocolVms:
                            logging.debug('VM Name: %s' % vm)

                            # Check if VM's tap device id is in tap device id list or not
                            if vm not in tapDeviceIDList:
                                log_utils.display_message(logging.WARNING, 'Instance %s does not exist! %s protocol will be ignored.' % (vm, protocol))
                                del traceList[:]
                                break

                            # Get VM id by VM name
                            vmId = openstack.get_instance_id(vm)

                            # Check if VM exists or not
                            if vmId == '':
                                log_utils.display_message(logging.WARNING, 'Instance %s is not running! %s protocol will be ignored.' % (vm, protocol))
                                del traceList[:]
                                break
                            traceList.append(tapDeviceIDList.get(vm))

                        # Connect to Fuel Node. The function then sets another ssh connection to Compute Node
                        if len(traceList) != 0:
                            parameters = dict()
                            parameters.update({'ip': params['Fuel']['fuel_node']})
                            parameters.update({'username': params['Fuel']['fuel_node_username']})
                            parameters.update({'password': params['Fuel']['fuel_node_password']})
                            parameters.update({'traceList': traceList})
                            parameters.update({'protocol': protocol})
                            parameters.update({'computeNode': computeNode})
                            parameters.update({'pid_file': params['Environment']['pid_file']})

                            network_utils.trace_start(parameters)
                    # If no protocol is specified
                    elif protocol == 'ANY':
                        pass
                    # No VMs found for this protocol
                    else:
                        log_utils.display_message(logging.WARNING, 'No Configuration Found for %s Protocol.' % protocol)
                # Protocol is not valid
                else:
                    log_utils.display_message(logging.INFO, '%s protocol will be ignored because it is not supported.' % protocol)
        # Trace start aborted
        else:
            log_utils.display_message(logging.INFO, 'Exiting Program.')
            sys_utils.die()
    # Instance or stack does not exist
    else:
        log_utils.display_message(logging.ERROR, '%s Instance or Stack Does Not Exist!' % instance_name)
        sys_utils.die()


def trace_end(params):
    '''
    A function to end network package trace.

    Args:
        params (dictionary): vAnalyzer configurations

    Returns:

    Raises:

    '''

    log_utils.display_message(logging.INFO, 'vAnalyzer Trace End')

    # Get instance name from parameters dictionary
    instance_name = params['vAnalyzer']['instance_name']

    # Check if there is existing traces
    pid_file = params['Environment']['pid_file']
    if sys_utils.is_a_file(pid_file):
        log_utils.display_message(logging.DEBUG, 'Ending tcpdump process on Compute node')

        # Create a new vOpenstack instance
        openstack = vOpenstack()

        # Check if instance or stack with given name exists
        instanceId = openstack.get_instance_id(instance_name)
        stackId = openstack.get_stack_id(instance_name)
        if instanceId != '' and stackId != '':
            # Check Compute Hostname
            computeNode = openstack.get_compute_hostname(instance_name)

            # Get vAnalyzer Instance IP Address
            public_net_name = openstack.get_network_name(params['vAnalyzer']['private_net_id'])
            vanalyzer_ip = openstack.get_instance_ip(instance_name, public_net_name)

            # Ask for confirmation on trace end operation
            if log_utils.response_to_question('Do you want to end the trace(s) on %s ? ' % computeNode, default='yes'):
                parameters = dict()
                parameters.update({'ip': params['Fuel']['fuel_node']})
                parameters.update({'username': params['Fuel']['fuel_node_username']})
                parameters.update({'password': params['Fuel']['fuel_node_password']})
                parameters.update({'pid_file': params['Environment']['pid_file']})
                parameters.update({'computeNode': computeNode})
                parameters.update({'instance_name': instance_name})
                parameters.update({'vanalyzer_ip': vanalyzer_ip})
                parameters.update({'vanalyzer_username': params['vAnalyzer']['username']})
                parameters.update({'vanalyzer_password': params['vAnalyzer']['password']})

                network_utils.trace_end(parameters)
    # No existing traces
    else:
        log_utils.display_message(logging.ERROR, 'There are no running processes. Please start trace first!')
        sys_utils.die()


def compare(params):
    '''
    A function to import captured pcap files into database.

    Args:
        params (dictionary): vAnalyzer configurations

    Returns:

    Raises:

    '''

    log_utils.display_message(logging.INFO, 'vAnalyzer Compare')

    # Get instance name from parameters dictionary
    instance_name = params['vAnalyzer']['instance_name']

    # Create a new vOpenstack instance
    openstack = vOpenstack()

    # Check if there are any running processes
    if sys_utils.is_a_file(params['Environment']['pid_file']):
        log_utils.display_message(logging.ERROR, 'Please stop tracing process and try again')
        sys_utils.die()

    # Check if instance or stack with given name exists
    instanceId = openstack.get_instance_id(instance_name)
    stackId = openstack.get_stack_id(instance_name)
    if instanceId != '' and stackId != '':
        # Get vAnalyzer Instance IP Address
        public_net_name = openstack.get_network_name(params['vAnalyzer']['private_net_id'])
        vanalyzer_ip = openstack.get_instance_ip(instance_name, public_net_name)

        parameters = dict()
        parameters.update({'vanalyzer_ip': vanalyzer_ip})
        parameters.update({'vanalyzer_username': params['vAnalyzer']['username']})
        parameters.update({'vanalyzer_password': params['vAnalyzer']['password']})

        # Import PCAPs to Elasticsearch DB
        log_utils.display_message(logging.DEBUG, 'Importing PCAP files from /home/ubuntu/vanalyzer-inbox folder into Elasticsearch database.')
        network_utils.import_pcaps_to_db_in_vanalyzer(parameters)

        # Move PCAPs from inbox folder to archive folder
        log_utils.display_message(logging.DEBUG, 'Moving PCAP files from /home/ubuntu/vanalyzer-inbox folder to /home/ubuntu/vanalyzer-archive folder.')
        network_utils.move_pcaps_to_archive_folder(parameters)
    # Instance or stack does not exist
    else:
        log_utils.display_message(logging.ERROR, '%s Instance or Stack Does Not Exist!' % instance_name)
        sys_utils.die()


def report(params):
    '''
    A function to compare the traces with specifications and generate report.

    Args:
        params (dictionary): vAnalyzer configurations

    Returns:

    Raises:

    '''

    log_utils.display_message(logging.INFO, 'vAnalyzer Report')

    # Get instance name from parameters dictionary
    instance_name = params['vAnalyzer']['instance_name']

    # Create a new vOpenstack instance
    openstack = vOpenstack()

    # Get vAnalyzer Instance IP Address
    public_net_name = openstack.get_network_name(params['vAnalyzer']['private_net_id'])
    vanalyzer_ip = openstack.get_instance_ip(instance_name, public_net_name)
    params.update({'vanalyzer_ip': vanalyzer_ip})
    params.update({'vanalyzer_ip': vanalyzer_ip})
    params.update({'vanalyzer_username': params['vAnalyzer']['username']})
    params.update({'vanalyzer_password': params['vAnalyzer']['password']})

    # Generate report
    reportFile = report_utils.generate_report(params)

    # Move report file to vAnalyzer instance
    log_utils.display_message(logging.DEBUG, 'Transfering report file to vAnalyzer instance.')
    params.update({'extension': 'json'})
    params.update({'from_folder': sys_utils.get_current_directory()})
    logging.debug(params['from_folder'])
    params.update({'to_folder': '/home/ubuntu/vanalyzer-reports/'})
    network_utils.transfer_files_from_controller_to_vanalyzer(params)

    # Delete JSON Report File
    log_utils.display_message(logging.DEBUG, 'Deleting report file from Controller node.')
    sys_utils.delete_file(reportFile)


def func_dispatcher(args):
    '''
    A function dispatcher that calls functions according to a given CLI command
    when the main function is called.

    Args:
        args (string): System arguments passed when calling main function

    Returns:

    Raises:

    '''

    log_utils.display_message(logging.debug, 'Arguments: %s' % args)

    allowed_commands = {
        'boot': vanalyzer_boot,
        'terminate': vanalyzer_terminate,
        'trace-start': trace_start,
        'trace-end': trace_end,
        'compare': compare,
        'report': report,
        'usage': usage
    }

    print_usage = allowed_commands['usage']

    try:
        # Get first parameter passed to vAnalyzer tool
        command = str(args[1])

        # Check if parameter is valid
        if command in allowed_commands:
            log_utils.display_message(logging.DEBUG, 'vAnalyzer started with parameters: %s' % command)

            # Get configuration values
            vanalyzer_params = config_utils.read_configuration()
            logging.debug('vAnalyzer configurations: %s' % vanalyzer_params)

            # Check if environment variables are sourced
            if sys_utils.are_environment_variables_sourced():
                # Get corresponding function for parameter passed and execute it
                func = allowed_commands[command]
                func(vanalyzer_params)
                log_utils.display_message(logging.INFO, 'vAnalyzer %s operation finished successfully.' % command)
        # Invalid parameter is passed
        else:
            print_usage()
            log_utils.display_message(logging.ERROR, 'Please enter valid arguments!')
    # No parameter passed
    except IndexError:
        print_usage()

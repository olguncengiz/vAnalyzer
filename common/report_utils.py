import datetime
import logging
from common import (
    log_utils,
    sys_utils
)
from vElasticsearch import vElasticsearch


def generate_report(parameters):
    '''
    A function which generates JSON report and returns file name.

    Args:
        parameters (dictionary): The dictionary of values

    Returns:
        string: The file name of the JSON report

    Raises:

    '''

    vanalyzer_ip = parameters['vanalyzer_ip']

    # Create Elasticsearch object
    elasticsearch = vElasticsearch(vanalyzer_ip)

    # Get yaml files from protocol folder
    protocols = sys_utils.get_supported_protocols()

    results = list()
    for protocol in protocols:
        protocol_report = {}
        log_utils.display_message(logging.INFO, 'Executing query for %s protocol.' % protocol)
        yaml_file = sys_utils.get_protocol_yaml(protocol)

        # Get invalid packets for desired protocols
        packets = elasticsearch.execute_yaml_query(yaml_file)
        invalid_packets = int(packets['hits']['total'])
        log_utils.display_message(logging.DEBUG, 'Number of invalid packets: %i' % invalid_packets)

        # Get all packets for desired protocols
        packets = elasticsearch.get_all_packets_by_protocol(protocol)
        all_packets = int(packets['hits']['total'])
        log_utils.display_message(logging.DEBUG, 'Number of all packets: %i' % all_packets)

        percentage = 0.0
        if all_packets != 0:
            percentage = 100.0 * invalid_packets / all_packets

        log_utils.display_message(logging.DEBUG, 'Percentage of invalid packets: %.2f%%' % percentage)

        protocol_report.update({'invalid packets': invalid_packets, 'all packets': all_packets, 'percentage': percentage})
        results.append({'protocol': protocol, 'results': protocol_report})

    report_dict = {'report': results, 'configuration': parameters}

    # Write report dictionary to file
    log_utils.display_message(logging.DEBUG, 'Writing results to report.json file.')
    reportFileName = build_json_filename()
    sys_utils.save_as_json(reportFileName, report_dict)

    if log_utils.response_to_question('Do you want to move analyzed packets to archive?', default='no'):
        # Reindex packets-* database as analyzed
        log_utils.display_message(logging.DEBUG, 'Archiving new packets.')
        elasticsearch.reindex_packets_as_analyzed()

        # Delete packets-* database
        log_utils.display_message(logging.DEBUG, 'Deleting analyzed packets.')
        elasticsearch.delete_packets_index()

    return reportFileName


def build_json_filename():
    '''
    A function which builds JSON report file name.

    Args:

    Returns:
        string: The file name of the JSON report

    Raises:

    '''

    return 'report_' + datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S') + '.json'

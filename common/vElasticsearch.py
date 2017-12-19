import json
import logging
import sys_utils
import yaml
from rest_api_utils import get_request, post_request, delete_request


class vElasticsearch(object):
    def __init__(self, node='localhost', port='9200'):
        self.url = 'http://' + node + ':' + port + '/'
        self.headers = {}
        self.data = {}


    def execute_yaml_query(self, path_to_yaml_file):
        '''
        A function to execute a query from a YAML file.

        Args:
            path_to_yaml_file (string): The file path of YAML file

        Returns:
            dictionary: The query results as dictionary

        Raises:

        '''

        # Getting YAML file
        logging.debug('Trying to execute query using %s file.' % path_to_yaml_file)

        url = self.url + '/packets-*/_search?pretty'
        payload = yaml.safe_load(sys_utils.read_file(path_to_yaml_file))

        response = post_request(url, json.dumps(payload), self.headers)
        resp_dict = yaml.safe_load(response.text)

        logging.debug('Post Response From Elasticsearch: \n%s' % response.text)
        return resp_dict


    def get_all_packets_by_protocol(self, protocol):
        '''
        A function to get all network packets from Elasticsearch DB by using protocol name.

        Args:
            protocol (string): The name of the protocol

        Returns:
            dictionary: The query results as dictionary

        Raises:

        '''

        # Getting Packets
        logging.debug('Trying to get all packets.')
        url = self.url + '/packets-*/_search?q=protocol:' + protocol + '&pretty'

        response = get_request(url, self.headers)
        resp_dict = yaml.safe_load(response.text)

        logging.debug('Get Response From Elasticsearch: \n%s' % response.text)
        return resp_dict


    def delete_packets_index(self):
        '''
        A function to clear packets indexes from Elasticsearch DB.

        Args:

        Returns:

        Raises:

        '''

        # Getting Packets
        logging.debug('Deleting all packets.')
        url = self.url + '/packets-*/'

        response = delete_request(url, self.headers)

        logging.debug('Delete Response From Elasticsearch: \n%s' % response.text)


    def reindex_packets_as_analyzed(self):
        '''
        A function to reindex packets index as analyzed index on Elasticsearch DB.

        Args:

        Returns:

        Raises:

        '''

         # Getting Packets
        logging.debug('Trying to reindex all packets as analyzed.')
        url = self.url + '/_reindex'
        payload = {'source': {'index': 'packets-*'}, 'dest': {'index': 'analyzed_packets'} }

        response = post_request(url, json.dumps(payload), self.headers)

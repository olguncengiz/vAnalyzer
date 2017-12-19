import json
import logging
import os
import sys_utils
from rest_api_utils import get_request, post_request, delete_request


class vOpenstack(object):
    def __init__(self):
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self.apiUrls = {}
        self.token = ''
        self.initialize()


    def initialize(self):
        try:
            payload = {'auth': {'tenantName': os.environ['OS_TENANT_NAME'], 'passwordCredentials': {'username': os.environ['OS_USERNAME'], 'password': os.environ['OS_PASSWORD']}}}
            url = os.environ['OS_AUTH_URL'] + '/tokens'

            response = post_request(url, json.dumps(payload), self.headers)
            resp_dict = json.loads(response.text)
            self.load_api_urls(resp_dict)

            self.token = str(resp_dict['access']['token']['id'])
            logging.debug('Token Id: %s' % self.token)
            self.headers.update({'X-Auth-Token': self.token, 'X-Project-Id': os.environ['OS_TENANT_NAME']})
        except KeyError as e:
            logging.error('KeyError: %s' % e)


    def load_api_urls(self, resp_dict):
        '''
        A function to load API URLs of Openstack environment.

        Args:
            resp_dict (dictionary): The dictionary which holds all API URLs of Openstack

        Returns:

        Raises:

        '''

        for endpoint in resp_dict['access']['serviceCatalog']:
            header = 'API_URL_' + str(endpoint['name']).upper()
            publicURL = str(endpoint['endpoints'][0]['publicURL'])
            if publicURL.endswith('/'):
                publicURL = publicURL[:-1]
            self.apiUrls[header] = publicURL
        logging.debug('API URLs: %s' % self.apiUrls)


    def get_instance_id(self, instanceName):
        '''
        A function to get instance ID using instance name.

        Args:
            instanceName (string): The name of the instance

        Returns:
            string: The ID of the instance

        Raises:

        '''

        instanceId = ''

        try:
            # Getting Servers
            logging.debug('Trying to fetch instance %s' % instanceName)

            url = self.apiUrls['API_URL_NOVA'] + '/servers/detail'

            response = get_request(url, self.headers)

            resp_dict = json.loads(response.text)

            logging.debug('GET Response From Nova: %s' % response.text)

            for d in resp_dict['servers']:
                if d['name'] == instanceName and d['status'] == 'ACTIVE':
                    instanceId = str(d['id'])
        except KeyError as e:
            logging.error('KeyError: %s' % e)

        logging.debug('Instance ID: %s' % instanceId)

        return instanceId


    def get_stack_id(self, stackName):
        '''
        A function to get stack ID using stack name.

        Args:
            stackName (string): The name of the stack

        Returns:
            string: The ID of the stack

        Raises:

        '''

        stackId = ''

        try:
            # Getting Servers
            logging.debug('Trying to fetch stack %s' % stackName)
            url = self.apiUrls['API_URL_HEAT'] + '/stacks'

            response = get_request(url, self.headers)

            resp_dict = json.loads(response.text)

            for d in resp_dict['stacks']:
                if d['stack_name'] == stackName:
                    stackId = str(d['id'])
        except KeyError as e:
            logging.error('KeyError: %s' % e)

        logging.debug('Stack ID: %s' % stackId)

        return stackId


    def create_stack(self, stackName, templateFile):
        '''
        A function to create a stack using a template file.

        Args:
            stackName (string): The name of the stack
            templateFile (string): The name of the template file

        Returns:

        Raises:

        '''

        logging.debug('Creating Stack %s' % stackName)
        template_file = sys_utils.read_file(templateFile)
        payload = {'stack_name': stackName, 'template': template_file}
        url = self.apiUrls['API_URL_HEAT'] + '/stacks'

        response = post_request(url, json.dumps(payload), self.headers)


    def delete_stack(self, stackName, stackId):
        '''
        A function to delete a stack using a stack name and ID.

        Args:
            stackName (string): The name of the stack
            stackId (string): The id of the stack

        Returns:

        Raises:

        '''

        logging.debug('Deleting Stack %s' % stackName)
        url = self.apiUrls['API_URL_HEAT'] + '/stacks/' + stackName + '/' + stackId

        response = delete_request(url, self.headers)


    def get_network_name(self, networkId):
        '''
        A function to get network name using network ID.

        Args:
            networkId (string): The id of the network

        Returns:
            string: The name of the network

        Raises:

        '''

        # Getting network name with networkId
        networkName = ''

        try:
            url = self.apiUrls['API_URL_NEUTRON'] + '/v2.0/networks/' + networkId

            response = get_request(url, self.headers)

            resp_dict = json.loads(response.text)

            networkName = str(resp_dict['network']['name'])

        except KeyError as e:
            logging.error('KeyError: %s' % e)

        logging.debug('Network Name: %s' % networkName)
        return networkName


    def get_instance_name_by_id(self, instanceId):
        '''
        A function to get instance name using instance ID.

        Args:
            instanceId (string): The id of the instance

        Returns:
            string: The name of the instance

        Raises:

        '''

        # Getting instance name with deviceID
        instanceName = ''

        try:
            url = self.apiUrls['API_URL_NOVA'] + '/servers/' + instanceId

            response = get_request(url, self.headers)

            resp_dict = json.loads(response.text)

            instanceName = str(resp_dict['server']['name'])

        except KeyError as e:
            logging.error('KeyError: %s' % e)

        logging.debug('Instance Name: %s' % instanceName)
        return instanceName


    def get_tap_device_id_list(self):
        '''
        A function to get tap device IDs.

        Args:

        Returns:
            dictionary: The key / value pairs of tap device IDs

        Raises:

        '''

        #Getting port list from Neutron
        tapDeviceIds = {}

        try:
            logging.debug('Getting tap device ID list.')

            url = self.apiUrls['API_URL_NEUTRON'] + '/v2.0/ports?device_owner=compute:nova'

            response = get_request(url, self.headers)

            resp_dict = json.loads(response.text)

            for port in resp_dict['ports']:
                instanceName = self.get_instance_name_by_id(port['device_id'])
                tapDeviceIds[instanceName] = 'tap%s' % str(port['id'][:11])

        except KeyError as e:
            logging.error('KeyError: %s' % e)

        logging.debug('Tap Device IDs: %s' % tapDeviceIds)
        return tapDeviceIds

    def get_all_vms(self):
        '''
        A function to get all virtual machines.

        Args:

        Returns:
            list: The list of virtual machines

        Raises:

        '''

        vmList = list()

        # Getting available VM list and protocol list
        try:
            logging.debug('Getting Available VM list.')

            url = self.apiUrls['API_URL_NOVA'] + '/servers/detail'

            response = get_request(url, self.headers)

            resp_dict = json.loads(response.text)

            for vm in resp_dict['servers']:
                vmList.append(str(vm['name']))
        except KeyError as e:
            logging.error('KeyError: %s' % e)

        logging.debug('VM List: %s' % vmList)

        return vmList


    def get_compute_hostname(self, instanceName):
        '''
        A function to get compute host name for an instance.

        Args:
            instanceName: The name of the instance

        Returns:
            string: Compute node name where instance is running

        Raises:

        '''

        computeNode = ''

        try:
            # Getting Servers
            url = self.apiUrls['API_URL_NOVA'] + '/servers/detail?name=' + instanceName

            response = get_request(url, self.headers)

            resp_dict = json.loads(response.text)

            for d in resp_dict['servers']:
                computeNode = str(d['OS-EXT-SRV-ATTR:host'])
        except KeyError as e:
            logging.error('KeyError: %s' % e)

        logging.debug('Compute Node: %s' % computeNode)
        return computeNode


    def get_instance_ip(self, instanceName, publicNetName):
        '''
        A function to get IP address of an instance.

        Args:
            instanceName: The name of the instance
            publicNetName: The name of the public network

        Returns:
            string: IP address of the instance

        Raises:

        '''

        instanceIp = ''

        try:
            # Getting Servers
            url = self.apiUrls['API_URL_NOVA'] + '/servers/detail?name=' + instanceName

            response = get_request(url, self.headers)
            logging.debug('Response Text: %s' % response.text)

            resp_dict = json.loads(response.text)
            logging.debug('Response Dict: %s' % resp_dict)

            for d in resp_dict['servers']:
                instanceIp = d['addresses'][publicNetName][1]['addr']

        except KeyError as e:
            logging.error('KeyError: %s' % e)

        logging.debug('Instance IP %s' % instanceIp)

        return instanceIp

import paramiko
import logging


class SshConnection(object):
    def __init__(self, host_, user_, pass_):
        self.host = host_
        self.username = user_
        self.password = pass_

        # Logging into device
        self.session = paramiko.SSHClient()
        self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connecting to the IP Adress using the passed credentials
        self.session.connect(self.host, username=self.username, password=self.password)
        self.connection = self.session.invoke_shell()

        # Setting instance attributes
        self.buff_size = 1024
        self.inner_ssh_connections = list()

        # Wait for cursor to appear for initial receive operation
        self.wait()


    def send(self, command, expected_output=''):
        '''
        A function to execute command on SSH Connection and return output.

        Args:
            command (string): The command to execute
            expected_output (string): The output which will be waited from the console

        Returns:
            string: The output from the console

        Raises:

        '''

        self.connection.send(command.strip() + '\n')
        return self.wait(expected_output)


    def wait(self, expected_output=''):
        '''
        A function which waits until the expected output condition occurs.

        Args:
            expected_output (string): The output which will be waited from the console

        Returns:
            string: The output from the console

        Raises:

        '''

        output = ''
        received = ''
        buff = ''
        found = False
        counter = 0
        while not found and counter < 5:
            received = self.connection.recv(self.buff_size)
            output += received
            if expected_output != '':
                if received.endswith(expected_output):
                    found = True
                elif received.endswith('$ ') or received.endswith('# '):
                    found = True
            else:
                if received.endswith('$ ') or received.endswith('# '):
                    found = True
            if buff == received:
                counter = counter + 1
            buff = received
        logging.debug('Received Output: %s' % output)
        return output


    def open_ssh_connection(self, host_, user_, pass_):
        '''
        A function which establishes SSH connection to another server.

        Args:
            host_ (string): The IP or name of the remote server
            user_ (string): The user name of the server
            pass_ (string): The password of the user

        Returns:

        Raises:

        '''

        command = 'ssh ' + user_ + '@' + host_
        output = self.send(command, '\'s password: ')
        if output.endswith('\'s password: '):
            self.send(pass_)
        self.inner_ssh_connections.append(host_)


    def close_last_ssh_connection(self):
        '''
        A function which closes last SSH connection.

        Args:

        Returns:

        Raises:

        '''

        if len(self.inner_ssh_connections) != 0:
            self.send('exit')
            del self.inner_ssh_connections[-1]


    def get_last_ssh_connection(self):
        '''
        A function which peeks last SSH connection.

        Args:

        Returns:

        Raises:

        '''

        if len(self.inner_ssh_connections) != 0:
            return self.inner_ssh_connections[-1]
        else:
            return ''


    def close_all_ssh_connections(self):
        '''
        A function which closes all SSH connections.

        Args:

        Returns:

        Raises:

        '''

        self.send('~.')
        del self.inner_ssh_connections[:]

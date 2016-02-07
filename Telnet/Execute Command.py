import telnetlib
import re
import traceback
import time
import qualipy.api.cloudshell_api as CA
import json
import os
import errno
import qualipy.scripts.cloudshell_scripts_helpers as CS

serverAddress = CS.get_connectivity_context_details().server_address
adminUser = CS.get_connectivity_context_details().admin_user
adminPass = CS.get_connectivity_context_details().admin_pass
domain = CS.get_reservation_context_details().domain

#get the reservation id
resID = CS.get_reservation_context_details().id
#Set the ip of the host from the resource
host = CS.get_resource_context_details().address
#Set the user name of the user from the resource
atts = CS.get_resource_context_details().attributes
# Get the username out of the resource attributes
username = atts['User']

# Get the password out of the resource attributes
passwEn = atts['Password']

#Decrypt the password
session = CA.CloudShellAPISession(serverAddress,adminUser,adminPass,domain)
password = session.DecryptPassword(passwEn).Value

class TelnetManager:
    def __init__(self, username, password, host, port=23,
                 timeout=60, newline='\r'):
        self._handler = telnetlib.Telnet()

        self._username = username.encode('ascii')
        self._password = password.encode('ascii')

        self._host = host
        self._port = port

        self._timeout = timeout
        self._newline = newline

        self._more_line_re_str = '-- {0,1}[Mm]ore {0,1}--'
        self._more_line_pattern = re.compile(self._more_line_re_str)

        self.prompt = ''

    def connect(self, expected_str=''):
        data = ''
        if expected_str:
            self._prompt = expected_str

        try:
            self._handler.open(self._host, self._port, self._timeout)

            if self._username != None:
                data += self._readOutBuffer('([Ll]ogin|[Uu]sername):', self._timeout)
                self._handler.write(self._username + self._newline)

            if self._password != None:
                data += self._readOutBuffer('[Pp]assword:', self._timeout)
                self._handler.write(self._password + self._newline)
            data += self._readOutBuffer(self._prompt, self._timeout)

        except Exception, err:
            error_str = "Exception: " + str(err) + '\n'

            error_str += '-' * 60 + '\n'
            error_str += traceback.format_exc()
            error_str += '-' * 60

            raise Exception('Telnet Manager', error_str)

        return data

    def disconnect(self):
        self._handler.close()

    def sendCommand(self, command, re_string='', timeout=None):
        if command is not None:
            self._handler.write(command + self._newline)

        return self._readOutBuffer(re_string, timeout)

    def _readOutBuffer(self, re_string='', timeout=None):
        timeout = timeout if timeout else self._timeout

        expect_list = [re_string, self._more_line_re_str]
        input_buffer = ''
        try:
            if len(re_string) == 0:

                input_buffer = self._handler.read_all()
            else:
                response_tuple = self._readRecvData(expect_list, timeout)
                input_buffer += response_tuple[0]

                while response_tuple[1] != None:
                    response_tuple = self._readRecvData(expect_list, timeout)
                    input_buffer += response_tuple[0]

        except Exception, err:
            error_str = "Exception: " + str(err) + '\n'
            import traceback, sys

            error_str += '-' * 60 + '\n'
            error_str += traceback.format_exc()
            error_str += '-' * 60

            raise Exception('Telnet Manager', error_str)

        return self._normalizeBuffer(input_buffer)

    def _readRecvData(self, expect_list, timeout):
        response_tuple = self._handler.expect(expect_list, timeout)
        response = response_tuple[2]

        more_match = self._more_line_pattern.search(response)
        if more_match != None:
            self._handler.write(self._newline)
            more_pos = more_match.span()
            response = response[0:more_pos[0]] + response[more_pos[1]:]

        return (response, more_match)

    def _normalizeBuffer(self, input_buffer):
        """
        Method for clear color fro input_buffer and special characters
        """

        color_pattern = re.compile('\[([0-9]+;)*[0-9]+m|\[[0-9]+m|\[[A-Z]m*|\[[A-Z]{0,1}m|\b|\r|' + chr(27))            # 27 - ESC character

        result_buffer = ''
        match_iter = color_pattern.finditer(input_buffer)

        current_index = 0
        for match_color in match_iter:
            match_range = match_color.span()
            result_buffer += input_buffer[current_index:match_range[0]]
            current_index = match_range[1]

        result_buffer += input_buffer[current_index:]

        return result_buffer

telnet_manager = TelnetManager(username, password, host)

prompt = '[>$#]$'
out = telnet_manager.connect(prompt)

prompt = r':\\[A-Za-z0-9\._\-\\]*> {0,1}$'
out = telnet_manager.sendCommand(os.environ['Command'], prompt)

telnet_manager.disconnect()

print out

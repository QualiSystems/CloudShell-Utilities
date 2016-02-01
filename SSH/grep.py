import subprocess
import sys
import paramiko
import qualipy.api.cloudshell_api
import json
import os

Reservation_Context = os.environ['RESERVATIONCONTEXT']
Reservation_Context_Json = json.loads(Reservation_Context)

Quali_Connectivity_Context = os.environ['QUALICONNECTIVITYCONTEXT']
Quali_Connectivity_Context_Json = json.loads(Quali_Connectivity_Context)

Resource_context = os.environ['RESOURCECONTEXT']
Resource_context_Json = json.loads(Resource_context)

serverAddress = Quali_Connectivity_Context_Json['serverAddress']
adminUser = Quali_Connectivity_Context_Json['adminUser']
adminPass = Quali_Connectivity_Context_Json['adminPass']
domain = Reservation_Context_Json['domain']

session = qualipy.api.cloudshell_api.CloudShellAPISession(serverAddress,adminUser,adminPass,domain)

#get the reservation id
resID=Reservation_Context_Json['id']
#Set the ip of the host from the resource
Host = Resource_context_Json['address']
#Set the user name of the user from the resource
atts =Resource_context_Json['attributes']
user = atts['User']
#get the password of the user from the resource
passwEn = atts['Password']
#Decrypt the password
passw = session.DecryptPassword(passwEn).Value
#SSH session conenction
ssh = paramiko.SSHClient()


#Openning SSH session from the resource attributes details
def _OpenSSH():
    #Open paramiko sshclient
    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ConnectionDetails = ssh.connect(Host, username=user, password=passw)
    except:
        print 'Connection error has occured, check the connection details and try again: {} {} {}'.format(Host,user,passw)


def _CloseSSH():
    ssh.close()

# #1 End User provides 2 parameters to the command. The first parameter is a path of a file, the second parameter is a string.
# #  The 'grep' command will search the string inside the file in the given path
# #  and return the lines where the string is found as an output
#
def grepCommand(Search, InFile):
    #Calls a method to open the SSH conection with the machine
    _OpenSSH()
    #stdin - sending the command,
    #stdout - getting the output from the command
    #stderr - getting errors

    stdin, stdout, stderr = ssh.exec_command('grep {} {}'.format(Search,InFile))

    output = stdout.read()
    if output == '':
        print('The command: "grep {} {}'.format(Search,InFile) + '" returned no results')
        #Send the output to a method that will print the output and close the session
    print(output)
    _CloseSSH()

grepCommand(os.environ['SearchString'],os.environ['WithInFile'])

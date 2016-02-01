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

session = qualipy.api.cloudshell_api.CloudShellAPISession(serverAddress,adminUser,adminPass,domain)


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

# The End user provides the command as parameter to the script.
# The script will open SSH session teh Command will be executed and the session will be closed.

def executeCommand(command):
    #Calls a method to open the SSH conection with the machine
    _OpenSSH()
    #stdin - sending the command,
    #stdout - getting the output from the command
    #stderr - getting errors
    stdin, stdout, stderr = ssh.exec_command(command)
    #Send the output to a method that will print the output and close the session
    print (stdout.read())
    _CloseSSH()

executeCommand(os.environ['Command'])

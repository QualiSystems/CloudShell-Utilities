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


#Get connection details
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

#define the CloudShellAPI session
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

def ExecuteProcedure(filePath):
    _OpenSSH()
    #get the strings from the text file
    with open (filePath, "r") as myfile:
        commands = myfile.readlines()
    for line in commands:
        #prints the commands names and their outputs afterwards
        print line
        stdin, stdout, stderr = ssh.exec_command(line)
        print stdout.read()+'\n'
    _CloseSSH()
    return

ExecuteProcedure(os.environ['FilePath'])

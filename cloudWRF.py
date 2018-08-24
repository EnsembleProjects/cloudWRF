import f90nml
import StringIO

import paramiko
import time
import select
import sys


#class to represent experiment configuration
class cloudWRF:

    #generate then upload the namelist
    def uploadNameList(self,path):

      #create a virtual file
      self.output = StringIO.StringIO()
      #write the contents of the namelist to it
      self.namelist.write(self.output)
      #write to remote server
      self.writeRemoteFile(self.output,path)
      #destroy virtual file
      self.output.close()

    #WRITE FILE OVER SSH
    def writeRemoteFile(self,fileObj,remotePath):

      #setup ssh connection to remote server
      ssh = paramiko.SSHClient()
      #ignore key errors
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(self.server, username=self.username, password=self.password)
      #go to start of namelist content
      fileObj.seek(0)
      #upload
      ftp_client=ssh.open_sftp()
      ftp_client.putfo(fileObj,remotePath)
      ftp_client.close()

      print "Namelist uploaded, closing SSH connection"
      ssh.close()

    #runs any SSH command... needs to be limited to running wrf?
    def runWRF(self,cmd_to_execute):

      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(self.server, username=self.username, password=self.password)
      ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
      # Wait for the command to terminate
      while not ssh_stdout.channel.exit_status_ready():
          # Only print data if there is data to read in the channel
          if ssh_stdout.channel.recv_ready():
             rl, wl, xl = select.select([ssh_stdout.channel], [], [], 0.0)
             if len(rl) > 0:
                  # Print data from stdout
                  print ssh_stdout.channel.recv(1024),
            
      print "Command done, closing SSH connection"
      ssh.close()


    def __init__(self, server="server", username="un", password="pw", sourceNML='namelist.input'):
      self.namelist = f90nml.read(sourceNML)
      self.server = server
      self.username = username
      self.password = password





if __name__ == "__main__":

    #Create an instance for your experiment
    myExperiment = cloudWRF()
    #can also load a specified namelist source using:
    #myExperiment = cloudWRF("path to input namelist")

    #change some experiment parameters
    myExperiment.namelist['bdy_control']['spec_zone'] = 1000

    #CODE TO CREATE CLOUD INFRASTRUCTURE GOES HERE, RETURNING SSH CREDENTIALS

    myExperiment.server = "SERVER ADDRESS"
    myExperiment.username = "USERNAME"
    myExperiment.password = "PASSWORD"


    #Generate and upload namelist file to server, with remote path and filename passed
    myExperiment.uploadNameList('test5.txt')

    #run WRF, actually runs any ssh command... careful!
    myExperiment.runWRF("echo 'hello world!' | cat > hello.txt")
    myExperiment.runWRF("ls")




    

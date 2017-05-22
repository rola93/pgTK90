import paramiko
import sys
import mail

## EDIT SSH DETAILS ##
from mail import send_mail_alert

SSH_ADDRESS = "0.tcp.ngrok.io"
SSH_USERNAME = "pgtk90"
SSH_PASSWORD = "spectrumROOT"
SSH_COMMAND = "echo 'Hello World!'"
SSH_PORT = 18157

## CODE BELOW ##

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


ssh_stdin = ssh_stdout = ssh_stderr = None

try:
    ssh.connect(SSH_ADDRESS, username=SSH_USERNAME, password=SSH_PASSWORD, port=SSH_PORT)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(SSH_COMMAND)
except Exception as e:
    # sys.stderr.write("SSH connection error: {0}".format(e))
    send_mail_alert("SSH connection error: {0}".format(e) + "\n\nPosiblemente se haya caido la maquina :/")


if ssh_stdout:
    # sys.stdout.write(ssh_stdout.read())
    send_mail_alert("LLego todo bien, comentar esta linea luego de probar.")
if ssh_stderr:
    send_mail_alert(ssh_stderr.read() + "\n\nPosiblemente se haya caido la maquina :/")
    # sys.stderr.write(ssh_stderr.read())
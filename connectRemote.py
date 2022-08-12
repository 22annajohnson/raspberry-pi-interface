"""
    Author: Anna Johnson
    Date:  06/30/2022
    Version: 1
    Description: SSH into pis
"""

import paramiko, os, datetime
import makeVideo

rn = datetime.datetime.now()
current = os.getcwd()

def connect(ip):
    port, user, pw = 22, "pi", "duck236"
    # print(user, pw, port, ip)
    screenPlayer = "/home/pi/ScreenPlayer"
    manual = f"{screenPlayer}/ManualUpload"
    auto = f"{screenPlayer}/AutoUpload"
    archive = f"{screenPlayer}/Archive"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,port,user,pw)
 
    sftp = ssh.open_sftp()

    # stdin,stdout,stderror=ssh.exec_command('cd /home/pi/ScreenPlayer ; ls')
    # print(stdout.readlines())
    return sftp
    # sftp.mkdir("/home/pi/ScreenPlayer/Archive")


def downloadFiles(ip, remote):
    sftp = connect(ip)
    files = fileList(remote)
    for file in files:
        sftp.get(f"{remote}/{file}", f"{current}/downloaded/{file}")  
    extracted = os.listdir(f"{current}/downloaded")
    print(f"Files Extracted from {ip}: {extracted}")

def uploadFile(ip, local, remote):
    # print(ip, "\n", local, "\n", remote)
    sftp = connect(ip)
    try:
        file = local.split("\\")[-1]

        sftp.put(local, remote)
        print(f"\n{file} successfully uploaded to {remote}")
    except:
        print("Error")

def fileList(ip, remote):
    sftp = connect(ip)
    files = []
    for location in remote:
        files.append(sftp.listdir(location))
    
    return files

def slideShow(ip):
    sftp = connect(ip)




# print(fileList("10.10.0.208", ["/home/pi/ScreenPlayer/ManualUpload"]))

# uploadFile("10.10.0.200", "C:/Users/22ann/Documents/RPi_Interface/new.mp4", "/home/pi/ScreenPlayer/AutoUpload/new.mp4")
# images = []
# for image in os.listdir(current+"\images"):
#     images.append(current+"\images\\"+image)
# time = (str(rn.month)+str(rn.day)+str(rn.year)+"_"+str(rn.hour)+"-"+str(rn.minute)+"-"+str(rn.second))
# makeVideo.compile(images, [2, 2, 2, 2, 2, 2], time) 
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

def connect(ip, option = []):
    port, user, pw = 22, "pi", "duck236"
    screenPlayer = "/home/pi/ScreenPlayer"
    manual = f"{screenPlayer}/ManualUpload"
    auto = f"{screenPlayer}/AutoUpload"
    archive = f"{screenPlayer}/Archive"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,port,user,pw)
 
    # file = "test.mp4"
    # sftp.rename(f"/home/pi/ScreenPlayer/AutoUpload/{file}", f"/home/pi/ScreenPlayer/Archive/{file}")
    

    # if len(option) > 0:
    #     command = (f"cd /home/pi/ScreenPlayer; sudo chmod -R 0777 ./AutoUpload; sudo chmod -R 0777 ./Archive; echo mv {option[0]} {option[1]}")
    #     stdin, stdout, stderr=ssh.exec_command(command)
    #     print(stdout.readlines(), stderr.readlines())
    #     print(option[1], option[2])
    #     command = ("sudo chmod 777")
    #     ssh.exec_command(command)
    sftp = ssh.open_sftp()
    if option == ["ssh"]:
        return sftp, ssh
    else:
        return sftp

def downloadFiles(ip, remote=None, fileList=None):
    sftp = connect(ip)
    if fileList == None:
        files = fileList(ip, remote)
        for file in files:
            sftp.get(f"{remote}/{file}", f"{current}/downloaded/{file}")  
        extracted = os.listdir(f"{current}/downloaded")
        print(f"Files Extracted from {ip}: {extracted}")
    else:
        for file in fileList:
            fileName = file.split("/")[-1]
            sftp.get(f"{file}", f"{current}/downloaded/{fileName}")
    sftp.close()

def uploadFile(ip, local, remote):
    # print(ip, "\n", local, "\n", remote)
    sftp = connect(ip)
    try:
        file = local.split("/")[-1]

        sftp.put(local, remote)

        print(f"\n{file} successfully uploaded to {remote}")
    except:
        print("Error")
    sftp.close()

def archiveFile(ip, originalFile, workingDir):
    originalLocation = f"/home/pi/ScreenPlayer/AutoUpload/{originalFile}"
    newLocation = f"/home/pi/ScreenPlayer/Archive/{originalFile}"

    sftp = connect(ip)
    print(originalLocation)
    print(ip)
    print(sftp.listdir("/home/pi/ScreenPlayer/AutoUpload/"))
    sftp.get(originalLocation, f"{workingDir}/downloaded/{originalFile}")
    sftp.remove(originalLocation)
    sftp.put(f"{workingDir}/downloaded/{originalFile}", newLocation)
    os.remove(f"{workingDir}/downloaded/{originalFile}")
  

def fileList(ip, remote, option = []):
    print(remote)
    if option == ["ssh"]:
        sftp, ssh = connect(ip, option=[option[0]])
    else:
        sftp = connect(ip)
    files = []
    for location in remote:
        files.append(sftp.listdir(location))

    if option == ["ssh"]:
        return files, sftp, ssh
    return files, sftp

def slideShow(ip, option = ""):
    workingDir = os.getcwd()
    remote = ["/home/pi/ScreenPlayer/AutoUpload", "/home/pi/ScreenPlayer/ManualUpload"]
    directoryList, sftp, ssh = fileList(ip, remote, option=["ssh"])

    if option == "kill":
        print(option, ip)
        remote = "/home/pi/ScreenPlayer/SlideShow"
        print(remote)
        directoryList = sftp.listdir("/home/pi/ScreenPlayer/SlideShow")
        
        for file in directoryList:
            sftp.remove(f"/home/pi/ScreenPlayer/SlideShow/{file}")
        directoryList = os.listdir(f"{workingDir}\\downloaded")
        for file in directoryList:
            os.remove(f"{workingDir}\\downloaded\\{file}")

        command = f"killall -u pi"
        (stdin, stdout, stderr) = ssh.exec_command(command)
        return

    photoList = []
    for directoryNumber, directory in enumerate(directoryList):
        for file in directoryList[directoryNumber]:
            if directoryNumber == 0:
                directoryName = "AutoUpload"
            else: 
                directoryName = "ManualUpload"
            photoList.append(f"/home/pi/ScreenPlayer/{directoryName}/{file}")
    
    downloadFiles(ip, fileList=photoList)
    downloadedFiles = os.listdir(f"{workingDir}/downloaded")
    downloadedList = []
    for file in downloadedFiles:
        filePath = f"{workingDir}/downloaded/{file}"
        print(f"/home/pi/ScreenPlayer/SlideShow/{file}", filePath)
        sftp.put(filePath, f"/home/pi/ScreenPlayer/SlideShow/{file}")
    print("before command")
    command = f"export DISPLAY=:0 && feh -Y -x -q -D 5 -B black -F -Z -z -r /home/pi/ScreenPlayer/SlideShow"
    print(command)
    # command = 'ls -l'
    (stdin, stdout, stderr) = ssh.exec_command(command)
    print(stdout)



# ip = "10.10.0.200"
# port, user, pw = 22, "pi", "duck236"
# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect(ip,port,user,pw)

# command = f"export DISPLAY=:0 && feh -Y -x -q -D 5 -B black -F -Z -z -r /home/pi/ScreenPlayer/SlideShow"

# (stdin, stdout, stderr) = ssh.exec_command(command)  


# def slideShow(ip, option = ""):
    
    
#     remote = ["/home/pi/ScreenPlayer/AutoUpload", "/home/pi/ScreenPlayer/ManualUpload"]
#     directoryList, sftp, ssh = fileList(ip, remote, option=["ssh"])
#     photoList = []
#     durationList = []

#     if option == "kill":
#         command = f"killall -u pi"
#         (stdin, stdout, stderr) = ssh.exec_command(command)
#         return

#     for directoryNumber, directory in enumerate(directoryList):
#         for file in directoryList[directoryNumber]:
#             if directoryNumber == 0:
#                 directoryName = "AutoUpload"
#             else: 
#                 directoryName = "ManualUpload"
#             durationList.append(5)
#             photoList.append(f"/home/pi/ScreenPlayer/{directoryName}/{file}")
    
#     downloadFiles(ip, fileList=photoList)
#     workingDir = os.getcwd()
#     downloadedFiles = os.listdir(f"{workingDir}/downloaded")
#     downloadedList = []
#     for file in downloadedFiles:
#         downloadedList.append(f"{workingDir}/downloaded/{file}")
#     print(downloadedList)

#     video = makeVideo.compile(downloadedList, durationList)
#     file = video.split("\\")[-1]    
#     sftp.put(video, f"/home/pi/ScreenPlayer/SlideShow/{file}")
#     command = f"omxplayer --loop --no-osd ~/ScreenPlayer/SlideShow/{file}"
#     (stdin, stdout, stderr) = ssh.exec_command(command)



#     for file in downloadedList:
#         os.remove(file)



# connect("10.10.0.200")
# print(fileList("10.10.0.208", ["/home/pi/ScreenPlayer/ManualUpload"]))

# uploadFile("10.10.0.200", "C:/Users/22ann/Documents/RPi_Interface/new.mp4", "/home/pi/ScreenPlayer/AutoUpload/new.mp4")
# images = []
# for image in os.listdir(current+"\images"):
#     images.append(current+"\images\\"+image)
# time = (str(rn.month)+str(rn.day)+str(rn.year)+"_"+str(rn.hour)+"-"+str(rn.minute)+"-"+str(rn.second))
# makeVideo.compile(images, [2, 2, 2, 2, 2, 2], time) 
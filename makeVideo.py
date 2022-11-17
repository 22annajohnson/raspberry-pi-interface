"""
    Author: Anna Johnson
    Date:  06/28/2022
    Version: 1
    Description: Turns images into a mp4 file
"""
import os, datetime

current = os.getcwd()


# p = ['C:/Users/22ann/Documents/RPi_Interface/images/test2.jpeg', 'C:/Users/22ann/Documents/RPi_Interface/images/test1.jpg', 'C:/Users/22ann/Documents/RPi_Interface/images/test3.jpg'] 
# d = ['3', '3', '3']


def compile(p, d):
    rn = datetime.datetime.now()
    time = (str(rn.month)+"_"+str(rn.day)+"_"+str(rn.year)+"_"+str(rn.hour)+"-"+str(rn.minute)+"-"+str(rn.second))

    def photos(photoList, durations):
        acceptedFormats = ["jpg", "jpeg", "png"]
        file = open("./resources/photos.txt", "w")
        for image in range(0, len(photoList), 1):
            if photoList[image].split(".")[-1] not in acceptedFormats:
                continue
            file.write(f"file '{photoList[image]}'\n")
            file.write(f"duration {int(durations[image])}\n")
        file.write(f"file '{photoList[image]}'")

    photos(p, d)
    

    # os.system(f"""ffmpeg  -f concat -safe 0 -i "{current}\\resources\\photos.txt" -vsync vfr -filter:v fps=fps=60 -pix_fmt yuv420p "{current}\\videos\\{time}.mp4""")
    os.system(f"""ffmpeg -loglevel panic -f concat -safe 0 -i "{current}\\resources\\photos.txt" -vf "crop=trunc(iw/2)*2:trunc(ih/2)*2" -vsync vfr -pix_fmt yuv420p -vcodec jpeg "{current}\\videos\\temp.mp4""")
    print("here")
    os.system(f"""ffmpeg  -i "{current}\\videos\\temp.mp4" -filter:v fps=fps=60 {current}\\videos\\{time}.mp4""")
    os.remove(f"{current}\\videos\\temp.mp4")
    # os.system(f"""ffmpeg -f concat -safe 0 -i "{current}\\resources\\photos.txt" -vf "crop=trunc(iw/2)*2:trunc(ih/2)*2, fps=60, format=yuv420p" -vsync vfr "{time}.mp4""")
    fileName = f"{current}\\videos\\{time}.mp4"
    return fileName
# compile(p="", d="")
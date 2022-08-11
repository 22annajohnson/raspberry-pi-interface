"""
    Author: Anna Johnson
    Date:  06/28/2022
    Version: 1
    Description: Turns images into a mp4 file
"""
import os, datetime

current = os.getcwd()

def compile(p, d):
    rn = datetime.datetime.now()
    time = (str(rn.month)+str(rn.day)+str(rn.year)+"_"+str(rn.hour)+"-"+str(rn.minute)+"-"+str(rn.second))

    def photos(photoList, durations):

        file = open("./resources/photos.txt", "w")
        for image in range(0, len(photoList), 1):
            file.write(f"file '{photoList[image]}'\n")
            file.write(f"duration {durations[image]}\n")
        file.write(f"file '{photoList[image]}'")

    photos(p, d)
    print(time)
    os.system(f"""ffmpeg -f concat -safe 0 -i "{current}\\resources\\photos.txt" -vf "crop=trunc(iw/2)*2:trunc(ih/2)*2" -vsync vfr -pix_fmt yuv420p "{time}.mp4""")


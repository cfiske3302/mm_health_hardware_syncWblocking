from PIL import Image
import numpy as np
import os
import imageio
import cv2
import sys

sys.path.insert(0, r"C:\Users\111\Desktop\mmhealth_2\sensors")
from config import *

config = configparser.ConfigParser()
config.read( r"C:\Users\111\Desktop\mmhealth_2\sensors\configs\sensors_config.ini")

# input_filepath = str(sys.argv[1])
def tiff_to_avi(input_filepath):
    path = os.path.dirname(input_filepath)
    filename_ext = os.path.basename(input_filepath)
    filename = os.path.splitext(filename_ext)[0]
    # ext = os.path.splitext(filename_ext)[1]
    # print(ext)
    output_filepath = os.path.join(path, filename + "_avi.avi")

    sensor_type = filename[:2]
    if(sensor_type == "ni"):
        sensor_type = "nir"
    elif(sensor_type == "po"):
        sensor_type  = "polarized"
    elif(sensor_type == "rg"):
        sensor_type = "rgbd"
    elif(sensor_type == "th"):
        sensor_type = "thermal"
    else: 
    # elif (sensor_type == "uv"):
        pass
    # elif(sensor_type == "rf"):
    #     pass
    # elif(sensor_type == "au"):
    #     sensor_type = "audio"

    width = config.getint(sensor_type, "width") 
    height = config.getint(sensor_type, "height") 
    fps = config.getint(sensor_type, "fps")

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video = cv2.VideoWriter(output_filepath, fourcc, fps, (width, height))

    imarray = imarray = imageio.volread(input_filepath) 
    print(imarray.shape) 
    # imarray = imarray.astype("uint8") #uint8
    NUM_FRAMES = imarray.shape[0]
    for i in range (NUM_FRAMES):
        frame = imarray[i]
        if (sensor_type == "nir" or sensor_type == "polarized" or sensor_type == "thermal"):
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        video.write(frame)

    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    input_filepath = "C:\Temp\mmhealth_data\testing6\polarized_1.tiff"
    tiff_to_avi(input_filepath)
    
# im = Image.open(filename)
# im.show()
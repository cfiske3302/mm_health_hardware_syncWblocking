from PIL import Image
import numpy as np
import os
import imageio
import cv2
import sys

input_name = str(sys.argv[1])
output_name = str(sys.argv[2])
width = int(sys.argv[3])
height = int(sys.argv[4])
fps = int(sys.argv[5])

filepath = r"C:\Temp\mmhealth_data\data"
filename = os.path.join(filepath, input_name + ".tiff")

fourcc = cv2.VideoWriter_fourcc(*'XVID')
filename2 = os.path.join(filepath, output_name + ".avi")
video = cv2.VideoWriter(filename2, fourcc, fps, (width, height))

if __name__ == "__main__":
    imarray = imarray = imageio.volread(filename) 
    print(imarray.shape) 
    # imarray = imarray.astype("uint8") #uint8
    NUM_FRAMES = imarray.shape[0]
    for i in range (NUM_FRAMES):
        frame = imarray[i]
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        video.write(frame)

video.release()
cv2.destroyAllWindows()

im = Image.open(filename)
im.show()
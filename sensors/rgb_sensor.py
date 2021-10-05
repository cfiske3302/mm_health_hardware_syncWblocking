# rgb sensor

import imageio
import numpy as np
import sys
import os

from config import *
from sensor import Sensor

class RGB_Sensor(Sensor):

    def __init__(self, filename : str, foldername : str = "data"):
        super().__init__(filename=filename, foldername=foldername)

        self.sensor_type = "rgb_camera"
        
        #initialize capture
        self.format = ".tiff"
        self.fps     = config.getint("rgb", "fps")
        self.width   = config.getint("rgb", "width") #not setting
        self.height  = config.getint("rgb", "height") #not setting
        self.channels = config.getint("rgb", "channels") #not setting
        self.compression = config.getint("rgb", "compression")
        self.counter = 0

        kargs = { 'fps': self.fps, 'ffmpeg_params': ['-s',str(self.width) + 'x' + str(self.height)] }
        self.reader = imageio.get_reader('<video1>', format = "FFMPEG", dtype = "uint8", **kargs)

    def __del__(self) -> None:
        self.release_sensor()
        print("Released {} resources.".format(self.sensor_type))
        # print(self.filepath)
        
    def acquire(self, acquisition_time : int) -> bool:
        NUM_FRAMES = self.fps*acquisition_time  # number of images to use in AVI file
        frames = np.empty((NUM_FRAMES, self.height, self.width, self.channels), np.dtype('uint16'))

        for im in self.reader:
            if (self.counter < NUM_FRAMES):
                if ((self.counter != 0)):
                    if ( np.max(im  - frames[self.counter-1]) != 0 ):
                        frames[self.counter] = im # Reads 3 channels, but each channel is identical (same pixel info)
                        self.record_timestamp()
                        self.counter += 1
                else:
                    frames[self.counter] = im # Reads 3 channels, but each channel is identical (same pixel info)
                    self.counter += 1
            else:
                break

        imageio.mimwrite(self.filepath + self.format, frames, bigtiff=True)

        self.save_timestamps()
        self.time_stamps = []

    def release_sensor(self) -> bool:
        pass

    def print_stats(self):
        print("_____________ RGB Camera Specifications _____________")
        print("FPS = {} f/s".format(self.fps))
        print("Resolution = {} x {}".format(self.width, self.height))

# #To test code, run this file.
if __name__ == '__main__':
    rgb_cam = RGB_Sensor(filename="rgb_1")
    rgb_cam.acquire(acquisition_time=5)
    rgb_cam.print_stats()
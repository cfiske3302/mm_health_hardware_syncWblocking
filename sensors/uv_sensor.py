# uv sensor

import imageio
import numpy as np
import sys
import os

from config import *
from sensor import Sensor

class UV_Sensor(Sensor):

    def __init__(self, filename : str, foldername : str = "data"):
        super().__init__(filename=filename, foldername=foldername)

        self.sensor_type = "uv_camera"
        
        #initialize capture
        self.format = ".tiff"
        self.fps     = config.getint("uv", "fps")
        self.width   = config.getint("uv", "width") #not setting
        self.height  = config.getint("uv", "height") #not setting
        self.channels = config.getint("uv", "channels") #not setting
        self.compression = config.getint("uv", "compression")
        self.counter = 0

        kargs = { 'fps': self.fps, 'ffmpeg_params': ['-s',str(self.width) + 'x' + str(self.height)] }
        self.reader = imageio.get_reader('<video0>', format = "FFMPEG", dtype = "uint8", **kargs)

    def __del__(self) -> None:
        self.release_sensor()
        print("Released {} resources.".format(self.sensor_type))
        
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

        imageio.mimwrite(self.filepath + self.format, frames)

        self.save_timestamps()
        self.time_stamps = []

    def release_sensor(self) -> bool:
        pass

    def print_stats(self):
        print("_____________ UV Camera Specifications _____________")
        print("FPS = {} f/s".format(self.fps))
        print("Resolution = {} x {}".format(self.width, self.height))

# #To test code, run this file.
if __name__ == '__main__':
    uv_cam = UV_Sensor(filename="uv_1")
    uv_cam.acquire(acquisition_time=5)
    uv_cam.print_stats()
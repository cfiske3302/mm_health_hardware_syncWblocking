# thermal sensor

import imageio
import numpy as np
import sys
import os

from config import *
from sensor import Sensor

class Thermal_Sensor(Sensor):

    def __init__(self, filename : str, foldername : str = "data"):
        super().__init__(filename=filename, foldername=foldername)

        self.sensor_type = "thermal_camera"
        
        #initialize capture
        self.format = ".tiff"
        self.fps     = config.getint("thermal", "fps")
        self.width   = config.getint("thermal", "width") #not setting
        self.height  = config.getint("thermal", "height") #not setting
        self.channels = config.getint("thermal", "channels") #not setting
        self.compression = config.getint("thermal", "compression")
        # self.acquisition_time = 5
        self.counter = 0

        kargs = { 'fps': self.fps, 'ffmpeg_params': ['-s',str(self.width) + 'x' + str(self.height)] }
        self.reader = imageio.get_reader('<video0>', format = "FFMPEG", dtype = "uint16", **kargs)

    def __del__(self) -> None:
        self.release_sensor()
        print("Released {} resources.".format(self.sensor_type))
        # print(self.filepath)
        
    def acquire(self, acquisition_time : int) -> bool:
        NUM_FRAMES = self.fps*acquisition_time  # number of images to use in AVI file
        frames = np.empty((NUM_FRAMES, self.height, self.width), np.dtype('uint16'))

        for im in self.reader:
            if (self.counter < NUM_FRAMES):
                if ((self.counter != 0)):
                    if ( np.max(im[:,:,0]  - frames[self.counter-1]) != 0 ):
                        frames[self.counter] = im[:,:,0] # Reads 3 channels, but each channel is identical (same pixel info)
                        self.record_timestamp()
                        self.counter += 1
                else:
                    frames[self.counter] = im[:,:,0] # Reads 3 channels, but each channel is identical (same pixel info)
                    self.counter += 1
            else:
                break

        imageio.mimwrite(self.filepath + self.format, frames, bigtiff=True)

        self.save_timestamps()
        self.time_stamps = []

    def release_sensor(self) -> bool:
        #Release camera
        pass

    def print_stats(self):
        print("_____________ Thermal Camera Specifications _____________")
        print("FPS Requested = {} f/s".format(self.fps))
        print("FPS Recorded = {} f/s".format(int(self.reader.get_meta_data()['fps'])))
        print("Resolution = {} x {}".format(self.width, self.height))

# #To test code, run this file.
if __name__ == '__main__':

    thermal_cam = Thermal_Sensor(filename="thermal_1")
    thermal_cam.acquire(acquisition_time=5)
    thermal_cam.print_stats()
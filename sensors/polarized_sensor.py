# polarized sensor

import sys
import os
import PySpin
import matplotlib.pyplot as plt
import numpy as np
import cv2
import imageio

from sensor import Sensor
from config import *

class Polarized_Sensor(Sensor):

    def __init__(self, filename : str, foldername : str = "individual_sensor_test"):
        super().__init__(filename=filename, foldername=foldername)

        self.sensor_type = "polarized_camera"
        self.fps     = config.getint("mmhealth", "fps")
        self.width   = config.getint("polarized", "width") 
        self.height  = config.getint("polarized", "height") 
        self.channels = config.getint("polarized", "channels") 
        self.compression = config.getint("polarized", "compression")
        self.calibrate_mode = config.getint("mmhealth", "calibration_mode") 
        self.calibrate_format = ".png"
        self.format = ".tiff"

        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        self.num_cameras = self.cam_list.GetSize()

        if self.num_cameras == 0:
            self.cam_list.Clear()
            self.system.ReleaseInstance()
            print('Not enough cameras!')

        for i, self.cam in enumerate(self.cam_list):
            nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
            node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
            if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
                self.device_serial_number = node_device_serial_number.GetValue()

            if (self.device_serial_number == "19224369"):
                self.cam_polar = self.cam
                del self.cam
            elif (self.device_serial_number == "21290846"):
                del self.cam

        self.cam_polar.Init()
        self.nodemap = self.cam_polar.GetNodeMap()
        self.nodemap_tldevice = self.cam_polar.GetTLDeviceNodeMap()

        # set fps
        node_acquisition_frame_rate_control_enable = PySpin.CBooleanPtr(self.nodemap.GetNode("AcquisitionFrameRateEnable"))
        if not PySpin.IsAvailable(node_acquisition_frame_rate_control_enable) or not PySpin.IsWritable(node_acquisition_frame_rate_control_enable):
            print("Unable to turn on Acquisition Frame Rate Control Enable (bool retrieval). Aborting...")
            return False
        node_acquisition_frame_rate_control_enable.SetValue(True)
        if self.cam_polar.AcquisitionFrameRate.GetAccessMode() != PySpin.RW:
            print ("Unable to set Frame Rate. Aborting...")
            return False
        self.cam_polar.AcquisitionFrameRate.SetValue(self.fps) # frame rate + 1

        node_acquisition_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        # self.fps = PySpin.CFloatPtr(self.nodemap.GetNode('AcquisitionFrameRate'))
        # self.fps = self.fps.GetValue()
        # self.fps = int(self.fps)

        # set width
        if self.cam_polar.Width.GetAccessMode() == PySpin.RW and self.cam_polar.Width.GetInc() != 0 and self.cam_polar.Width.GetMax != 0:
            self.cam_polar.Width.SetValue(self.width)
            # print("Width set to %i..." % self.cam_polar.Width.GetValue() )
        else:
            print("Width not available...")
            result = False

        # set height
        if self.cam_polar.Height.GetAccessMode() == PySpin.RW and self.cam_polar.Height.GetInc() != 0 and self.cam_polar.Height.GetMax != 0:
            self.cam_polar.Height.SetValue(self.height)
            # print("Height set to %i..." % self.cam_polar.Height.GetValue() )
        else:
            print("Height not available...")
            result = False

    def __del__(self) -> None:
        self.release_sensor()
        print("Released {} resources.".format(self.sensor_type))

    def acquire(self, acquisition_time : int) -> bool:
        self.cam_polar.BeginAcquisition()
        if (self.calibrate_mode == 1):
            run = True
            while( run == True):
                # self.cam_polar.BeginAcquisition()
                image_result = self.cam_polar.GetNextImage(1000)
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d...' % image_result.GetImageStatus())
                else:
                    im_arr = image_result.GetNDArray()
                    frame = cv2.resize(im_arr, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
                    cv2.imshow('Input', frame)

                    key = cv2.waitKey(1)
                    if key == ord('s'):
                        start_num = 1
                        while(os.path.exists(self.filepath + "_" + str(start_num) + self.calibrate_format)):
                            start_num += 1
                        imageio.imwrite(self.filepath + "_" + str(start_num) + self.calibrate_format, im_arr)
                    elif key == ord('q'):
                        run = False
                        cv2.destroyAllWindows()
                        break

                    # c = cv2.waitKey(1)
                    # if c == 27:
                    #     break
                    # elif cv2.waitKey(1) & 0xFF == ord('s'):
                    #     start_num = 1
                    #     while(os.path.exists(self.calibrate_filepath + str(start_num) + ".png")):
                    #         start_num += 1
                    #     imageio.imwrite(self.calibrate_filepath + str(start_num) + ".png", im_arr)
                    # # elif cv2.waitKey(1) & 0xFF == ord('q'):
                    # #     run = False
                    # #     break
                    image_result.Release()
            self.cam_polar.EndAcquisition()

        else:
            NUM_FRAMES = self.fps*acquisition_time  # number of images to capture
            frames = np.empty((NUM_FRAMES, self.height, self.width), np.dtype('uint8'))

            # self.cam_polar.BeginAcquisition()
            for i in range(NUM_FRAMES):
                image_result = self.cam_polar.GetNextImage(1000)
                self.record_timestamp()
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d...' % image_result.GetImageStatus())
                else:
                    img = image_result.GetNDArray()
                    frames[i] = img
                    image_result.Release()

            self.cam_polar.EndAcquisition()
            imageio.mimwrite(self.filepath + self.format, frames, bigtiff=True)
            self.save_timestamps()
            self.time_stamps = []
            
    def release_sensor(self) -> bool:
        self.cam_polar.DeInit()
        del self.cam_polar
        self.cam_list.Clear()
        self.system.ReleaseInstance()


    def print_stats(self):
        print("_____________ Polarized Camera Specifications _____________")
        print("FPS = {} f/s".format(self.fps))
        print("Resolution = {} x {}".format(self.height, self.width))
        print("Comression - ", self.compression)

# #To test code, run this file.
if __name__ == '__main__':
    polarized_cam = Polarized_Sensor(filename="polarized_1")
    polarized_cam.acquire(acquisition_time=5)
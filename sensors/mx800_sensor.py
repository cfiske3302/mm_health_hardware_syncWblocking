# mx800 sensor

import pyautogui
import time
import os
import keyboard
import sys

from config import *
from sensor import Sensor

class MX800_Sensor(Sensor):

    def __init__(self, filename : str, foldername : str = "data"):
        super().__init__(filename=filename, foldername=foldername)

        self.sensor_type = "mx800"

        #set parameters for video recorder
        self.long_pause = 1
        self.short_pause = 0.1
        self.abs_path  = os.path.join(config.get("mmhealth", "abs_path"), r"mx800\VSCaptureMP-master\VSCaptureMP\VSCaptureMP\bin\Debug" )

        #initialize capture
        os.startfile(os.path.join(self.abs_path, "VSCaptureMP.exe"))
        # # COM Port
        # time.sleep(self.long_pause)
        # keyboard.write('COM7')
        # pyautogui.press('enter')
        # # BAUD Rate
        # time.sleep(self.short_pause)
        # keyboard.write('92600')
        # pyautogui.press('enter')
        # ...
        time.sleep(self.long_pause)
        keyboard.write('2')
        pyautogui.press('enter')
        # ...
        time.sleep(self.short_pause)
        keyboard.write('2')
        pyautogui.press('enter')
        # ...
        time.sleep(self.short_pause)
        keyboard.write('1')
        pyautogui.press('enter')
        # ...
        # time.sleep(self.short_pause)
        # keyboard.write('test_mx')
        # pyautogui.press('enter')
        # ...
        time.sleep(self.short_pause)
        keyboard.write('2')
        pyautogui.press('enter')
        # ...
        time.sleep(self.short_pause)
        keyboard.write('1')
        pyautogui.press('enter')
        # IP Address
        time.sleep(self.short_pause)
        keyboard.write('192.168.33.32')

    def __del__(self) -> None:
        self.release_sensor()
        print("Released {} resources.".format(self.sensor_type))
        
    def acquire(self, acquisition_time : int) -> bool:
        pyautogui.press('enter')

        # print('MX800 start')
        time.sleep(acquisition_time)
        self.release_sensor()


    def release_sensor(self) -> bool:
        #Release mx800
        pyautogui.press('escape')

    def print_stats(self):
        print("_____________ mx800 Specifications _____________")
        # print("FPS = {} f/s".format(self.fps))
        # print("Resolution = {} x {}".format(self.height, self.width))
        # print("Encoding: {}".format(self.fourcc))



#To test code, run this file.
if __name__ == '__main__':

    mic = MX800_Sensor(filename="test_run")
    mic.acquire(acquisition_time=10)

# RF Sensor

# rgb sensor

import numpy as np
import sys
import subprocess
from mmwave.dataloader import DCA1000
import time

from sensor import Sensor

class RF_Sensor(Sensor):

    def __init__(self, filename : str, foldername : str = "data", sensor_on = False):
        super().__init__(filename=filename, foldername=foldername)

        self.sensor_type = "RF"
        self.fps = 6.5 #These needs to be emperically determined.
        self.dca = DCA1000()
        
        #initialize capture through running windows executable that runs with mmwave_studio
        if(not sensor_on):
            subprocess.Popen(r'C:\ti\mmwave_studio_02_01_01_00\mmWaveStudio\RunTime\run_mmwavestudio.cmd',
                                cwd=r'C:\ti\mmwave_studio_02_01_01_00\mmWaveStudio\RunTime')
        #IMPORTANT, wait 120 seconds in all other processes, setup takes 55 seconds at least.

        #set parameters for RF
        #None to be done, this is accomplished by our LUA config file
        

    def __del__(self) -> None:
        self.release_sensor()
        print("Released {} resources.".format(self.sensor_type))
        # print(self.filepath)
        
    def acquire(self, acquisition_time : int) -> bool:
        num_frames = int(self.fps*acquisition_time)
        adc_data_list = []

        for i in range(num_frames):
            adc_data = self.dca.read().astype(np.int16)
            frame = self.dca.organize(adc_data, 128, 4, 384)
            adc_data_list.append(frame)
            self.record_timestamp()

        adc_data_reshaped = np.stack(adc_data_list)

        np.save(self.filepath, adc_data_reshaped)
        self.save_timestamps()
        self.time_stamps = []


    def release_sensor(self) -> bool:
        #Release RF
        #TODO either let it run forever, or kill process and DCA1000 
        pass

    def print_stats(self):
        print("_____________ RF Specifications _____________")
        print("TODO print Config File")

# #To test code, run this file.
if __name__ == '__main__':

    rf_s = RF_Sensor(filename="rf_output_1", sensor_on=True)
    time.sleep(5)
    rf_s.acquire(acquisition_time=15)
    rf_s.print_stats()